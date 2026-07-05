import pandas as pd
import time
import os
from datetime import datetime

import refinitiv.data as rd


def format_date(date_value):
    return pd.to_datetime(date_value).strftime("%Y%m%d")


def to_output_date(date_value):
    return pd.to_datetime(date_value).strftime("%Y-%m-%d")


def get_constituent_rics(index, date_value, max_retries=3, retry_delay=5):
    """
    Get constituent RICs
    """
    date_for_api = format_date(date_value)
    attempts = max_retries + 1  # first try + retries
    data = None

    for attempt in range(1, attempts + 1):
        try:

            if date_for_api < "20160601":
                # Use legacy index RIC format for dates before June 1, 2016
                adjusted_index = f"0#{index}({date_for_api})"
                data = rd.get_data(adjusted_index, ["TR.RIC"])
        
                break

            data = rd.get_data(index, ["TR.IndexConstituentRIC", "TR.IndexConstituentName"], parameters={"SDate": date_for_api})

            break
        except Exception as exc:
            if attempt == attempts:
                print(f"Skipping date {date_for_api} after {attempts} attempts for index {index}. Last error: {exc}")
                return []
            print(f"Attempt {attempt} failed for date {date_for_api} (index {index}). Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    if data is None or data.empty:
        return []

    if "Constituent RIC" not in data.columns:
        if "RIC" in data.columns:
            data = data.rename(columns={"RIC": "Constituent RIC"})
        else:
            print(f"No constituent RICs found for date {date_for_api} (index {index})")
            return []

    # Clean and drop na
    rics = (
        data["Constituent RIC"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    rics = [ric for ric in rics.unique().tolist() if ric]

    return rics


def get_company_names(rics, max_retries=3, retry_delay=5):
    """
    Get company names for a list of RICs.
    """
    # Remove empty/None values up front
    clean_rics = [ric for ric in rics if ric]
    if not clean_rics:
        return pd.DataFrame(columns=["RIC", "Company_Name"])

    attempts = max_retries + 1
    
    for attempt in range(1, attempts + 1):
        try:
            data = rd.get_data(clean_rics, ["TR.CommonName"])
            data = data.rename(columns={
                "Instrument": "RIC",
                "Company Common Name": "Company_Name"
            })
            return data
        except Exception as exc:
            if attempt == attempts:
                print(f"Failed to get company names after {attempts} attempts. Last error: {exc}")
                return pd.DataFrame(columns=["RIC", "Company_Name"])
            print(f"Attempt {attempt} to get company names failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    return pd.DataFrame(columns=["RIC", "Company_Name"])


def build_presence_matrix(index, start_date, end_date, frequency="D"):
    """
    Build a constituent presence matrix
    """
    date_range = pd.date_range(start=start_date, end=end_date, freq=frequency)

    if date_range.empty:
        print("No dates in the specified range.")
        return pd.DataFrame(columns=["Date"])

    daily_membership = []
    all_constituents = set()

    print(f"Building presence matrix for index: {index}")

    for single_date in date_range:
        rics = get_constituent_rics(index=index, date_value=single_date)
        members = set(rics)
        daily_membership.append((single_date, members))
        all_constituents.update(members)
        print(f"Processed date: {single_date.strftime('%Y-%m-%d')} -> {len(members)} constituents")

    sorted_companies = sorted(all_constituents)

    print(f"Total unique constituents found: {len(sorted_companies)}")

    presence_rows = []
    
    print("Constructing presence matrix...")
    for single_date, members in daily_membership:
        row = {"Date": to_output_date(single_date)}
        row.update({ric: (1 if ric in members else 0) for ric in sorted_companies})
        presence_rows.append(row)

    print("Presence matrix construction complete.")
    
    return pd.DataFrame(presence_rows, columns=["Date"] + sorted_companies)


def get_constituents(index, start_date, end_date, frequency="D", output_folder="data", output_filename=None):
    """
    Generate an Excel file with index constituents data.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")
    
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean index name for filename (remove special characters)
        clean_index = index.replace("#", "").replace(".", "_").strip("_")
        output_filename = f"constituents_{clean_index}_{timestamp}.xlsx"
    
    if not output_filename.endswith(".xlsx"):
        output_filename += ".xlsx"
    
    output_path = os.path.join(output_folder, output_filename)
    
    print("=" * 60)
    print(f"Getting constituents for index: {index}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Frequency: {frequency}")
    print("=" * 60)
    
    # Build presence matrix
    presence_matrix = build_presence_matrix(
        index=index,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency
    )
    
    # Get unique constituents (all columns except "Date")
    if len(presence_matrix.columns) > 1:
        unique_constituents = [
            ric for ric in presence_matrix.columns[1:]
            if isinstance(ric, str) and ric.strip()
        ]
    else:
        unique_constituents = []
    
    print(f"\nRetrieving company names for {len(unique_constituents)} constituents...")
    
    # Get company names
    if unique_constituents:
        constituents_df = get_company_names(unique_constituents)
    else:
        constituents_df = pd.DataFrame(columns=["RIC", "Company_Name"])
    
    # Write to Excel with two sheets
    print(f"\nWriting data to: {output_path}")
    
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        presence_matrix.to_excel(writer, sheet_name="Presence_Matrix", index=False)
        constituents_df.to_excel(writer, sheet_name="Constituents", index=False)
    
    print("=" * 60)
    print("Export complete!")
    print(f"  - Presence matrix: {len(presence_matrix)} dates x {len(unique_constituents)} constituents")
    print(f"  - Constituents list: {len(constituents_df)} entries")
    print(f"  - Output file: {output_path}")
    print("=" * 60)
    
    return output_path

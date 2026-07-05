import pandas as pd
import os

def load_constituents_from_file(file_path, sheet_name="Constituents"):
    # Determine file type and read accordingly
    if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        return load_from_excel(file_path, sheet_name)
    elif file_path.endswith(".csv"):
        return load_from_csv(file_path)
    else:
        raise ValueError(f"Unsupported file format. Expected .xlsx, .xls, or .csv: {file_path}")


def load_from_excel(file_path, sheet_name):
    try:
        if sheet_name == "Constituents":
            # Read from the Constituents sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            if "RIC" not in df.columns:
                raise ValueError(f"Column RIC not found in sheet '{sheet_name}'. Available columns: {list(df.columns)}")
            
            rics = df["RIC"].dropna().astype(str).unique().tolist()
            
        elif sheet_name == "Presence_Matrix":
            # Read from the Presence Matrix sheet and extract RICs from column headers
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            if "Date" not in df.columns:
                raise ValueError(f"Column Date not found in sheet '{sheet_name}'. This may not be a valid presence matrix.")
            
            # All columns except "Date" are RICs
            rics = [col for col in df.columns if col != "Date"]
            
        else:
            # Try to read from the specified sheet and look for RIC column
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            if "RIC" in df.columns:
                rics = df["RIC"].dropna().astype(str).unique().tolist()
            else:
                # Assume first column contains RICs
                first_col = df.columns[0]
                print(f"Warning: RIC column not found. Using first column '{first_col}' as RIC source.")
                rics = df[first_col].dropna().astype(str).unique().tolist()
        
        print(f"Loaded {len(rics)} RICs from '{file_path}' (sheet: {sheet_name})")
        return rics
        
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")


def load_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        
        if "RIC" in df.columns:
            rics = df["RIC"].dropna().astype(str).unique().tolist()
        elif "Instrument" in df.columns:
            rics = df["Instrument"].dropna().astype(str).unique().tolist()
        else:
            # Assumes first column contains RICs
            first_col = df.columns[0]
            print(f"Warning: RIC column not found. Using first column '{first_col}' as RIC source.")
            rics = df[first_col].dropna().astype(str).unique().tolist()
        
        print(f"Loaded {len(rics)} RICs from '{file_path}'")
        return rics
        
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")


def load_constituents_with_names(file_path, sheet_name="Constituents"):
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        required_columns = ["RIC", "Company_Name"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}. Available columns: {list(df.columns)}")
        
        print(f"Loaded {len(df)} constituents with names from '{file_path}'")
        return df[required_columns]
        
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {e}")

import pandas as pd
import time
import os
from datetime import datetime

import refinitiv.data as rd


# Supported frequency formats for rd.get_history()
SUPPORTED_FREQUENCIES = [
    "daily", "1d", "1D",
    "7D", "7d", "weekly", "1W",
    "monthly", "1M",
    "quarterly", "3M", "6M",
    "yearly", "12M", "1Y"
]

def get_history(
    stocks,
    fields,
    start_date,
    end_date,
    frequency="daily",
    output_folder="data",
    output_prefix="history",
    saving_interval=0.05,
    max_retries=3,
    retry_delay=5,
    sleep_time=1
):
    """
    Get historical time series data for a list of stocks using rd.get_history().
    """
    # Validate inputs
    if not stocks:
        raise ValueError("Stock list cannot be empty")
    if not fields:
        raise ValueError("Fields list cannot be empty")
    
    if frequency not in SUPPORTED_FREQUENCIES:
        raise ValueError(f"Frequency '{frequency}' not supported. Choose from: {SUPPORTED_FREQUENCIES}")
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")
    
    # File paths for temporary and final outputs
    temp_data_path = os.path.join(output_folder, f"TEMP_{output_prefix}_data.csv")
    temp_remaining_path = os.path.join(output_folder, f"TEMP_{output_prefix}_remaining.csv")
    temp_failed_path = os.path.join(output_folder, f"TEMP_{output_prefix}_failed.csv")
    
    # Initialize or resume from previous run
    all_data = pd.DataFrame()
    remaining_stocks = list(stocks)
    failed_stocks = []
    
    # Check for existing temporary files to resume
    if os.path.exists(temp_data_path) and os.path.exists(temp_remaining_path):
        print("Found existing temporary files. Resuming from previous run...")
        try:
            all_data = pd.read_csv(temp_data_path)
            remaining_stocks = pd.read_csv(temp_remaining_path)["RIC"].tolist()

            if os.path.exists(temp_failed_path):
                failed_stocks = pd.read_csv(temp_failed_path)["RIC"].tolist()

            print(f"Resumed with {len(remaining_stocks)} remaining stocks and {len(failed_stocks)} failed stocks")
        except Exception as e:
            print(f"Error loading temporary files: {e}. Starting fresh...")
            all_data = pd.DataFrame()
            remaining_stocks = list(stocks)
            failed_stocks = []
    
    # Calculate saving checkpoints
    total_stocks = len(stocks)
    stocks_to_process = len(remaining_stocks)
    processed_count = total_stocks - stocks_to_process
    last_save_percentage = processed_count / total_stocks if total_stocks > 0 else 0
    
    print("=" * 60)
    print(f"Starting history retrieval (rd.get_history)")
    print(f"Total stocks: {total_stocks}")
    print(f"Remaining to process: {stocks_to_process}")
    print(f"Fields: {fields}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Frequency: {frequency}")
    print(f"Saving interval: {saving_interval * 100:.1f}%")
    print("=" * 60)
    
    start_time = time.time()
    
    # Process each stock
    stocks_processed_this_session = 0
    
    for i, stock in enumerate(remaining_stocks.copy()):
        current_processed = processed_count + stocks_processed_this_session + 1
        current_percentage = current_processed / total_stocks
        
        print(f"[{current_processed}/{total_stocks}] ({current_percentage * 100:.1f}%) Processing: {stock}")
        
        # Get data with retries
        stock_data = get_history_with_retry(
            stock=stock,
            fields=fields,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        if stock_data is not None and not stock_data.empty:
            all_data = pd.concat([all_data, stock_data], ignore_index=True)
        else:
            failed_stocks.append(stock)
            print(f"  -> Added {stock} to failed stocks list")
        
        # Remove from remaining stocks
        remaining_stocks.remove(stock)
        stocks_processed_this_session += 1
        
        if current_percentage >= last_save_percentage + saving_interval:
            save_progress(
                all_data=all_data,
                remaining_stocks=remaining_stocks,
                failed_stocks=failed_stocks,
                temp_data_path=temp_data_path,
                temp_remaining_path=temp_remaining_path,
                temp_failed_path=temp_failed_path
            )
            
            # Print progress update
            elapsed_time = time.time() - start_time
            print_progress(
                processed=current_processed,
                total=total_stocks,
                elapsed_time=elapsed_time,
                failed_count=len(failed_stocks)
            )
            
            last_save_percentage = current_percentage
        
        # Sleep between requests
        if remaining_stocks:
            time.sleep(sleep_time)
    
    # save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_data_path = os.path.join(output_folder, f"{output_prefix}_data_{timestamp}.csv")
    final_failed_path = os.path.join(output_folder, f"{output_prefix}_failed_{timestamp}.csv")
    
    if not all_data.empty:
        all_data.to_csv(final_data_path, index=False)
        print(f"Final data saved to: {final_data_path}")
    
    if failed_stocks:
        failed_df = pd.DataFrame({"RIC": failed_stocks})
        failed_df.to_csv(final_failed_path, index=False)
        print(f"Failed stocks saved to: {final_failed_path}")
    
    # Clean up temporary files
    cleanup_temp_files([temp_data_path, temp_remaining_path, temp_failed_path])
    
    # Print final summary
    elapsed_time = time.time() - start_time
    print("=" * 60)
    print("History loading complete!")
    print(f"  - Total stocks processed: {total_stocks}")
    print(f"  - Successful: {total_stocks - len(failed_stocks)}")
    print(f"  - Failed: {len(failed_stocks)}")
    print(f"  - Total time: {elapsed_time / 60:.2f} minutes")
    print(f"  - Output file: {final_data_path}")
    print("=" * 60)
    
    return all_data


def get_history_with_retry(stock, fields, start_date, end_date, frequency, max_retries=3, retry_delay=5):
    """
    Get historical data for a single stock
    """
    
    attempts = max_retries + 1
    
    for attempt in range(1, attempts + 1):
        try:
            data = rd.get_history(
                stock,
                fields=fields,
                interval=frequency,
                start=start_date,
                end=end_date
            )
            
            if data is not None and not data.empty:
                
                data = data.reset_index()
                
                # Add stock column
                data["Stock"] = stock
            
                if "Date" not in data.columns:
                    if data.columns[0] == "index":
                        data = data.rename(columns={"index": "Date"})
                    elif len(data.columns) > 0:
                        first_col = data.columns[0]
                        if pd.api.types.is_datetime64_any_dtype(data[first_col]):
                            data = data.rename(columns={first_col: "Date"})
                
                # Convert datetime to date only (remove time component)
                if "Date" in data.columns:
                    data["Date"] = pd.to_datetime(data["Date"]).dt.date
                
                return data
            else:
                print(f"  Attempt {attempt}: Empty response for {stock}")
                
        except Exception as exc:
            print(f"  Attempt {attempt}: Error for {stock} - {exc}")
            
            if attempt < attempts:
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    print(f"  Failed to get history for {stock} after {attempts} attempts")
    return None


def save_progress(all_data, remaining_stocks, failed_stocks, temp_data_path, temp_remaining_path, temp_failed_path):
    """Save current progress to temporary files."""
    try:
        if not all_data.empty:
            all_data.to_csv(temp_data_path, index=False)
        
        if remaining_stocks:
            pd.DataFrame({"RIC": remaining_stocks}).to_csv(temp_remaining_path, index=False)
        
        if failed_stocks:
            pd.DataFrame({"RIC": failed_stocks}).to_csv(temp_failed_path, index=False)
        
        print("  [Progress saved]")
        
    except Exception as e:
        print(f"  Warning: Failed to save progress: {e}")


def print_progress(processed, total, elapsed_time, failed_count):
    """Print progress update"""

    percentage = (processed / total) * 100
    avg_time_per_stock = elapsed_time / processed if processed > 0 else 0
    remaining = total - processed
    estimated_remaining_time = avg_time_per_stock * remaining
    
    print("\n" + "=" * 40)
    print(f"Progress Update: {processed}/{total} ({percentage:.1f}%)")
    print(f"  - Elapsed time: {elapsed_time / 60:.2f} minutes")
    print(f"  - Estimated remaining: {estimated_remaining_time / 60:.2f} minutes")
    print(f"  - Failed stocks so far: {failed_count}")
    print("=" * 40 + "\n")


def cleanup_temp_files(file_paths):
    """Remove temporary files."""

    for path in file_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Warning: Could not remove temp file {path}: {e}")

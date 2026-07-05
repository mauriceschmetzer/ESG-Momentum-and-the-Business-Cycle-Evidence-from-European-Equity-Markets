import os
import sys
import pandas as pd
import datetime

import refinitiv.data as rd

from helper_functions import to_target_currency, load_constituents_from_file, get_history, get_data

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
local_path = r"C:\Users\mauri\Desktop\Uni\1_MSc_Data_Science_in_Business_and_Economics\5_Semester\Master Thesis\workspace\Refinitiv-Data-Download"

# Path to the constituents file
constituents_file = os.path.join(local_path, "data", "output", "constituents_STOXX.xlsx")

output_folder = os.path.join(local_path, "data", "output")
output_xlsx = os.path.join(output_folder, "constituent_timeseries")

os.chdir(local_path)
sys.path.append(local_path)

class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# Set up logging
logpath = os.path.join(output_folder, f"log_{datetime}.log")
logfile = open(logpath, "w", encoding="utf-8")

sys.stdout = Tee(sys.stdout, logfile)
sys.stderr = Tee(sys.stderr, logfile)

# Open Refinitiv session
rd.open_session()

# ---------------------------------------------------------------------------
# Load constituents list
# ---------------------------------------------------------------------------
stocks = load_constituents_from_file(constituents_file)
index = ".STOXX"

start_date = "2010-01-01"
end_date = "2026-02-28"

# ---------------------------------------------------------------------------
# Refinitiv Parameters
# ---------------------------------------------------------------------------
daily_history_fields = [
    "TR.PriceClose",
    "TR.CompanyMarketCap", 
    "TR.CompanyMarketCap(ShType=FFL)", 
    "TR.CompanyMarketCap(ShType=OUT)", 
    "TR.SharesOutstanding",
    "TR.PriceToBVPerShare"
]

daily_history_index_fields = [
    "TR.PriceClose",
    "TR.PriceClose.Currency",
]

yearly_history_fields = [
    "TR.TRESGScore",
]

dividend_data_fields = [
    "TR.DivExDate",
    "TR.DivExDate.periodenddate",
    "TR.DivAdjustedGross",
    "TR.DivAdjustedGross.periodenddate", 
    "TR.DivType",
    "TR.DivPaymentType",
    "TR.DivCurr",
    "TR.DivIsRescinded",
    "TR.DivRescindDate",
]

financial_data_fields = [
    "TR.OperatingIncome", 
    "TR.OperatingIncome.periodenddate",
    "TR.TotalEquity",
    "TR.TotalEquity.periodenddate", 
    "TR.TotalAssetsReported",
    "TR.TotalAssetsReported.periodenddate",
    "TR.ISOriginalAnnouncementDate",
]

category_data_fields = [
    "TR.GICSSector",
    "TR.ICBSector",
    "TR.ICBIndustry",
    "TR.PriceClose.Currency",
    "TR.ExchangeCountry",
    "TR.CoRPrimaryCountry",
    "TR.HeadquartersCountry"
]

target_currency = "EUR"

daily_history_fields = [to_target_currency(field, target_currency) for field in daily_history_fields]
daily_history_index_fields = [to_target_currency(field, target_currency) for field in daily_history_index_fields]
dividend_data_fields = [to_target_currency(field, target_currency) for field in dividend_data_fields]
financial_data_fields = [to_target_currency(field, target_currency) for field in financial_data_fields]
yearly_history_fields = [to_target_currency(field, target_currency) for field in yearly_history_fields]

if daily_history_fields:
    daily_ts = get_history(
        stocks = stocks,
        fields = daily_history_fields,
        start_date = start_date,
        end_date = end_date,
        frequency = "daily",
        output_folder = output_folder,
        output_prefix = "daily_stock_history_file",
        saving_interval = 0.01,
        max_retries = 3,
        sleep_time = 2,
    )

if daily_history_index_fields:
    daily_index_ts = get_history(
        stocks = [index],
        fields = daily_history_index_fields,
        start_date = start_date,
        end_date = end_date,
        frequency = "daily",
        output_folder = output_folder,
        output_prefix = "daily_index_history_file",
        saving_interval = 0.01,
        max_retries = 3,
        sleep_time = 2,
    )

if yearly_history_fields:
    yearly_d = get_history(
        stocks = stocks,
        fields = yearly_history_fields,
        start_date = start_date,
        end_date = end_date,
        frequency = "yearly",
        output_folder = output_folder,
        output_prefix = "annual_history_file",
        saving_interval = 0.01,
        max_retries = 3,
        sleep_time = 1,
    )

if dividend_data_fields:
    dividend_d = get_data(
        stocks = stocks,
        fields = dividend_data_fields,
        start_date = start_date,
        end_date = end_date,
        output_folder = output_folder,
        output_prefix = "dividend_data_file",
        saving_interval = 0.01,
        max_retries = 3,
        sleep_time = 1,
    )

if financial_data_fields:
    quarterly_d = get_data(
        stocks = stocks,
        fields = financial_data_fields,
        start_date = start_date,
        end_date = end_date,
        parameters = {"Period": "FQ0",
                      "ReportingState": "Orig"},
        frequency = "FQ",
        output_folder = output_folder,
        output_prefix = "quarterly_financial_data_file",
        saving_interval = 0.01,
        max_retries = 3,
        sleep_time = 1,
    )

    annual_d = get_data(
        stocks = stocks,
        fields = financial_data_fields,
        start_date = start_date,
        end_date = end_date,
        parameters = {"Period": "FY0",
                      "ReportingState": "Orig"},
        frequency = "FY", 
        output_folder = output_folder,
        output_prefix = "annual_financial_data_file",
        saving_interval = 0.01,
        max_retries = 3,
        sleep_time = 1,
    )

if category_data_fields:
    once_d = get_data(
        stocks = stocks,
        fields = category_data_fields,
        start_date = start_date,
        end_date = end_date,
        output_folder = output_folder,
        output_prefix = "once_data_file",
        saving_interval = 0.01,
        max_retries = 3,
        sleep_time = 1,
    )

# Close Refinitiv session
rd.close_session()

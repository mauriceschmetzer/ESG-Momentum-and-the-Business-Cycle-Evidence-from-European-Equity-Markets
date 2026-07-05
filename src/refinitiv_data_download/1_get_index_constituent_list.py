import os
import sys

import refinitiv.data as rd

from helper_functions import get_constituents

local_path = r"C:\Users\mauri\Desktop\Uni\1_MSc_Data_Science_in_Business_and_Economics\5_Semester\Master Thesis\workspace\Refinitiv-Data-Download"

os.chdir(local_path)
sys.path.append(local_path)

rd.open_session()

index_code = ".STOXX" 
start_date = "2016-06-01"
end_date = "2026-02-28"
frequency = "D"
output_folder = os.path.join(local_path, "data", "output")
output_filename = f"constituents_{index_code.replace('#', '').replace('.', '_')}.xlsx"

output_path = get_constituents(
    index=index_code,
    start_date=start_date,
    end_date=end_date,
    frequency=frequency,
    output_folder=output_folder,
    output_filename=output_filename,
)

print(f"Constituents saved to: {output_path}")

rd.close_session()
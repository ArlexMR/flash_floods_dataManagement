import pandas as pd 
import xarray as xarray
import numpy as numpy
import matplotlib.pyplot as plt
from pathlib import Path
import datetime
csvs_folder = Path("../USGSdata")
output_parquet_folder = Path("C:/Users/arlex/OneDrive - Virginia Tech/Projects/FlashFloodPrediction/DB/usgs_parquet")
output_report = Path("C:/Users/arlex/OneDrive - Virginia Tech/Projects/FlashFloodPrediction/DB/")
unit_conv_factor = (0.3048)**3

report = {}
files_list = list(csvs_folder.iterdir())
for i, filepath in enumerate(files_list):
    if (i+1) % 5 == 0:
        print(f"processing file: {i+1} / {len(files_list)}")
    if not filepath.name.startswith("USGS-"):
        print(f"unknown file name convention {filepath.name}")
        continue
    station_code = filepath.name.removeprefix("USGS-").removesuffix(".csv")
    df = pd.read_csv(filepath, index_col="time", usecols=["time", "value"], parse_dates=True)
    df = df.loc[~df.index.duplicated()]
    df = df.resample("h").asfreq() * unit_conv_factor
    df.rename(columns = {"value":"Qcms"}, inplace=True)
    df.to_parquet(output_parquet_folder / f"{filepath.name.removesuffix(".csv")}.parquet",
                   compression="zstd", 
                   compression_level=1
                   )
    tot_nan = df.isna().sum().values
    report[station_code]={
        "start_date":   df.index[0],
        "end_date":     df.index[-1],
        "tot_nan":      tot_nan,
        "frac_nan":     tot_nan / len(df)
    }

pd.DataFrame(report).T.to_csv(output_report / f"report_csv_to_parquet_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.csv")

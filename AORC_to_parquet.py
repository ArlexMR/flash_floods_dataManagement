import pandas as pd 
from pathlib import Path
import shutil 
import os

aorc_path = Path("../data/AORC_data")
aorc_output_parquet = Path("../data/AORC_parquet")
aorc_files = list(aorc_path.iterdir())
variables = set([file.name[:-9] for file in aorc_files])

years = range(1980,2021)

print("---------------Grouping years------------------")

if (aorc_output_parquet/"temp").exists():
    shutil.rmtree(aorc_output_parquet/"temp")
os.mkdir(aorc_output_parquet /"temp" )

for variable in list(variables):
    
    print(f"processing {variable}")
    df_list = []
    for year in years:
        print(f"\tyear {year}")
        filename = f"{variable}_{year}.csv"
        df = pd.read_csv(aorc_path / filename, dtype = {"region": str}, index_col="region").T
        df.index = pd.to_datetime(df.index)
        df = df[~df.index.duplicated()]
        df = df.resample("h").asfreq()
        df_list.append(df)
    df_all = pd.concat(df_list).resample("h").asfreq()
    for site_code in df_all:
        df_all[[site_code]].to_parquet(aorc_output_parquet /"temp"/ f"{variable}_{site_code}.parquet",
                       compression="zstd", 
                       compression_level=1
                       )

print("---------------Grouping catchments------------------")
site_codes = set([path.name.split("_")[2].removesuffix(".parquet") for path in (aorc_output_parquet / "temp").iterdir()])

for site_code in site_codes:
    site_files = (aorc_output_parquet / "temp").glob(f"*_{site_code}.parquet")
    site_dfs = []
    for file in site_files:
        varname = "_".join(file.name.split("_")[:2])
        df = pd.read_parquet(file)
        site_dfs.append(df.rename(columns = {site_code:varname}))
    pd.concat(site_dfs,axis = 1).to_parquet(aorc_output_parquet / f"AORC_{site_code}.parquet",
                       compression="zstd", 
                       compression_level=1
                       )
print("---------------Removing temporary files------------------")

shutil.rmtree(aorc_output_parquet/"temp")

print("---------------Completed------------------")

print(f"results saved to: {aorc_output_parquet}")
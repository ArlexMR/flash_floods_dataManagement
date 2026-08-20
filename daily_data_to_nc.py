
import numpy as np
import xarray as xr
from pathlib import Path
import json
from dataretrieval import waterdata
from datetime import date

def get_mapping_from_numeric_code_to_actual_str_code(site_no):
    site_ids_all = [f"USGS-{site_n}" for site_n in site_no] + [f"USGS-0{site_n}" for site_n in site_no]

    monit_locs = waterdata.get_monitoring_locations(monitoring_location_id=site_ids_all)
    correct_codes = monit_locs[0].monitoring_location_number.values

    site_number_to_str = {}
    for site_as_n in site_no:
        if str(site_as_n) in correct_codes:
            site_number_to_str[site_as_n] = str(site_as_n)
        elif f"0{site_as_n}" in correct_codes:
             site_number_to_str[site_as_n] = f"0{site_as_n}"
        else:
            print(f"Error with site: {site_as_n}")
    return site_number_to_str


farshid_daymet_file = Path("C:/Users/arlex/OneDrive - Virginia Tech/Projects/FlashFloodPrediction/DB/FarshidsData/f2003_daymet_20240826.npy")
farshid_names_file = Path("C:/Users/arlex/OneDrive - Virginia Tech/Projects/FlashFloodPrediction/DB/FarshidsData/f2003_daymet_20240826_name.json")
output_path = "C:/Users/arlex/OneDrive - Virginia Tech/Projects/FlashFloodPrediction/DB/daily_all.nc"
arr = np.load(farshid_daymet_file)
with open(farshid_names_file) as f:
    names = json.load(f)
len(names)
new_names = []
for name in names:
    new_names.append(name.replace("/","-"))
    data_vars = {
    key:(("catchment", "date"), arr[:,:,i]) for key, i in zip(new_names,range(len(new_names)))
}

site_no = arr[:,0,new_names.index("site_no")].astype(int)

site_number_to_str = get_mapping_from_numeric_code_to_actual_str_code(site_no)

site_codes = [site_number_to_str[site_as_n] for site_as_n in arr[:,0,new_names.index("site_no")].astype(int)]


dates = [np.datetime64(f"{str(datenum)[:4]}-{str(datenum)[4:6]}-{str(datenum)[6:8]}")
            for datenum in arr[0,:,new_names.index("datetime")].astype(int)
]


ds = xr.Dataset(
    data_vars=data_vars,
    coords={
        "catchment": site_codes,
        "date": dates
    }
)
ds.to_netcdf(output_path)

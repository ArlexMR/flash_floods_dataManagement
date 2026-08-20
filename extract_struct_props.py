import pandas as pd 
import numpy as numpy
from pathlib import Path

import numpy as np
import json

aorc_path = Path("../data/AORC_parquet/")

sites = [file.name.removeprefix("AORC_").removesuffix(".parquet") for file in aorc_path.iterdir()]
sites = {int(site): site for site in sites}

struct_props_path = Path("../data/FarshidsData/attr2003_mswep_03122024.npy")
struct_prop_names_path = Path("../data/FarshidsData/attr2003_mswep_03122024_name.json")
with open(struct_prop_names_path) as f:
    struct_names = json.load(f)
site_no_idx = struct_names.index("site_no_int")

struct_prop_arr =  np.load(struct_props_path)
struct_props_df = pd.DataFrame(struct_prop_arr, columns=struct_names, index = struct_prop_arr[:,site_no_idx])

filt_df = struct_props_df.loc[struct_props_df.index.isin(sites.keys())]
filt_df.index = [sites[site_no] for site_no in filt_df.index]
filt_df.index = filt_df.index.rename("site_code")
filt_df.to_csv("../data/Struct_props.csv")

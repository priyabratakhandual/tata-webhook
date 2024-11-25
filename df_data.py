import pandas as pd
import numpy as np
import os

index_dir = "all_data"
path = os.getcwd()+"/"+index_dir

# Load the DataFrame from the pickle file
df_service_basic = pd.read_pickle(f"{path}/service_df.pkl")
df_sales_basic = pd.read_pickle(f"{path}/sales_df.pkl")


def get_basic_submodule(module,submodule=None, issuecategory=None):
    if module == "Service":
        df = df_service_basic
        cat_list = list(df["Sub-Module"].unique())
    elif module == "Sales":
        df = df_sales_basic
        cat_list = list(df["Sub-Module"].unique())
    
    if submodule:
        cat_list = list(df[df["Sub-Module"] == submodule]["Issue Category"].unique())
        if issuecategory:
            filtered_df = df[(df["Sub-Module"] == submodule) & (df["Issue Category"] == issuecategory)]
            result_dict = filtered_df[["Issue","Resolution/Escalation"]].to_dict(orient="records")
            return result_dict

    return cat_list
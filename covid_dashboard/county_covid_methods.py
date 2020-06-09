from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np

FACTOR = 1e-9
def format_time(val,time_format: str = "%d-%m-%Y"):
#     print(val)
    val *= FACTOR
    current_date = datetime.fromtimestamp(val)
    return current_date.strftime(time_format)


def generate_title(title_text: str):
    st.title(title_text)

def load_data(data_file: str,nrows: int=None,date_col="date"):
    assert data_file.endswith(".csv"), "Data file has to be in the csv format"
    
    data = pd.read_csv(data_file,nrows=nrows).drop('fips',axis=1)
    data = data.assign(temp_col=pd.to_datetime(data[date_col])).drop(date_col,axis=1).rename({"temp_col":date_col},axis=1)
    data = data.assign(month_year=data.apply(lambda row: _get_month_year(row[date_col]),axis=1))
        
    return data

def _get_month_year(date):
    date = date.to_pydatetime()
    return date.strftime("%b-%Y")
    

def combine_with_states(data: pd.DataFrame,states_df: pd.DataFrame,state_name_col: str="name",data_state_col: str="state"):
    states_df = states_df.rename({"state":"code"},axis=1)
    temp_df = data.merge(states_df,left_on=data_state_col,right_on=state_name_col).drop(state_name_col,axis=1)
    return temp_df

@st.cache
def load_covid_data(data_file: str,state_file: str,nrows: int=None,date_col="date",
                    state_name_col: str="name",data_state_col: str="state"):
    covid_df = load_data(data_file,nrows,date_col)
    covid_df = combine_with_states(covid_df,pd.read_csv(state_file),state_name_col,data_state_col)
    return covid_df

def agg_data_by_cols(data: pd.DataFrame,agg_cols: list,val_cols: list=None,ops: str="sum"):
    assert agg_cols is not None and len(agg_cols) > 0, "There should be at least one column to aggregate by"
    assert ops != "count", "Count operation is not supported by this function"
    val_cols = val_cols if val_cols is not None else [col for col in data.columns if col not in agg_cols]
    val_col_ops = {col:ops for col in val_cols}
    temp_df = data.groupby(agg_cols).agg(val_col_ops).reset_index()
    return temp_df

def _get_attrs_for_county_month(group_df,val_cols: list,agg_cols: list = ["month_year","county"],date_col: str="date",):
    selected_cols = agg_cols+val_cols
    group_df = group_df.sort_values(date_col,ascending=False).head(1)[selected_cols]
    return group_df

@st.cache
def extract_attrs_by_month(data: pd.DataFrame,month_year_col: str="month_year",date_col: str="date",
                           county_col="county",val_cols: list=None):
    agg_cols = [month_year_col,county_col]
    selected_cols = agg_cols+val_cols+[date_col]
    group_df = data[selected_cols].groupby(agg_cols)
    groups = [_get_attrs_for_county_month(group,val_cols) for label,group in group_df]
    temp_df = pd.concat(groups)
    selected_cols = [month_year_col]+val_cols
    val_op_map = {val:"sum" for val in val_cols}
    temp_df = temp_df[selected_cols].groupby(month_year_col).agg(val_op_map).reset_index()
    return temp_df

@st.cache
def count_data_by_cols(data: pd.DataFrame,agg_cols: list,post_count_col: str="count"):
    assert agg_cols is not None and len(agg_cols) > 0, "There should be at least one column to count by"
    temp_df = data[agg_cols]
    temp_df = temp_df.groupby(agg_cols).count().reset_index()
    temp_df.columns = agg_cols+[post_count_col]
    return temp_df

def get_cases_by_date_range(data: pd.DataFrame,start_date,end_date,date_col="date",val_cols: list=["cases","deaths"],
                            melt_flag: bool = True,melt_var: str="category",melt_val: str="count"):
    temp_df = filter_data_by_date_range(data,start_date,end_date,date_col="date")
    agg_dict = {val: "sum" for val in val_cols}
    temp_df = temp_df.groupby(date_col).agg(agg_dict).reset_index()
    temp_df.columns = [date_col]+val_cols
    temp_df = temp_df.melt(id_vars=[date_col],value_vars=val_cols,var_name=melt_var, 
                           value_name=melt_val) if melt_flag else temp_df
#     print(temp_df.head())
    return temp_df

def filter_data_by_date_range(data: pd.DataFrame,start_date,end_date,date_col="date"):
#     print(type(start_date))
    org_cols = data.columns
    temp_df = data.assign(is_valid=data[date_col].apply(lambda val: (val >= start_date) & (val <= end_date)))
    temp_df = temp_df.loc[temp_df["is_valid"] == True,org_cols]
    return temp_df
    
def prepare_end_date(data: pd.Series, start_date):
#     print(start_date)
    return np.sort(data[data > start_date].unique())
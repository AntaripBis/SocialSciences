from datetime import datetime
import time
from math import ceil

import streamlit as st
import pandas as pd
import numpy as np

from county_covid_methods import (load_data,combine_with_states,agg_data_by_cols,count_data_by_cols,
                                 extract_attrs_by_month,get_cases_by_date_range,prepare_end_date,
                                 format_time,FACTOR)


def generate_date_range(data: pd.DataFrame,factor=1e-9,date_col: str="date"):
    init_date_range = np.sort(data[date_col].unique())
    start_date = st.sidebar.selectbox("Select Start Date: ",init_date_range.tolist(),
                                      format_func=format_time)
    start_date = datetime.fromtimestamp(start_date*factor)
    end_date_range = prepare_end_date(data[date_col],start_date)
    end_date = st.sidebar.selectbox("Select End Date: ",end_date_range.tolist(),
                                    format_func=format_time)
    end_date = datetime.fromtimestamp(end_date*factor)
    
    return start_date, end_date

def generate_date_select(date_arr: np.array,factor=1e-9,label: str="Select Date"):
    date_arr = np.sort(date_arr)
    start_date = st.sidebar.selectbox(label,date_arr.tolist(),
                                      format_func=format_time)
    start_date = datetime.fromtimestamp(start_date*factor)
    return start_date


def generate_multiselectbox(data: pd.DataFrame,label: str,select_col: str = None,selected_cols: list=None):
    assert selected_cols is not None or select_col is not None, "One of selected_cols or the column whose values will be used should be non-NULL"
    content = data[select_col].unique().tolist() if selected_cols is None else selected_cols
    selected_content = st.sidebar.multiselect(label,content,default=content)
    return selected_content

def generate_selectbox(data: pd.DataFrame, select_col: str,label: str):
    content = data[select_col].unique().tolist()
#     content = ["All"]+content if add_all else content
    selected_content = st.sidebar.selectbox(label,content)
    return selected_content

def generate_slider(data: pd.DataFrame,label: str):
    max_value = data.shape[0]
    min_value = 1
    init_selected_val = (min_value, min(3000,max_value))
    selected_content = st.sidebar.slider(label,min_value,max_value,init_selected_val)
    return selected_content
    
@st.cache(suppress_st_warning=True)   
def get_selected_month_data(data: pd.DataFrame,month_col: str,selected_month):
    temp_df = data.loc[data[month_col] == selected_month,:]
    return temp_df


def build_month_case_div(data: pd.DataFrame,month_col: str="month_year",date_col: str="date",
                         month_label: str="Select Month: ",date_label: str = "Select Date: "):
    selected_month = generate_selectbox(data,month_col,month_label)
    temp_df = get_selected_month_data(data,month_col,selected_month)
    selected_date = generate_date_select(temp_df[date_col].unique(),label=date_label)
    return selected_date,temp_df
    
    
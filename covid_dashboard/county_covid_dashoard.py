from datetime import datetime, timedelta
import time

import streamlit as st
import pandas as pd
import numpy as np

from county_covid_methods import (load_covid_data,combine_with_states,agg_data_by_cols,count_data_by_cols,
                                   extract_attrs_by_month,get_cases_by_date_range,prepare_end_date,
                                   format_time,FACTOR,filter_data_by_date_range)

from create_visuals import create_area_chart,create_bar_chart,create_line_chart,create_us_map_with_cases_deaths

from dashboard_methods import (generate_date_range,generate_multiselectbox,generate_selectbox,
                               generate_slider,build_month_case_div)

DATA_FILE = "../../data/us_counties.csv"
STATE_FILE = "../../data/states.csv"
STATE_NAME_COL = "name"
DATA_STATE_COL = "state"

data_load_state = st.text('Loading data...')
data = load_covid_data(DATA_FILE,STATE_FILE,state_name_col=STATE_NAME_COL,data_state_col=DATA_STATE_COL)
# data = combine_with_states(data,pd.read_csv(STATE_FILE),state_name_col=STATE_NAME_COL,data_state_col=DATA_STATE_COL)
data_load_state.text('%d rows of data loaded' % (data.shape[0]))

is_header1_active =st.sidebar.checkbox('Display Raw data')
if is_header1_active:
    min_value, max_value = generate_slider(data,"Select Index Range: ")
    init_data_cols = list(data.columns)
    selected_cols = generate_multiselectbox(data,"Select Columns: ",selected_cols=init_data_cols)
    show_df = data 
    if max_value+1-min_value == data.shape[0] or len(selected_cols) != len(init_data_cols):
        show_df = data.loc[min_value-1:max_value,selected_cols]
    data_load_state.text('%d rows of data selected !!' % (max_value+1-min_value))
    st.dataframe(show_df,height=280,width=720)

#Groupby date
is_header2_active =st.sidebar.checkbox('Cases in States by Date')
if is_header2_active:
    data_load_state.text("")
    selected_date,selected_month_df = build_month_case_div(data,month_label="Select Month: ",date_label="Select Date: ")
#     st.write(selected_date)
    start_time = selected_date -timedelta(hours=6)
    end_time = selected_date+timedelta(hours=6)
    selected_month_df = selected_month_df[["state","date","latitude","longitude","cases","deaths"]]
    selected_date_df = filter_data_by_date_range(selected_month_df,start_time,end_time,date_col="date")
#     st.dataframe(selected_date_df)
    selected_date_df = selected_date_df.groupby(["state","latitude","longitude"]).agg({"cases":"sum","deaths":"sum"}).reset_index()
    chart_title="Cases and Deaths across US on %s" % (selected_date.strftime("%d-%m-%Y"))
    us_map_chart = create_us_map_with_cases_deaths(selected_date_df,chart_title=chart_title,lat_col="latitude",
                                                  lon_col="longitude",case_col="cases",death_col="deaths",width=640,height=360)
    st.altair_chart(us_map_chart,use_container_width=True)
    
    

#Create filter by date
is_header3_active = st.sidebar.checkbox('Trend by State')

if is_header3_active:
    data_load_state.text("")
    selected_state = generate_selectbox(data,"state","Select state: ")
    
    state_df = data.loc[data["state"] == selected_state,:]
    
    start_date, end_date = generate_date_range(state_df,FACTOR)
    
    date_filter_df = get_cases_by_date_range(state_df,start_date,end_date,date_col="date",melt_var="category",melt_val="count")
    # st.dataframe(date_filter_df.head(100))
    state_cases_chart = create_line_chart(date_filter_df,"date","count",x_type="date",x_label="Date of Year",
                                           y_label="# Cases/Deaths",chart_title="Covid Cases/Deaths over Time",
                                           width=640,height=360,category="category",x_format="%d-%m-%y")

    st.altair_chart(state_cases_chart,use_container_width=True)
    

is_header4_active = st.sidebar.checkbox('Trend by County')

if is_header4_active:
    data_load_state.text("")
    selected_county = generate_selectbox(data,"county","Select county: ")
    
    county_df = data.loc[data["county"] == selected_county,:] #if selected_state != "All" else data
    
    start_date, end_date = generate_date_range(county_df,FACTOR)
    
    county_filter_df = get_cases_by_date_range(county_df,start_date,end_date,date_col="date",melt_var="category",melt_val="count")
    # st.dataframe(date_filter_df.head(100))
    county_cases_chart = create_line_chart(county_filter_df,"date","count",x_type="date",x_label="Date of Year",
                                           y_label="# Cases/Deaths",chart_title="Covid Cases/Deaths over Time",
                                           width=640,height=360,category="category",x_format="%d-%m-%y")

    st.altair_chart(county_cases_chart,use_container_width=True)
    

    



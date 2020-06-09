from datetime import datetime

import altair as alt
import pandas as pd
from vega_datasets import data
import streamlit as st

TYPE_SYM_MAP = {"catg": "N","date":"T","ord":"O","num":"Q"}

def create_area_chart(data: pd.DataFrame,x_col:str,y_col: str,x_type: str="catg",chart_title: str="",
                     height: int=360, width: int = 640,x_label: str=None,y_label: str=None,x_format: str="%b-%Y"):
    
    assert x_type in TYPE_SYM_MAP, "X type has to be one of catg, ord, num or date"
    x_label = x_label if x_label is not None else x_col
    x_val = "%s:%s" % (x_col,TYPE_SYM_MAP[x_type])
#     print(x_val)
    x_alt = alt.X(x_val,title=x_label,axis=alt.Axis(format=x_format)) if x_type == "date" else alt.X(x_val,title=x_label)
    if x_type == "date":
        data = data.assign(temp_col=data[x_col].apply(lambda unit: datetime.strptime(unit,x_format)))
        data = data.drop(x_col,axis=1).rename({"temp_col":x_col},axis=1)
    
    y_label = y_label if y_label is not None else y_col
    y_alt = alt.Y("%s:Q" % (y_col),title=y_label)
#     print("%s:Q" % (y_col))
    data = data.drop_duplicates()
#     print(data)
    
    chart = alt.Chart(data).mark_area(opacity=0.7).encode(x=x_alt,y=y_alt)
    chart = chart.properties(height=height,width=width,title=chart_title)
#     print(type(chart))
    return chart

def create_bar_chart(data: pd.DataFrame,x_col:str,y_col: str,x_type: str="catg",chart_title: str="",
                     height: int=360, width: int = 640,x_label: str=None,y_label: str=None,x_format: str="%b-%Y",
                    bar_size: int=30):
    
    assert x_type in TYPE_SYM_MAP, "X type has to be one of catg, ord, num or date"
    x_label = x_label if x_label is not None else x_col
    x_val = "%s:%s" % (x_col,TYPE_SYM_MAP[x_type])
#     print(x_val)
    x_alt = alt.X(x_val,title=x_label,axis=alt.Axis(format=x_format)) if x_type == "date" else alt.X(x_val,title=x_label)
    if x_type == "date":
        data = data.assign(temp_col=data[x_col].apply(lambda unit: datetime.strptime(unit,x_format)))
        data = data.drop(x_col,axis=1).rename({"temp_col":x_col},axis=1)
    
    y_label = y_label if y_label is not None else y_col
    y_alt = alt.Y("%s:Q" % (y_col),title=y_label)
#     print("%s:Q" % (y_col))
    data = data.drop_duplicates()
#     print(data.head())
    
    chart = alt.Chart(data).mark_bar(size=bar_size).encode(x=x_alt,y=y_alt)
    chart = chart.properties(height=height,width=width,title=chart_title)
#     print(type(chart))
    return chart

def create_line_chart(data: pd.DataFrame,x_col:str,y_col: str,x_type: str="catg",chart_title: str="",
                     height: int=360, width: int = 640,x_label: str=None,y_label: str=None,x_format: str="%b-%Y",
                     category: str=None):
    
    assert x_type in TYPE_SYM_MAP, "X type has to be one of catg, ord, num or date"
    x_label = x_label if x_label is not None else x_col
    x_val = "%s:%s" % (x_col,TYPE_SYM_MAP[x_type])
#     print(x_val)
    x_alt = alt.X(x_val,title=x_label,axis=alt.Axis(format=x_format)) if x_type == "date" else alt.X(x_val,title=x_label)
    if x_type == "date" and str(data[x_col].dtype) == "object" :
        data = data.assign(temp_col=data[x_col].apply(lambda unit: datetime.strptime(unit,x_format)))
        data = data.drop(x_col,axis=1).rename({"temp_col":x_col},axis=1)
    
    y_label = y_label if y_label is not None else y_col
    y_alt = alt.Y("%s:Q" % (y_col),title=y_label)
#     print("Came till here !")
    data = data.drop_duplicates()
#     print("Came till here 2 !")
    color = alt.value('green') if category is None else category
    
    chart = alt.Chart(data).mark_line().encode(x=x_alt,y=y_alt,color=color)
    chart = chart.properties(height=height,width=width,title=chart_title)
#     print("Came till here 3!")
    return chart

@st.cache
def create_us_background(background_type="states",height: int=360, width: int=640):
    
    entities = alt.topo_feature(data.us_10m.url, feature=background_type)
    
    background = alt.Chart(entities).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        width=width,
        height=height
    ).project('albersUsa')
    
    return background

def create_us_map_with_cases_deaths(chart_df: pd.DataFrame,case_col: str="cases",death_col: str="deaths",state_col: str="state",
                                    lat_col: str="lat",lon_col: str="lon",height: int=360, width: int = 640, 
                                    chart_title: str = "Map of US"):
    
    background = create_us_background("states",height=height,width=width)
    
    points = alt.Chart(chart_df).mark_circle().encode(
        longitude="%s:Q" % (lon_col),
        latitude="%s:Q" % (lat_col),
        size=alt.Size('%s:Q' % (case_col)),
        color=alt.value('steelblue'),
        tooltip=[state_col,case_col,death_col]
    ).properties(title=chart_title)
    
    return background+points
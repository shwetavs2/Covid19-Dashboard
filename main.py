import pandas as pd
df1=pd.read_csv('covid_deaths_usafacts.csv')
b=pd.read_csv('covid_county_population_usafacts.csv')
df2=pd.read_csv('covid_confirmed_usafacts.csv')
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
st.set_page_config(layout="wide")
st.subheader("Covid 19 Dashboard")
st.markdown('<style>#vg-tooltip-element{z-index: 1000051}</style>',unsafe_allow_html=True)

col1,col2 = st.columns([2,2])
col3,col4=st.columns([2,2])

test=df2
filtered_cases = test.drop(columns = ['countyFIPS', 
                       'StateFIPS','County Name',
                       '2020-01-22','2020-01-23', '2020-01-24'])                       
before_sum = filtered_cases.iloc[:,1:]
calculated_sum=before_sum.sum(axis=0).to_frame()
calculated_diff = calculated_sum.diff().T
final = calculated_diff.drop(columns = ['2020-01-25'])
@st.cache
def weekly_data(increasing_cases):
    start_day = False
    count = 0
    count_1 = []
    for a,b in increasing_cases.items():
        start_dt = pd.to_datetime(a, format='%Y/%m/%d', 
                                    exact = False)
        first_weekday = start_dt.day_name()
        if not start_day and first_weekday != 'Sunday':
            continue
        start_day = True
        count += b
        if first_weekday == 'Saturday':
            count_1.append(count)
            count = 0
    return count_1
final_week = pd.DataFrame(weekly_data(final)).rename(columns={0:"Covid Cases"})
final_plot=pd.DataFrame(data=final_week)

final_plot.index.name='week'
final_plot.reset_index(inplace=True)

line_chart = alt.Chart(final_plot).mark_line(interpolate='basis').encode(
    alt.X('week', title='Week',axis=alt.Axis(labelOverlap=True)),
    alt.Y('Covid Cases', title='covid cases in usa'),
    tooltip=['week','Covid Cases'],
    color='cases:N'
).properties(
    title='Covid 19 new cases'
)
col1.altair_chart(line_chart,use_container_width=True)
col1.write('Weekly increasing cases of covid in usa')
#####################Question 2########################
df_death=df1

death_cases = df_death.drop(columns = ['countyFIPS', 
                       'StateFIPS','County Name',
                       '2020-01-22','2020-01-23', '2020-01-24'])

new_deaths = death_cases.iloc[:,1:]
death_cases_total=new_deaths.sum(axis=0).to_frame()
new_cases = death_cases_total.diff().T
final_death = new_cases.drop(columns =['2020-01-25'])

final_week_death = pd.DataFrame(weekly_data(final_death)).rename(columns={0:"Covid Cases"})
final_plot_death=pd.DataFrame(data=final_week_death)

final_plot_death.index.name='week'
final_plot_death.reset_index(inplace=True)

line_chart_1 = alt.Chart(final_plot_death).mark_line(interpolate='basis').encode(
    alt.X('week', title='Week',axis=alt.Axis(labelOverlap=True)),
    alt.Y('Covid Cases', title='covid deaths in usa'),
    tooltip=['week','Covid Cases'],
    color='cases:N'
).properties(
    title='Covid 19 new deaths'
)

col2.altair_chart(line_chart_1,use_container_width=True)
col2.write('Weekly deaths of covid patients in usa')

##################Question 3###############################
merged_inner = pd.merge(left=df2, right=b, how='inner', left_on=['countyFIPS','State'], right_on=['countyFIPS','State'])
merged_inner['countyFIPS']=merged_inner['countyFIPS'].apply(lambda x:'{0:0>5}'.format(x))
merged_inner.drop(columns=['County Name_y'],inplace=True)
merged_inner.drop(columns='StateFIPS' ,inplace=True)
merged_inner['countyandstate']=merged_inner['County Name_x']+merged_inner['State']
new=merged_inner.loc[:,'2020-01-22':'2022-02-07'].diff(axis=1)
new.drop(columns=['2020-01-22'],inplace=True)
new_cases_weekly_total =  pd.DataFrame(weekly_data(new))

final_map1=new_cases_weekly_total.T
population=merged_inner['population']
cfips=merged_inner['countyFIPS']
location=merged_inner['countyandstate']
final_map1=final_map1.join(population)
final_map1=final_map1.join(cfips)
final_map1=final_map1.join(location)

final_map1['covid_per_100k']=((final_map1['2022-01-30']/final_map1['population'])*100000).to_frame().round()
final_map1['covid_per_100k'].fillna(0,inplace=True)
pd.options.mode.use_inf_as_na = True

from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
import plotly.express as px
fig = px.choropleth(final_map1, 
    geojson=counties, 
    locations='countyFIPS', 
    color=final_map1['covid_per_100k'],
    color_continuous_scale="Viridis",
    range_color=(0, 2000),
    scope="usa",
    hover_data=['countyandstate'],
    width=650,
    height=700
)
col3.plotly_chart(fig)

###################Question 4#####################################
deaths_merged = pd.merge(left=df1, right=b, how='inner', left_on=['countyFIPS','State'], right_on=['countyFIPS','State'])
deaths_merged['countyFIPS']=deaths_merged['countyFIPS'].apply(lambda x:'{0:0>5}'.format(x))
deaths_merged.drop(columns=['County Name_y'],inplace=True)
deaths_merged.drop(columns='StateFIPS' ,inplace=True)
deaths_merged['countyandstate']=merged_inner['County Name_x']+merged_inner['State']

new_df=deaths_merged.loc[:,'2020-01-22':'2022-02-07'].diff(axis=1)
new_df.drop(columns=['2020-01-22'],inplace=True)

new_cases_weekly_deaths =  pd.DataFrame(weekly_data(new_df))

final_df=new_cases_weekly_deaths.T
population=deaths_merged['population']
cfips=deaths_merged['countyFIPS']
location=merged_inner['countyandstate']

final_df=final_df.join(population)
final_df=final_df.join(cfips)
final_df=final_df.join(location)
final_df['covid_per_100k']=((final_df['2022-01-30']/final_df['population'])*100000).to_frame().round()
final_df['covid_per_100k'].fillna(0,inplace=True)
pd.options.mode.use_inf_as_na = True

fig1 = px.choropleth(final_df, 
    geojson=counties, 
    locations='countyFIPS', 
    color=final_df['covid_per_100k'],
    color_continuous_scale="Viridis",
    range_color=(0, 30),
    scope="usa",
    hover_data=['countyandstate'],
    width=650,
    height=700
)
col4.plotly_chart(fig1)
############################Question 5#################################
population=merged_inner['population']
after_div=(final_map1.loc[:,'2020-01-26':'2022-01-30'].div(final_map1.population,axis=0)*100000).round().fillna(0)
n=after_div
n.rename_axis('weeks')
n=n.join(cfips)
case_rate =n.melt(id_vars=['countyFIPS'],value_vars=n.columns[:-1])
st.slider("week")

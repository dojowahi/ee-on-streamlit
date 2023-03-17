import streamlit as st
import ee
import geemap.foliumap as geemap
import json
from datetime import datetime, timedelta, date
import geemap.colormaps as cm
import pandas as pd

from helpers import ee_authentication, landComposite, buildings
    

# Define the Streamlit app
def app():
    
    # _______________________ LAYOUT CONFIGURATION __________________________

    st.set_page_config(page_title='Dynamic World Change', layout="wide")

# shape the map
    st.markdown(
        f"""
    <style>
    .appview-container .main .block-container{{

        padding-top: {3}rem;
        padding-right: {2}rem;
        padding-left: {0}rem;
        padding-bottom: {0}rem;
    }}


    </style>
    """,
        unsafe_allow_html=True,
    )
    
    # Set the app title
    st.title("Dynamic Change with Building Footprint")
    
    ## ___________________ SIDEBAR PARAMETERS ___________________________


    st.sidebar.info('### ***US States and Counties***')

    with st.sidebar:
        # Add a dropdown to select a state
        state_county_data = pd.read_csv("https://raw.githubusercontent.com/dojowahi/ee-on-streamlit/main/data/usa_state_county.csv",encoding = 'unicode_escape')
        states = sorted(state_county_data["state"].unique())
        selected_state = st.selectbox("Select a state", states)

        # Use the state code to filter the counties dataframe
        counties = sorted(state_county_data.loc[state_county_data["state"] == selected_state]["county"].unique())

        # Add a dropdown to select a county
        selected_county = st.selectbox("Select a county", counties)

        # Add a dropdown to select intial year
        years = ['2017','2018','2019','2020','2021','2022']
        selected_year = st.selectbox('Select a year', years)
        
        geoid = state_county_data.loc[(state_county_data["county"] == selected_county) & (state_county_data["state"] == selected_state), "fips"].iloc[0]
        
        button = st.button('Update')

        
    # __________________ MAP INSTANCE _________________
    if button:
    
        with st.spinner("Processing satellite imagery for county "+ selected_county + " ..."):
        
            #st.write(selected_county,selected_year)
            ee_authentication()
            gee_counties = ee.FeatureCollection('TIGER/2016/Counties')
            gee_states = ee.FeatureCollection('TIGER/2016/States');

            diff_viz = {"min": -1, "max": 1, "palette": ["green", "white", "red"]}
            filtered_state = gee_states.filter(ee.Filter.eq('NAME', selected_state))
            statefp = filtered_state.first().get('STATEFP')
            #filtered_county = gee_counties.filter(ee.Filter.And(ee.Filter.eq('NAMELSAD', selected_county),ee.Filter.eq('GEOID', geoid)))
            filtered_county = gee_counties.filter(ee.Filter.And(ee.Filter.eq('NAMELSAD', selected_county),ee.Filter.eq('STATEFP', statefp)))

            geometry = filtered_county.geometry()
            dwCompositeStart,builtStart = landComposite(geometry,selected_year)
            dwCompositeEnd,builtEnd = landComposite(geometry,"2022")
            #diff = dwCompositeEnd.subtract(dwCompositeStart)

            newBuilt = builtEnd.subtract(builtStart)

            Map = geemap.Map(basemap='HYBRID')
            dwVisParams = {"min": 0,"max": 8,"palette": ['#419BDF', '#397D49', '#88B053', '#7A87C6','#E49635', '#DFC35A', '#C4281B', '#A59B8F', '#B39FE1']}
            #Map.add_legend(title="Dynamic World Land Cover",builtin_legend="Dynamic_World",)
            
            try:
                Map.addLayer(dwCompositeStart, dwVisParams, "Dynamic_"+selected_year,shown=False)
                Map.addLayer(dwCompositeEnd, dwVisParams, "Dynamic_2022",shown=False)
            except Exception as e:
                st.write(e)
                error_msg = f"No imagery available for county {selected_county} in {selected_state} with code {statefp} for the {selected_year} and GeoID {geoid}"
                st.write(error_msg)

            buildingsFc = buildings(selected_state)

            #color = st.color_picker('Select a color', '#FF5500')

            style = {'fillColor': '00000000', 'color': '#BB40DA'}


            left = geemap.ee_tile_layer(buildingsFc.style(**style), {}, 'Buildings')
            right =  geemap.ee_tile_layer(newBuilt, diff_viz, "Dynamic Built Change")
            #Map.centerObject(buildingsFc.first(),zoom=16)

            Map.centerObject(dwCompositeStart,zoom=12)
            Map.split_map(left, right)
            
                
            Map.to_streamlit(height=900,responsive=True) 

app()

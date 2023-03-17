# Helper functions
import ee
import geemap
import streamlit as st
import json
from datetime import datetime, timedelta, date

# Secrets
def ee_authentication():
    json_data = st.secrets["json_data"]
    service_account = st.secrets["service_account"]

    # Preparing values
    json_object = json.loads(json_data, strict=False)
    json_object = json.dumps(json_object)

    # Authorising the app
    credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
    ee.Initialize(credentials)

def buildings(state):
    try:
        fc = ee.FeatureCollection(f'projects/sat-io/open-datasets/MSBuildings/US/{state}')
    except:
        st.error('No data available for the selected state.')
        
    return fc
    
    
def landComposite(geometry,year):

        #st.write(geometry.getInfo())
        startDate = year+"-01-01"
        endDate = year+"-12-31"
        #st.write(startDate,endDate)

        dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1').filterDate(startDate, endDate).filterBounds(geometry)
        #Create a Mode Composite.
        classification = dw.select('label')
        dwComposite = classification.reduce(ee.Reducer.mode()).clip(geometry)
        builtArea = dwComposite.eq(6)
        return dwComposite, builtArea

def getNLCD(year):

    # Import the NLCD collection.
    dataset = ee.ImageCollection("USGS/NLCD_RELEASES/2019_REL/NLCD")

    # Filter the collection by year.
    nlcd = dataset.filter(ee.Filter.eq("system:index", year)).first()

    # Select the land cover band.
    landcover = nlcd.select("landcover")
    return landcover

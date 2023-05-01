# Helper functions
import ee
import geemap
import streamlit as st
import json
import datetime
import pandas as pd
from google.cloud import bigquery
from PIL import Image
from google.cloud import storage
import io
import time
import logging

# Secrets
def ee_authentication():
    # Using secrets from Streamlit
    # json_data = st.secrets["json_data"]
    # service_account = st.secrets["service_account"]
    
    # Using secrets fro Github Actions
    json_data = os.environ["GCP_SA_KEY_JSON"]
    service_account = os.environ["GCP_SA_ACCOUNT"]

    # Preparing values
    json_object = json.loads(json_data, strict=False)
    json_object = json.dumps(json_object)

    # Authorising the app
    credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
    ee.Initialize(credentials)

def buildings(state):
    try:
        state = state.replace(" ", "")
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

def get_wildfire(state,county,start_date,end_date):

    admin0 = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0")
    admin2 = ee.FeatureCollection("FAO/GAUL/2015/level2")
    admin1 = ee.FeatureCollection("FAO/GAUL/2015/level1")

    sel_state = admin2.filter(ee.Filter.eq('ADM1_NAME', state))
    sel_county = sel_state.filter(ee.Filter.eq('ADM2_NAME', county))
    county_area = sel_county.geometry()
    dataset = ee.ImageCollection('FIRMS').filterDate(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")).mosaic().clip(county_area)

    fires = dataset.select('T21')
    blaze = fires.gte(300)
    blaze = blaze.updateMask(blaze.lt(300))

    vectors = blaze.addBands(blaze).reduceToVectors(**{
      'geometry': county_area,
      'scale': 100,
      # crs: current.projection(),
      'labelProperty': 'blaze',
      'geometryType': 'polygon',
      'eightConnected': True,
      'reducer': ee.Reducer.mean(),
      'maxPixels': 1e10
    })

    fire_vector = vectors.geometry()

    return blaze, county_area, fire_vector


def get_building(wildfire_vector,county):
    try:
        # Connect to BigQuery
        keys = ['type', 'coordinates']
        bq = {x:wildfire_vector[x] for x in keys}
        geo_txt = json.dumps(bq)
        now = datetime.datetime.now()
        current_date_time = now.strftime('%Y%m%d%H%M%S')
        col_nm = county+'_'+str(current_date_time)

        client = bigquery.Client()
        load_query = f'''DECLARE wildfire GEOGRAPHY;
                         DECLARE query_nm STRING;

             SET wildfire = (select ST_GEOGFROMGEOJSON('{geo_txt}', make_valid => TRUE));
             SET query_nm = ('{col_nm}');

            INSERT into gee.wildfire_building WITH s1 as
     (SELECT query_nm as tran_id, geometry as bld_vector FROM `bigquery-public-data.geo_openstreetmap.planet_layers`,UNNEST(all_tags) AS tags
       WHERE  tags.key = "building"
       AND ST_Dimension(geometry) = 2
       AND ST_DWITHIN(geometry, wildfire, 1))
       select * from s1;'''


        list_building = f''' select ST_ASGEOJSON(ST_UNION_AGG(bld_vector)) AS multipolygon_building, count(*) as cnt from gee.wildfire_building WHERE tran_id='{col_nm}'; '''

        logging.info("Query:",load_query)

        bq_df = client.query(load_query)
        time.sleep(5)
        building_poly = client.query(list_building).to_dataframe()

        return building_poly

    except:
        st.error("Error retrieving data")

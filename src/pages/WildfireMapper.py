import streamlit as st
import ee
import geemap.foliumap as geemap
import json
import datetime
from helpers import ee_authentication, get_wildfire, get_building


# Define the Streamlit app
def app():
    ee_authentication()

    # Set the app title
    st.title("Mapping wildfires and buildings")

    # ___________________ SIDEBAR PARAMETERS ___________________________

    st.sidebar.info("### ***US States***")

    with st.sidebar:
        # Add a dropdown to select a state
        # admin0 = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0")
        admin2 = ee.FeatureCollection("FAO/GAUL/2015/level2")
        admin1 = ee.FeatureCollection("FAO/GAUL/2015/level1")
        stateNames = (
            admin1.filter(ee.Filter.eq("ADM0_NAME", "United States of America"))
            .aggregate_array("ADM1_NAME")
            .sort()
        )

        selected_state = st.selectbox("Select a state", stateNames.getInfo())

        # Use the state code to filter the counties dataframe
        countyNames = (
            admin2.filter(ee.Filter.eq("ADM1_NAME", selected_state))
            .aggregate_array("ADM2_NAME")
            .sort()
        )

        # Add a dropdown to select a county
        selected_county = st.selectbox("Select a county", countyNames.getInfo())

        # Add a dropdown to select intial year
        default_start_dt = datetime.datetime(2022, 8, 1).date()
        start_date = st.sidebar.date_input("Start date:", value=default_start_dt)
        default_end_dt = default_start_dt + datetime.timedelta(days=100)

        end_date = st.sidebar.date_input("End date:", value=default_end_dt)

        # Ensure end date is not more than 4 months after start date
        if (end_date - start_date).days > 120:
            st.sidebar.error("End date must be within 4 months of start date.")
            st.stop()

        submitted = st.button("Submit")

    # __________________ MAP INSTANCE _________________
    if submitted:
        with st.spinner(
            "Processing satellite imagery for state " + selected_state + " ..."
        ):
            # container = st.empty()

            # st.write(selected_county,selected_year)
            fire, county_geo, fire_vector = get_wildfire(
                selected_state, selected_county, start_date, end_date
            )
            firesVis = {
                "min": 325.0,
                "max": 400.0,
                "palette": ["yellow", "orange", "red"],
            }

            if fire:
                # Create a map object

                Map = geemap.Map(basemap="ROADMAP")

                try:
                    Map.addLayer(county_geo, {}, "County")
                    Map.addLayer(fire, firesVis, "Wildfire")

                    building_list = get_building(fire_vector.getInfo(), selected_county)

                    if building_list is None or building_list.loc[0][0] is None:
                        building_geojson = None
                        st.write("No buildings affected by wildfires")
                    else:
                        building_geojson = json.loads(building_list.loc[0][0])
                        eeBuilding = ee.Geometry(building_geojson)
                        st.write(
                            "The number of buildings affected by this wildfire:"
                            + str(building_list.loc[0][1])
                        )
                        Map.addLayer(eeBuilding, {}, "Buildings")

                except Exception as e:
                    st.write(e)

                Map.centerObject(county_geo, zoom=11)

                Map.to_streamlit(height=900, responsive=True)

            else:
                error_msg = f"No wildfires detected for county {selected_county} in {selected_state} for the chosen time period"
                st.write(error_msg)


app()

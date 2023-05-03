import streamlit as st
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Web App URL: <https://ee-github-apps-rhvexdce7q-uc.a.run.app>
GitHub Repository: <https://github.com/dojowahi/ee-on-streamlit>
"""

st.sidebar.title("About")
st.sidebar.info(markdown)


# Customize page title
st.title("Streamlit on Cloud Run for Earth Engine apps")

st.markdown(
    """
    This multipage app template demonstrates various interactive web apps created using [streamlit](https://streamlit.io) and Google Earth Engine.
    The app is deployed on Google Cloud Run, and uses Github Actions for CI/CD
    """
)

st.header("Instructions")

markdown = """
1. You can find my [GitHub repository](https://github.com/dojowahi)
2. Connect with me [LinkedIn](https://www.linkedin.com/in/ankur-wahi-7a20b92/)
"""

st.markdown(markdown)

m = leafmap.Map(minimap_control=True)
m.add_basemap("OpenTopoMap")
m.to_streamlit(height=500)

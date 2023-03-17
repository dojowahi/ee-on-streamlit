# Earth Engine App with Streamlit
The goal of this demo is to build an Earth Engine App and deploy it using Streamlit.
The code uses Python APIs and uses the geemap python library developed by ![Qiusheng Wu] (https://geemap.org/)
The code can be replicated and executed on your local machine or any other hyperscaler, but I will be showing how to run it on GCP

## Requirements

* Ensure you have a GCP project with APIs for artifact registry, cloud build and cloud run
* To make GEE work with Streamlit you will need to do GEE authentication with a key. The instruction about how to do it is already written in this clear and excellent tutorial by 
![Mykola Kozyr] (https://medium.com/@mykolakozyr/using-google-earth-engine-in-a-streamlit-app-62c729793007)


## Setting up the demo
**1)** In Cloud Shell or other environment where you have the gcloud SDK installed, execute the following commands:
```console
gcloud components update 
cd $HOME

https://github.com/dojowahi/ee-on-streamlit.git
cd ~/ee-on-streamlit


gcloud builds submit --tag gcr.io/${GOOGLE_CLOUD_PROJECT}/streamlit-ee:2.0.0 .

gcloud run deploy streamlit-ee --image gcr.io/${GOOGLE_CLOUD_PROJECT}/streamlit-ee:2.0.0 --region us-central1 
```

# Use an official GDAL image as the base image
FROM osgeo/gdal:ubuntu-small-latest

# install pip
RUN apt-get update && apt-get -y install python3-pip --fix-missing

# Set the working directory in the container
WORKDIR /app


# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the app's dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app to the container
COPY . .

CMD streamlit run --server.port 8080 --server.enableCORS false app.py

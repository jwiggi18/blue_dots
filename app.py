import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import folium
from streamlit_folium import st_folium
import random
import json
import sqlite3

# Set page config to wide
st.set_page_config(layout="wide")

# Connect to/create SQLite database
conn = sqlite3.connect('locations.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        state TEXT,
        latitude REAL,
        longitude REAL
    )
''')
conn.commit()

# Custom CSS to increase font size for all text input fields
font_css = """
<style>
div[class*="stRadio"] label p {
    font-size: 20px;
}

div[class*=stTextInput] label p {
    font-size: 20px;
}
</style>
"""
    

# Initialize geolocator
geolocator = Nominatim(user_agent="blue_dots_oklahoma (jodiewiggins18@gmail.com)")

# Function to get lat, lon from city, state
def get_lat_lon(city, state):
    try:
        location = geolocator.geocode(f"{city}, {state}, 'USA'")
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        st.error(f"Geocoding service error: {e}")
        return None, None

# Function to add jitter to latitude and longitude
def add_jitter(lat, lon, jitter_amount=0.05):
    lat_jitter = random.uniform(-jitter_amount, jitter_amount)
    lon_jitter = random.uniform(-jitter_amount, jitter_amount)
    lat += lat_jitter
    lon += lon_jitter
    st.write(f"Jitter applied: lat + {lat_jitter}, lon + {lon_jitter}")  # Debugging line to show jitter amount
    return lat, lon

# add location to the database
def add_location_to_db(city, state, lat, lon):
    c.execute('INSERT INTO locations (city, state, latitude, longitude) VALUES (?, ?, ?, ?)', 
              (city, state, lat, lon))
    conn.commit()
    
# pull locations from the database
def fetch_all_locations():
    c.execute('SELECT city, state, latitude, longitude FROM locations')
    return pd.DataFrame(c.fetchall(), columns=['City', 'State', 'Latitude', 'Longitude'])

# Make title blue
st.markdown(
    """
    <style>
    .title {
        background-color: #0073e6;
        padding: 10px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    </style>
    <div class="title">
        <h1>Blue Dots in Oklahoma!!</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.write(font_css, unsafe_allow_html=True)

# Radio buttons to select input method
input_method = st.radio("Select input method (if you don't live in a city you can enter your latitude and longitude)", ("City and State", "Latitude and Longitude"))

if input_method == "City and State":
    # Input boxes for city and state
    city = st.text_input("Enter the City")
    # Dropdown menu for state
    states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
              'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
              'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
              'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
              'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
              'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
              'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
              'Wisconsin', 'Wyoming']
    oklahoma_index = states.index("Oklahoma")
    state = st.selectbox("Select the State", options=states, index=oklahoma_index)

    # Button to add location
    if st.button("Add Location"):
        if city and state:
            lat, lon = get_lat_lon(city, state)
            if lat and lon:
                #add jitter
                lat, lon = add_jitter(lat, lon)
                #add location to db
                add_location_to_db(city, state, lat, lon)
                st.success(f"Location added: {city}, {state} ({lat}, {lon})")
            else:
                st.error("Could not find the location. Please check the city and state.")
        else:
            st.error("Please enter both city and state.")

elif input_method == "Latitude and Longitude":
    # Input boxes for latitude and longitude
    latitude = st.text_input("Enter Latitude")
    longitude = st.text_input("Enter Longitude")

    # Button to add location
    if st.button("Add Location"):
        if latitude and longitude:
            try:
                lat = float(latitude)
                lon = float(longitude)
                # Add jitter to the coordinates
                lat, lon = add_jitter(lat, lon) 
                #add location to the db               
                add_location_to_db("N/A", "N/A", lat, lon)
                st.success(f"Location added: ({lat}, {lon})")
            except ValueError:
                st.error("Please enter valid numerical values for latitude and longitude.")
        else:
            st.error("Please enter both latitude and longitude.")

# Fetch locations from the database
locations_df = fetch_all_locations()    

# Load Oklahoma geoJSON data
with open("oklahoma.geojson") as f:
    oklahoma_geojson = json.load(f)
        
# Display the map centered on Oklahoma
oklahoma_coords = (35.4676, -97.5164)
m = folium.Map(location=oklahoma_coords, zoom_start=7)

# Add blue dots for each location in the DataFrame
for i, row in locations_df.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=5,
        color='#0000FF',
        fill=True,
        fill_color='#0000FF',
        fill_opacity=0.7,
        popup=f"{row['City']}, {row['State']}" if row['City'] != "N/A" else f"({row['Latitude']}, {row['Longitude']})"
    ).add_to(m)
    
#add state outline
oklahoma_layer = folium.GeoJson(
    data=oklahoma_geojson,
    name="Oklahoma",
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': 'blue',  # Outline color
        'weight': 3,      # Outline weight
        'opacity': 1
    }
).add_to(m)
    
# adjust the map zoom to ensure the whole state stays visible (as defined by geoJSON file)
bounds = oklahoma_layer.get_bounds()
m.fit_bounds(bounds)

# Group by city and state to get counts
location_counts = locations_df.groupby(['City', 'State']).size().reset_index(name='Count')

# Add a running total of all entries at the bottom of the dataframe
total_count = pd.DataFrame({'City': ['Total'], 'State': [''], 'Count': [location_counts['Count'].sum()]})
location_counts_with_total = pd.concat([location_counts, total_count], ignore_index=True)
st.dataframe(location_counts_with_total)

#Display the map and Dataframe
container = st.container()
with container:
    st_folium(m, width='100%', height=400)
    st.dataframe(location_counts_with_total)
    
#close db connection
conn.close()

st.markdown(
    """
    Oklahoma GeoJSON file from 
    [US States GeoJSON](https://raw.githubusercontent.com/deldersveld/topojson/master/countries/united-states/us-states.json)
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    Code for this page available at 
    [GitHub](https://github.com/jwiggi18/blue_dots)
    """,
    unsafe_allow_html=True
)



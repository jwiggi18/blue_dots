import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import folium
from streamlit_folium import st_folium
import random

# Initialize geolocator
geolocator = Nominatim(user_agent="blue_dots_oklahoma (jodiewiggins18@gmail.com)")

# Initialize an empty DataFrame to store locations
if 'locations' not in st.session_state:
    st.session_state['locations'] = pd.DataFrame(columns=['City', 'State', 'Latitude', 'Longitude'])

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

# List of U.S. states
states = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
    'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
    'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
    'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
    'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
    'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
    'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
    'Wisconsin', 'Wyoming'
]

# Find the index of "Oklahoma" in the states list
oklahoma_index = states.index("Oklahoma")

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


# Radio buttons to select input method
input_method = st.radio("Select input method", ("City and State", "Latitude and Longitude"))

if input_method == "City and State":
    # Input boxes for city and state
    city = st.text_input("Enter the City")
    # Dropdown menu for state
    state = st.selectbox("Select the State", options=states, index=oklahoma_index)


    # Button to add location
    if st.button("Add Location"):
        if city and state:
            lat, lon = get_lat_lon(city, state)
            if lat and lon:
                #Apply jitter
                lat, lon = add_jitter(lat, lon)
                #debugging
                st.write(f"Jittered coords: ({lat}, {lon})")
                # Add the location to the DataFrame
                new_data = {'City': city, 'State': state, 'Latitude': lat, 'Longitude': lon}
                #convert dictionary to dataframe with a single row
                new_data_df = pd.DataFrame([new_data])
                #add the new row to the existing df
                st.session_state['locations'] = pd.concat([st.session_state['locations'], new_data_df], ignore_index=True)
                
                st.success(f"Location added: {city}, {state} ({lat}, {lon})")
                # Debug: Print the df
                st.write(st.session_state['locations'])  # Check the current DataFrame content
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
                lat, lon = add_jitter(lat, lon) #add jitter to differentiate overlapping dots
                st.write(f"Jittered coordinates: ({lat}, {lon})") #debugging to check if jitter is working
                # Add the location to the DataFrame
                new_data = {'City': "N/A", 'State': "N/A", 'Latitude': lat, 'Longitude': lon}
                st.session_state['locations'] = st.session_state['locations'].append(new_data, ignore_index=True)
                
                st.success(f"Location added: ({lat}, {lon})")
                # Debug: Print the DataFrame
                st.write(st.session_state['locations'])  # Check the current DataFrame content
            except ValueError:
                st.error("Please enter valid numerical values for latitude and longitude.")
        else:
            st.error("Please enter both latitude and longitude.")

# Display the map centered on Oklahoma
oklahoma_coords = (35.0020, -98.50000)
m = folium.Map(location=oklahoma_coords, zoom_start=7)

# Add blue dots for each location in the DataFrame
for i, row in st.session_state['locations'].iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"{row['City']}, {row['State']}" if row['City'] != "N/A" else f"({row['Latitude']}, {row['Longitude']})",
        icon=folium.Icon(color="blue")
    ).add_to(m)

# Display the map
st_folium(m, width=800, height=450)

# Show the DataFrame of locations
st.dataframe(st.session_state['locations'])




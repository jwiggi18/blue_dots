import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Initialize geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

# Initialize an empty DataFrame to store locations
if 'locations' not in st.session_state:
    st.session_state['locations'] = pd.DataFrame(columns=['City', 'State', 'Latitude', 'Longitude'])

# Function to get lat, lon from city, state
def get_lat_lon(city, state):
    location = geolocator.geocode(f"{city}, {state}")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Title of the Streamlit app
st.title("Blue Dots in Oklahoma!!")

# Radio buttons to select input method
input_method = st.radio("Select input method", ("City and State", "Latitude and Longitude"))

if input_method == "City and State":
    # Input boxes for city and state
    city = st.text_input("Enter the City")
    state = st.text_input("Enter the State")

    # Button to add location
    if st.button("Add Location"):
        if city and state:
            lat, lon = get_lat_lon(city, state)
            if lat and lon:
                # Add the location to the DataFrame
                new_data = {'City': city, 'State': state, 'Latitude': lat, 'Longitude': lon}
                st.session_state['locations'] = st.session_state['locations'].append(new_data, ignore_index=True)
                
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
                # Add the location to the DataFrame
                new_data = {'City': "N/A", 'State': "N/A", 'Latitude': lat, 'Longitude': lon}
                st.session_state['locations'] = st.session_state['locations'].append(new_data, ignore_index=True)
                
                st.success(f"Location added: ({lat}, {lon})")
            except ValueError:
                st.error("Please enter valid numerical values for latitude and longitude.")
        else:
            st.error("Please enter both latitude and longitude.")

# Display the map centered on Oklahoma
oklahoma_coords = (35.0078, -97.0929)
m = folium.Map(location=oklahoma_coords, zoom_start=6)

# Add blue dots for each location in the DataFrame
for i, row in st.session_state['locations'].iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"{row['City']}, {row['State']}" if row['City'] != "N/A" else f"({row['Latitude']}, {row['Longitude']})",
        icon=folium.Icon(color="blue")
    ).add_to(m)

# Display the map
st_folium(m, width=700, height=500)

# Show the DataFrame of locations
st.dataframe(st.session_state['locations'])


import requests
import geopandas as gpd
import pandas as pd
import os

CACHE_FOLDER = "../data"

# all the countries in Asia for filtering
ASIAN_COUNTRIES = [
    'Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 
    'Bhutan', 'Brunei', 'Cambodia', 'China', 'Georgia', 'India', 
    'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan',
    'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives',
    'Mongolia', 'Myanmar', 'Nepal', 'North Korea', 'Oman', 'Pakistan',
    'Palestine', 'Philippines', 'Qatar', 'Saudi Arabia', 'Singapore',
    'South Korea', 'Sri Lanka', 'Syria', 'Taiwan', 'Tajikistan', 'Thailand',
    'Timor-Leste', 'Turkey', 'Turkmenistan', 'United Arab Emirates',
    'Uzbekistan', 'Vietnam', 'Yemen', 'Russia'
]

def get_earthquake_data(days_back=None, min_mag=5.0, start_date=None, end_date=None):
    # gets earthquake data from USGS API for Asia
    # can use either days_back OR specific start_date/end_date
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    
    # set up date parameters
    if start_date and end_date:
        # use specific date range (e.g., "2025-01-01" to "2025-12-31")
        starttime = start_date
        endtime = end_date
    else:
        # use days_back from today
        days = days_back if days_back else 365
        starttime = (pd.Timestamp.now() - pd.Timedelta(days=days)).isoformat()
        endtime = None
    
    params = {
        "format": "geojson",
        "starttime": starttime,
        "minmagnitude": min_mag,
        "minlatitude": -10,
        "maxlatitude": 80,
        "minlongitude": 25,
        "maxlongitude": 180
    }
    
    if endtime:
        params["endtime"] = endtime
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            gdf = gpd.GeoDataFrame.from_features(data["features"])
            if not gdf.empty:
                gdf.crs = "EPSG:4326"
                
                # depth is stored in the z coordinate of the geometry point
                if 'geometry' in gdf.columns:
                    gdf['depth_km'] = gdf.geometry.apply(lambda p: p.z if p.has_z else 10.0)
                    
            return gdf
        else:
            print("USGS error:", response.status_code)
            return gpd.GeoDataFrame()
            
    except Exception as e:
        print("Error:", e)
        return gpd.GeoDataFrame()

def get_cities_data():
    # downloads city data from Natural Earth
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)
        
    local_path = os.path.join(CACHE_FOLDER, "ne_10m_populated_places.json")
    
    # check if we already downloaded it
    if os.path.exists(local_path):
        return gpd.read_file(local_path)
    
    # download if not cached
    url = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_10m_populated_places_simple.geojson"
    try:
        print("Downloading cities...")
        cities = gpd.read_file(url)
        cities = cities[cities['pop_max'] > 100000].copy()
        
        # keep only Asian cities
        if 'adm0name' in cities.columns:
            cities = cities[cities['adm0name'].isin(ASIAN_COUNTRIES)].copy()
        elif 'ADM0NAME' in cities.columns:
            cities = cities[cities['ADM0NAME'].isin(ASIAN_COUNTRIES)].copy()
        
        # rename columns to be consistent
        if 'pop_max' in cities.columns:
            cities = cities.rename(columns={'pop_max': 'POP_MAX'})
        if 'name' in cities.columns:
            cities = cities.rename(columns={'name': 'NAME'})
            
        cities.to_file(local_path, driver="GeoJSON")
        return cities
    except Exception as e:
        print("Download failed:", e)
        return gpd.GeoDataFrame()

def get_country_boundaries():
    # get country shapes for the background of the map
    try:
        local_path = os.path.join(CACHE_FOLDER, "ne_110m_admin_0_countries.json")
        if os.path.exists(local_path):
            world = gpd.read_file(local_path)
        else:
            url = "https://raw.githubusercontent.com/martynafford/natural-earth-geojson/master/110m/cultural/ne_110m_admin_0_countries.json"
            print("Downloading country boundaries...")
            world = gpd.read_file(url)
            
            # fix column names
            if 'NAME' in world.columns and 'name' not in world.columns:
                 world['name'] = world['NAME']
            
            if not os.path.exists(CACHE_FOLDER):
                os.makedirs(CACHE_FOLDER)
            world.to_file(local_path, driver="GeoJSON")

        # filter just the Asian countries
        asia = world[world['name'].isin(ASIAN_COUNTRIES)].copy()
        return asia
    except Exception as e:
        print("Could not load boundaries:", e)
        return gpd.GeoDataFrame()

def load_asian_cities(min_population=250000):
    # loads cities and filters by population size
    cities = get_cities_data()
    
    if cities.empty:
        return cities
        
    # standardize the column names
    cols_map = {
        'NAME': 'name',
        'name': 'name',
        'ADM0NAME': 'country',
        'adm0name': 'country',
        'POP_MAX': 'population',
        'pop_max': 'population'
    }
    cities = cities.rename(columns=cols_map)
    
    # only keep cities above the population threshold
    cities = cities[cities['population'] >= min_population].copy()
    
    return cities

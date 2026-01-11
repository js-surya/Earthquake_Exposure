import numpy as np
from scipy.spatial import cKDTree
import geopandas as gpd

def build_kdtree(earthquakes_gdf):
    # builds a KD-tree so we can search for nearby earthquakes super fast
    # way faster than looping through everything
    coords = np.array(list(zip(earthquakes_gdf.geometry.x, earthquakes_gdf.geometry.y)))
    tree = cKDTree(coords)
    return tree, coords

def get_magnitude_based_radius(magnitude):
    # empirical formula for felt distance based on magnitude
    # source: seismological research literature
    # larger earthquakes can be felt much farther away
    # e.g. M5 = ~100km, M6 = ~300km, M7 = ~600km, M8 = ~1000km
    radius = 10 ** (0.5 * magnitude - 0.5)
    # minimum 50km, maximum 1500km
    return max(50, min(radius, 1500))

def find_earthquakes_within_radius(city_point, kdtree, earthquake_coords, earthquakes_gdf, radius_km):
    # finds all earthquakes within radius_km of the city
    radius_meters = radius_km * 1000  # convert to meters
    
    # query the tree to get all earthquakes in range
    indices = kdtree.query_ball_point([city_point.x, city_point.y], r=radius_meters)
    
    if not indices:
        return []  # no earthquakes found
        
    nearby_quakes = []
    
    for idx in indices:
        # calculate the actual distance to this earthquake
        eq_coord = earthquake_coords[idx]
        dist_meters = np.sqrt((city_point.x - eq_coord[0])**2 + (city_point.y - eq_coord[1])**2)
        dist_km = dist_meters / 1000.0
        
        # get the earthquake record
        eq_record = earthquakes_gdf.iloc[idx].to_dict()
        
        # sometimes the properties arent in a dict, so we need to make one
        if 'properties' not in eq_record:
            properties = {
                'mag': eq_record.get('mag', 0),
                'place': eq_record.get('place', 'Unknown'),
                'time': eq_record.get('time', 0),
            }
            eq_record['properties'] = properties
            
        eq_record['geometry'] = earthquakes_gdf.iloc[idx].geometry
        eq_record['dist_km'] = dist_km
        nearby_quakes.append(eq_record)
        
    return nearby_quakes

def find_earthquakes_with_dynamic_radius(city_point, kdtree, earthquake_coords, earthquakes_gdf, max_radius_km=1500):
    # uses magnitude-dependent radius for each earthquake
    # this is more scientifically accurate - bigger quakes affect farther cities
    
    # first get all earthquakes within max radius
    radius_meters = max_radius_km * 1000
    indices = kdtree.query_ball_point([city_point.x, city_point.y], r=radius_meters)
    
    if not indices:
        return []
        
    nearby_quakes = []
    
    for idx in indices:
        eq_record = earthquakes_gdf.iloc[idx]
        magnitude = eq_record.get('mag', 5.0)
        
        # calculate how far this magnitude can be felt
        felt_radius = get_magnitude_based_radius(magnitude)
        
        # calculate actual distance
        eq_coord = earthquake_coords[idx]
        dist_meters = np.sqrt((city_point.x - eq_coord[0])**2 + (city_point.y - eq_coord[1])**2)
        dist_km = dist_meters / 1000.0
        
        # only include if the city is within the felt radius for this magnitude
        if dist_km <= felt_radius:
            eq_dict = eq_record.to_dict()
            
            if 'properties' not in eq_dict:
                properties = {
                    'mag': eq_dict.get('mag', 0),
                    'place': eq_dict.get('place', 'Unknown'),
                    'time': eq_dict.get('time', 0),
                }
                eq_dict['properties'] = properties
                
            eq_dict['geometry'] = eq_record.geometry
            eq_dict['dist_km'] = dist_km
            nearby_quakes.append(eq_dict)
        
    return nearby_quakes

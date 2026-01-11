import pandas as pd
import numpy as np

def calculate_pga_gmpe(magnitude, distance_km, depth_km):
    # ok so this is the PGA formula from Campbell-Bozorgnia (2008)
    # basically it tells us how much the ground shakes
    
    # first calculate the 3D distance (pythagoras in 3D)
    r_hyp = np.sqrt(distance_km**2 + depth_km**2)
    
    # add 1 to avoid log(0) which would break everything
    r_term = r_hyp + 1.0
    
    # the actual formula from the paper
    log_pga = -1.8 + (0.6 * magnitude) - (1.8 * np.log10(r_term)) - (0.003 * r_term)
    
    # convert from log back to normal
    pga = 10 ** log_pga
    
    return pga

def calculate_city_risk_profile(city, nearby_earthquakes):
    # this function calculates how risky a city is based on nearby earthquakes
    
    # if there's no earthquakes nearby, the city is safe
    if not nearby_earthquakes:
        return {
            'city_name': city['name'],
            'country': city['country'],
            'population': city['population'],
            'max_pga': 0.0,
            'risk_category': 'MINIMAL',
            'risk_description': 'No significant shaking predicted',
            'num_earthquakes': 0,
            'num_shallow_quakes': 0,
            'max_magnitude': 0.0,
            'closest_quake_distance': float('inf'),
            'top_contributing_quakes': []
        }
    
    # let's process each earthquake and calculate its PGA
    processed_quakes = []
    
    for eq in nearby_earthquakes:
        mag = eq['properties']['mag']
        
        # depth can be in different places depending on how the data comes in
        # so we try all possible locations
        if 'depth_km' in eq:
            depth = eq['depth_km']
        elif 'depth_km' in eq['properties']:
            depth = eq['properties']['depth_km']
        elif isinstance(eq['geometry'], dict) and 'coordinates' in eq['geometry'] and len(eq['geometry']['coordinates']) > 2:
            depth = eq['geometry']['coordinates'][2]
        elif hasattr(eq['geometry'], 'has_z') and eq['geometry'].has_z:
            depth = eq['geometry'].z
        else:
            # if we can't find depth anywhere, just assume 10km
            depth = 10.0
            
        dist = eq.get('dist_km', 0)
        
        # now calculate how much this earthquake would shake the city
        pga = calculate_pga_gmpe(mag, dist, depth)
        
        # shallow earthquakes are way more dangerous
        if depth < 70:
            depth_type = 'SHALLOW'
        elif depth < 300:
            depth_type = 'INTERMEDIATE'
        else:
            depth_type = 'DEEP'
            
        # store all the info about this earthquake
        processed_quakes.append({
            'id': eq.get('id', 'unknown'),
            'magnitude': mag,
            'depth': depth,
            'depth_type': depth_type,
            'horizontal_distance': dist,
            'pga': pga,
            'place': eq['properties'].get('place', 'Unknown location'),
            'time': eq['properties']['time']
        })
    
    # find the maximum PGA (worst case scenario)
    max_pga = max(q['pga'] for q in processed_quakes) if processed_quakes else 0.0
    
    # now categorize the risk based on PGA value
    # these thresholds are from earthquake engineering standards
    if max_pga >= 0.5:
        category = 'CRITICAL'
        desc = 'Severe potential damage'
    elif max_pga >= 0.3:
        category = 'HIGH'
        desc = 'Moderate to heavy damage'
    elif max_pga >= 0.1:
        category = 'MODERATE'
        desc = 'Felt widely, slight damage'
    elif max_pga >= 0.02:
        category = 'LOW'
        desc = 'Felt by some, no damage'
    else:
        category = 'MINIMAL'
        desc = 'Not felt or weak shaking'
        
    # sort the earthquakes by PGA to see which ones are most dangerous
    top_quakes = sorted(processed_quakes, key=lambda x: x['pga'], reverse=True)
    
    # calculate some extra stats
    num_shallow = sum(1 for q in processed_quakes if q['depth'] < 70)
    max_mag = max(q['magnitude'] for q in processed_quakes)
    min_dist = min(q['horizontal_distance'] for q in processed_quakes)
    
    # return all the results as a dictionary
    return {
        'city_name': city['name'],
        'country': city['country'],
        'population': city['population'],
        'max_pga': max_pga,
        'risk_category': category,
        'risk_description': desc,
        'num_earthquakes': len(nearby_earthquakes),
        'num_shallow_quakes': num_shallow,
        'max_magnitude': max_mag,
        'closest_quake_distance': min_dist,
        'top_contributing_quakes': top_quakes[:5]  # just keep the top 5
    }

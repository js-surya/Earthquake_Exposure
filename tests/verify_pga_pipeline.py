import sys
import os
import pandas as pd
import geopandas as gpd

# Add src to path
# Add src to path
# Assuming running from project root
sys.path.insert(0, os.path.abspath("src"))

try:
    from earthquake_exposure import acquire, preprocess, spatial_index, metrics, viz
    print("✓ Imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

def main():
    print("Starting verification...")
    
    # 1. Acquire
    print("1. Acquiring data...")
    try:
        # fetch small amount of data to be fast
        quakes = acquire.get_earthquake_data(days_back=30, min_mag=5.0)
        print(f"  - Fetched {len(quakes)} earthquakes")
        if not quakes.empty and 'depth_km' in quakes.columns:
            print("  - 'depth_km' column found")
        else:
            print("  ✗ 'depth_km' column MISSING or no data")
            
        cities = acquire.load_asian_cities(min_population=1000000)
        print(f"  - Loaded {len(cities)} major cities")
    except Exception as e:
        print(f"✗ Acquire failed: {e}")
        return

    if quakes.empty or cities.empty:
        print("⚠ Empty data, skipping logic tests")
        return

    # 2. Preprocess
    print("\n2. Preprocessing...")
    try:
        quakes_proj = preprocess.project_to_metric(quakes)
        cities_proj = preprocess.project_to_metric(cities)
        print(f"  - Projected earthquakes to {quakes_proj.crs}")
        print(f"  - Projected cities to {cities_proj.crs}")
    except Exception as e:
        print(f"✗ Preprocess failed: {e}")
        return

    # 3. Spatial Index
    print("\n3. Spatial Indexing...")
    try:
        tree, coords = spatial_index.build_kdtree(quakes_proj)
        print(f"  - KD-Tree built with {len(coords)} points")
        
        # Test query for first city
        city = cities_proj.iloc[0]
        nearby = spatial_index.find_earthquakes_within_radius(
            city.geometry, tree, coords, quakes_proj, radius_km=3000 # Large radius to ensure matches
        )
        print(f"  - Found {len(nearby)} quakes near {city['name']} (search radius 3000km)")
    except Exception as e:
        print(f"✗ Spatial Index failed: {e}")
        return

    # 4. Metrics
    print("\n4. Metrics (PGA)...")
    try:
        city_info = {
            'name': city['name'],
            'country': city['country'],
            'population': city['population'],
            'geometry': city.geometry
        }
        risk = metrics.calculate_city_risk_profile(city_info, nearby)
        print(f"  - Risk Profile for {city['name']}:")
        print(f"    Max PGA: {risk['max_pga']:.4f}g")
        print(f"    Category: {risk['risk_category']}")
        print(f"    Shallow Quakes: {risk['num_shallow_quakes']}")
    except Exception as e:
        print(f"✗ Metrics calculation failed: {e}")
        return
        
    print("\n✓ Verification COMPLETE: Pipeline functionality validated.")

if __name__ == "__main__":
    main()

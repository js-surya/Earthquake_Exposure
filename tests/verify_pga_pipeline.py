# test_basic.py
# quick tests to make sure everything works

import sys
import os
sys.path.insert(0, os.path.abspath("src"))

from earthquake_exposure import acquire, preprocess, spatial_index, metrics

def test_pga_calculation():
    # test 1: check pga formula works
    pga = metrics.calculate_pga_gmpe(magnitude=6.0, distance_km=50, depth_km=10)
    print(f"Test 1: PGA for M6.0 at 50km = {pga:.4f}g")
    
    # bigger magnitude should give bigger pga
    pga_big = metrics.calculate_pga_gmpe(magnitude=7.0, distance_km=50, depth_km=10)
    if pga_big > pga:
        print("  OK - bigger magnitude = bigger PGA")
    else:
        print("  FAIL")

def test_pga_distance():
    # test 2: closer distance should give higher pga
    pga_close = metrics.calculate_pga_gmpe(magnitude=6.0, distance_km=20, depth_km=10)
    pga_far = metrics.calculate_pga_gmpe(magnitude=6.0, distance_km=100, depth_km=10)
    print(f"Test 2: PGA at 20km = {pga_close:.4f}g, at 100km = {pga_far:.4f}g")
    
    if pga_close > pga_far:
        print("  OK - closer = higher PGA")
    else:
        print("  FAIL")

def test_pga_depth():
    # test 3: shallow earthquakes should be more dangerous
    pga_shallow = metrics.calculate_pga_gmpe(magnitude=6.0, distance_km=50, depth_km=10)
    pga_deep = metrics.calculate_pga_gmpe(magnitude=6.0, distance_km=50, depth_km=100)
    print(f"Test 3: PGA at 10km depth = {pga_shallow:.4f}g, at 100km = {pga_deep:.4f}g")
    
    if pga_shallow > pga_deep:
        print("  OK - shallow = higher PGA")
    else:
        print("  FAIL")

def test_data_fetch():
    # test 4: check we can get earthquake data
    print("Test 4: Fetching earthquake data...")
    quakes = acquire.get_earthquake_data(days_back=30, min_mag=5.0)
    print(f"  Got {len(quakes)} earthquakes")
    
    if len(quakes) >= 0:  # even 0 is ok if no quakes in last 30 days
        print("  OK - data fetch works")

def test_cities_fetch():
    # test 5: check we can get city data
    print("Test 5: Fetching city data...")
    cities = acquire.load_asian_cities(min_population=1000000)
    print(f"  Got {len(cities)} cities")
    
    if len(cities) > 0:
        print("  OK - city data works")
    else:
        print("  FAIL - no cities found")

if __name__ == "__main__":
    print("Running 5 tests...\n")
    test_pga_calculation()
    test_pga_distance()
    test_pga_depth()
    test_data_fetch()
    test_cities_fetch()
    print("\nAll tests done!")

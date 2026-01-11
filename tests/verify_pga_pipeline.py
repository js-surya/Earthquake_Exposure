# test_basic.py
# just some quick tests to make sure things work

import sys
import os
sys.path.insert(0, os.path.abspath("src"))

from earthquake_exposure import acquire, preprocess, spatial_index, metrics

def test_pga_calculation():
    # test the pga formula with some known values
    pga = metrics.calculate_pga_gmpe(magnitude=6.0, distance_km=50, depth_km=10)
    print(f"PGA for M6.0 at 50km: {pga:.4f}g")
    
    # bigger magnitude should give bigger pga
    pga_big = metrics.calculate_pga_gmpe(magnitude=7.0, distance_km=50, depth_km=10)
    print(f"PGA for M7.0 at 50km: {pga_big:.4f}g")
    
    if pga_big > pga:
        print("OK - bigger magnitude = bigger PGA")
    else:
        print("FAIL - something's wrong")

def test_data_fetch():
    # try to get some earthquake data
    print("\nTrying to fetch earthquake data...")
    quakes = acquire.get_earthquake_data(days_back=30, min_mag=5.0)
    print(f"Got {len(quakes)} earthquakes")
    
    if len(quakes) > 0:
        print("OK - data fetching works")
    else:
        print("WARN - no earthquakes found (might be ok if none in last 30 days)")

if __name__ == "__main__":
    print("Running basic tests...\n")
    test_pga_calculation()
    test_data_fetch()
    print("\nDone!")

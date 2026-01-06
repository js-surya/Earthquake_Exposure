import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import pytest
from earthquake_exposure.preprocess import cleanup_gdf, fix_crs_to_metric
from earthquake_exposure.spatial_index import EarthquakeIndex
from earthquake_exposure.metrics import apply_normalization, get_final_score

# Test 1: Check if cleanup works
def test_cleanup_gdf():
    # Create a dummy dataframe with a missing geometry
    df = pd.DataFrame({
        'mag': [5.0, 6.0],
        'geometry': [Point(0, 0), None]
    })
    gdf = gpd.GeoDataFrame(df)
    
    cleaned = cleanup_gdf(gdf)
    
    # We should only have 1 row left
    assert len(cleaned) == 1
    # It should have a depth column now
    assert 'depth_km' in cleaned.columns

# Test 2: Check CRS projection
def test_fix_crs_to_metric():
    df = pd.DataFrame({'geometry': [Point(0, 0)]})
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326")
    
    projected = fix_crs_to_metric(gdf)
    
    # CRS should be 4087 now
    assert projected.crs == "EPSG:4087"

# Test 3: Check Spatial Index (KDTree)
def test_spatial_index():
    # Quakes at (0,0) and (10,10)
    df = pd.DataFrame({
        'mag': [5.0, 5.0],
        'geometry': [Point(0, 0), Point(10, 10)]
    })
    gdf = gpd.GeoDataFrame(df)
    index = EarthquakeIndex(gdf)
    
    # Query point (1,1) -> should be closest to (0,0) which is index 0
    # Distance should be small, approx sqrt(2) = 1.41
    dist = index.get_nearest_dist(1, 1)
    
    assert dist < 2.0

# Test 4: Check Normalization logic
def test_normalization():
    df = pd.DataFrame({
        'n_quakes': [1, 10],
        'm_max': [5, 8],
        'impact_score': [10, 100],
        'd_near': [100, 10]
    })
    
    norm = apply_normalization(df)
    
    # Max value in normalized columns should be 1.0 (or close to it)
    assert norm['n_quakes'].max() <= 1.0
    assert norm['m_max'].max() <= 1.0
    
# Test 5: Final Score Range
def test_final_score():
    df_norm = pd.DataFrame({
        'n_quakes': [0.5],
        'm_max': [0.5],
        'd_score': [0.5]
    })
    
    score = get_final_score(df_norm)
    
    # Score should be between 0 and 1
    assert score.iloc[0] >= 0
    assert score.iloc[0] <= 1

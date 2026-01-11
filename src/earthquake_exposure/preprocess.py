import geopandas as gpd

def project_to_metric(gdf, target_crs='EPSG:4087'):
    # Convert to a projection that measures distances in meters
    # EPSG:4087 is World Equidistant Cylindrical which works well for Asia
    if gdf.crs is None:
        gdf.crs = 'EPSG:4326'  # Assume lat/lon if not set
        
    return gdf.to_crs(target_crs)

def clean_earthquake_data(gdf):
    # Remove rows with missing data
    gdf = gdf[gdf.geometry.notnull()].copy()
    
    if 'mag' in gdf.columns:
        gdf = gdf[gdf['mag'].notnull()].copy()
        
    return gdf

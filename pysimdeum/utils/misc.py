import geopandas as gpd

def fix_invalid_geometries(gdf):
    """
    Fixes invalid geometries in a GeoDataFrame using the buffer(0) trick.

    Args:
        gdf (gpd.GeoDataFrame): The GeoDataFrame to fix.

    Returns:
        gpd.GeoDataFrame: The GeoDataFrame with fixed geometries.
    """
    gdf['geometry'] = gdf['geometry'].buffer(0)
    
    return gdf
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

def is_weekend_day(day_number):

    # Calculate the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = day_number % 7

    # Check if the day is either 5 (Saturday) or 6 (Sunday)Add commentMore actions

    return day_of_week in (5, 6)


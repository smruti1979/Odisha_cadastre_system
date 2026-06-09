import pandas as pd
import geopandas as gpd
import folium
from shapely import wkt
from sklearn.cluster import KMeans
import numpy as np

def convert_dataframe_to_geodataframe(df: pd.DataFrame) -> gpd.GeoDataFrame:
    if df.empty or 'geometry_wkt' not in df.columns:
        return gpd.GeoDataFrame(df, geometry=gpd.GeoSeries(), crs="EPSG:4326")
    df['geometry'] = df['geometry_wkt'].apply(wkt.loads)
    return gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

def build_interactive_satellite_map(joined_gdf: gpd.GeoDataFrame) -> folium.Map:
    """Builds a state-wide map view with dynamic ML spatial cluster coloring."""
    centroid = joined_gdf.geometry.unary_union.centroid
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=8, max_zoom=22)
    
    # --- FIX: Replaced broken Google Sat URL with the official XYZ tile map pattern ---
    folium.TileLayer(
        tiles='https://google.com{x}&y={y}&z={z}',
        attr='Google Satellite Engine',
        name='Odisha Regional Satellite View',
        overlay=False,
        control=True
    ).add_to(m)
    
    # --- INTEGRATING MACHINE LEARNING K-MEANS CLUSTERING ---
    coordinates = np.array([[geom.centroid.y, geom.centroid.x] for geom in joined_gdf.geometry])
    
    num_records = len(joined_gdf)
    n_clusters = min(3, num_records) 
    
    if n_clusters > 1:
        # Safeguarded configuration to ensure cross-compatibility with scikit-learn
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        joined_gdf['spatial_cluster_id'] = kmeans.fit_predict(coordinates)
    else:
        joined_gdf['spatial_cluster_id'] = 0
        
    cluster_colors = {0: '#ff0055', 1: '#00ffcc', 2: '#ffcc00'}
    
    for idx, row in joined_gdf.iterrows():
        color = cluster_colors.get(int(row['spatial_cluster_id']), '#ffffff')
        
        single_row_gdf = gpd.GeoDataFrame([row], geometry='geometry', crs="EPSG:4326")
        
        # Explicit clean type conversion to guarantee tooltip compatibility
        single_row_gdf['plot_no'] = single_row_gdf['plot_no'].astype(str)
        single_row_gdf['area_acres'] = single_row_gdf['area_acres'].astype(float)
        single_row_gdf['ai_confidence_score'] = single_row_gdf['ai_confidence_score'].astype(float)
        
        folium.GeoJson(
            single_row_gdf,
            name=f"Plot {row['plot_no']} (Cluster {row['spatial_cluster_id']})",
            style_function=lambda x, col=color: {
                'fillColor': col,
                'color': '#ff0000', # Red parcel outline boundaries
                'weight': 2,
                'fillOpacity': 0.45,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['tenant_name_en', 'district', 'city', 'plot_no', 'area_acres', 'ai_confidence_score'],
                aliases=['Owner:', 'District:', 'City:', 'Plot:', 'Acres:', 'AI Match Score:']
            )
        ).add_to(m)
        
    # Standardize map bounds using strict float primitive data casting
    minx, miny, maxx, maxy = joined_gdf.geometry.total_bounds
    m.fit_bounds([[float(miny), float(minx)], [float(maxy), float(maxx)]])
    
    return m
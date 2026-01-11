import plotly.express as px
import plotly.graph_objects as go
import folium
import pandas as pd
import json

def generate_interactive_map(cities_gdf, eq_gdf, exposure_df):
    # makes a folium map with cities and earthquakes
    center_lat = cities_gdf.geometry.y.mean()
    center_lon = cities_gdf.geometry.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=2, tiles='CartoDB positron')
    
    # add earthquake markers
    for _, row in eq_gdf.iterrows():
        depth_str = f"Depth: {row['depth_km']} km<br>" if 'depth_km' in row else ""
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=row['mag'],
            color='#FF4B4B',
            fill=True,
            fill_color='#FF4B4B',
            popup=folium.Popup(f"<b>Mag:</b> {row['mag']}<br>{depth_str}{row['place']}", max_width=200)
        ).add_to(m)

    # add city markers colored by risk
    for _, row in cities_gdf.iterrows():
        score_row = exposure_df[exposure_df['city_name'] == row['name']]
        if not score_row.empty:
            score = score_row.iloc[0]['max_pga']
            
            if score < 0.1:
                color = 'blue'
            elif score < 0.3:
                color = 'orange'
            else:
                color = 'red'
                
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=5 + (score * 50),
                color=color,
                fill=True,
                popup=f"{row['name']}: {score:.4f}g PGA"
            ).add_to(m)
            
    return m

def generate_interactive_dashboard(eq_gdf, exposure_df):
    # makes scatter plots for analysis
    fig1 = px.scatter(
        eq_gdf,
        x='mag',
        y='depth_km' if 'depth_km' in eq_gdf.columns else 'mag',
        color='mag',
        title="Earthquake Depth vs Magnitude",
        color_continuous_scale='Viridis',
        labels={'mag': 'Magnitude', 'depth_km': 'Depth (km)'}
    )
    if 'depth_km' in eq_gdf.columns:
        fig1.update_yaxes(autorange="reversed")
    fig1.update_layout(template="plotly_white")

    fig2 = px.scatter(
        exposure_df,
        x='closest_quake_distance',
        y='max_pga',
        size='population',
        color='max_magnitude',
        hover_name='city_name',
        title="City Risk: PGA vs Distance",
        labels={'closest_quake_distance': 'Dist to Quake (km)', 'max_pga': 'Max PGA (g)'},
        size_max=40
    )
    fig2.update_layout(template="plotly_white")
    
    return fig1, fig2

def generate_plotly_map(cities_gdf, eq_gdf, exposure_df, boundaries_gdf=None):
    # creates the main interactive map with plotly
    cities_df = cities_gdf.copy()
    cities_df = cities_df.merge(
        exposure_df[['city_name', 'max_pga', 'num_earthquakes', 'max_magnitude', 'closest_quake_distance']], 
        left_on='name', 
        right_on='city_name', 
        how='inner'
    )
    
    # only show cities with some risk
    cities_df = cities_df[cities_df['max_pga'] > 0].copy()
    
    cities_df['lat'] = cities_df.geometry.y
    cities_df['lon'] = cities_df.geometry.x
    
    # hover text
    country_col = 'country' if 'country' in cities_df.columns else 'adm0name'
    country_name = cities_df[country_col] if country_col in cities_df.columns else "Unknown"
    
    cities_df['hover_text'] = (
        "<b>" + cities_df['name'] + "</b> (" + country_name + ")<br>" +
        "Population: " + cities_df['population'].apply(lambda x: f"{x:.0f}") + "<br>" +
        "Max PGA: " + cities_df['max_pga'].round(4).astype(str) + "g<br>" +
        "Nearby Quakes: " + cities_df['num_earthquakes'].astype(str)
    )

    # earthquake data
    eq_df = eq_gdf.copy()
    eq_df['lat'] = eq_df.geometry.y
    eq_df['lon'] = eq_df.geometry.x
    
    # convert time to date
    if pd.api.types.is_numeric_dtype(eq_df['time']):
        eq_df['date'] = pd.to_datetime(eq_df['time'], unit='ms').dt.strftime('%Y-%m-%d')
    else:
        eq_df['date'] = pd.to_datetime(eq_df['time']).dt.strftime('%Y-%m-%d')
    
    eq_df['hover_text'] = (
        "<b>Magnitude " + eq_df['mag'].astype(str) + "</b><br>" +
        eq_df['place'] + "<br>" +
        "Date: " + eq_df['date'] + "<br>" +
        "Depth: " + eq_df['depth_km'].astype(str) + " km"
    )

    fig = go.Figure()

    # add country boundaries if we have them
    if boundaries_gdf is not None and not boundaries_gdf.empty:
        geojson = json.loads(boundaries_gdf.to_json())
        
        fig.add_trace(go.Choroplethmapbox(
            geojson=geojson,
            locations=boundaries_gdf['name'],
            featureidkey="properties.name",
            z=[1] * len(boundaries_gdf),
            colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],
            marker_line_color='darkgrey',
            marker_line_width=1,
            showscale=False,
            hoverinfo='location',
            name='Boundaries'
        ))

    # add earthquakes
    fig.add_trace(go.Scattermapbox(
        lat=eq_df['lat'],
        lon=eq_df['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=eq_df['mag'] ** 2.5 / 2,
            color=eq_df['mag'],
            colorscale='YlOrRd',
            cmin=5.0,
            cmax=8.0,
            opacity=0.7,
            showscale=True,
            colorbar=dict(title="Magnitude", x=0.02, y=0.5, len=0.5)
        ),
        text=eq_df['hover_text'], hoverinfo='text', name='Earthquakes'
    ))

    # add cities
    fig.add_trace(go.Scattermapbox(
        lat=cities_df['lat'],
        lon=cities_df['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10, 
            color=cities_df['max_pga'],
            colorscale='Viridis_r',
            showscale=True,
            cmin=0,
            cmax=0.5,
            colorbar=dict(title="Max PGA (g)", x=0.98, len=0.5)
        ),
        text=cities_df['hover_text'], hoverinfo='text', name='Cities at Risk'
    ))

    # set up the map
    fig.update_layout(
        title="Asian Cities Seismic Risk Analysis (Year 2025)",
        mapbox_style="carto-positron",
        mapbox=dict(center=dict(lat=30, lon=100), zoom=2.5),
        margin={"r":0,"t":50,"l":0,"b":0},
        height=800
    )

    
    return fig

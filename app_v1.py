"""
MUSA 509 FINAL PROJECT
"""

#import packages
import requests
import geopandas as gpd
import pandas as pd
from cartoframes.viz import Layer, Map, color_category_style, popup_element
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import json
import matplotlib.colors as mcolors
from matplotlib import pyplot as plt
import folium #New
import carto2gpd #New
import json
import logging
from flask import Flask, request, render_template
from datetime import datetime



# load credentials from a file
with open("jxl.json", "r") as f_in:
    pg_creds = json.load(f_in)

# mapbox
with open("mapbox_token.json", "r") as mb_token:
    MAPBOX_TOKEN = json.load(mb_token)["token"]


app = Flask(__name__, template_folder="templates")

# load credentials from JSON file
HOST = pg_creds["HOST"]
USERNAME = pg_creds["USERNAME"]
PASSWORD = pg_creds["PASSWORD"]
DATABASE = pg_creds["DATABASE"]
PORT = pg_creds["PORT"]


# index page
@app.route("/")
def index():
    """Index page"""

    return render_template("page1.html")



#Functions

#get engine function
def get_sql_engine():
    return create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")


def get_address(address):
    
    geocoding_call = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    resp = requests.get(
        geocoding_call,
        params={'access_token': MAPBOX_TOKEN}
    )

    lng, lat = resp.json()["features"][0]["center"]
    return [lat, lng]

#get zipcode data
def zip_geom():
    """Get all geometry of Philly zipcode"""
    engine = get_sql_engine()
    zipgeom = text(
        """
    SELECT zip_code, geom
    FROM philly_zipcode
    """
    )
    zipgeom = gpd.read_postgis(zipgeom, con=engine)
    return zipgeom


#Get covid real-time data
def covid_realtime():
    """
    Get real-time accumulated covid data by each zip code.
    """
    url = "https://phl.carto.com/api/v2/sql"
    gdf = carto2gpd.get(url, "covid_cases_by_zip",fields=['zip_code', 'count', "etl_timestamp"])
    return gdf


#Merge two datasets and output to geodataframe
def merge_table(t1, t2):
    """
    Merge the covid data with the Philly zipcode data to get geometry.
    Because we need to change column at the later part, please make covid_data as t1,
    and make the Philly zip_code data as t2.
    """
    input1 = pd.merge(t1, t2, on="zip_code", how="inner")
    covid_zip = gpd.GeoDataFrame(input1)

    #change column name
    covid_zip.columns = ["zip_code", "covid_cases", "time", "geometry"]
    return covid_zip


def normalize(merged_table):
    """
    Normalize the covid data to used them in matplotlib color scheme.
    """
    #add normalization
    # Minimum
    min_val = merged_table['covid_cases'].min()

    # Maximum
    max_val = merged_table['covid_cases'].max()

    # Calculate a normalized column
    normalized = (merged_table['covid_cases'] - min_val) / (max_val - min_val)

    # Add to the dataframe
    merged_table['n_covid'] = normalized
    return merged_table


#change the geodataframe to geojson
def to_geojson(gdf):
    """
    Change the geodataframe to geojson.
    """
    covid_json = gdf.to_json()
    return covid_json

#define camp
cmap = plt.get_cmap('YlOrRd')

#For Folium map
#get style function
def get_style(feature):
    """
    Given an input GeoJSON feature, return a style dict.
    
    Notes
    -----
    The color in the style dict is determined by the 
    "percent_no_internet_normalized" column in the 
    input "feature".
    """
    # Get the data value from the feature
    value = feature['properties']['n_covid']
    
    # Evaluate the color map
    # NOTE: value must between 0 and 1
    rgb_color = cmap(value) # this is an RGB tuple
    
    # Convert to hex string
    color = mcolors.rgb2hex(rgb_color)
    
    # Return the style dictionary
    return {'weight': 2, 'color':"tomato", 'fillColor': color, "fillOpacity": 0.75}


def get_highlighted_style(feature):
    """
    Return a style dict to use when the user highlights a 
    feature with the mouse.
    """
    
    return {"weight": 3, "color": "black"}


#make folium map
def covid_map(geojson, add):
    """
    Output a folium map, which shows covid_cases by zipcode and indicate the user's
    entering address.
    """
    #make the map centered at Philly center
    m = folium.Map(location=[39.99, -75.13],tiles='Cartodb Positron',zoom_start=11)

    folium.GeoJson(
        geojson,
        style_function=get_style,
        highlight_function=get_highlighted_style,
        tooltip=folium.GeoJsonTooltip(['zip_code', 'covid_cases']) 
    ).add_to(m)

    #Add the point which indicates the user's location
    point_cor =get_address(add)

    folium.Marker(location=point_cor,
    icon=folium.Icon(color='black')).add_to(m)

    return m



@app.route("/covidviewer", methods=["GET"])
def covid_viewer():
    """
    Get the url page based on the entering address.
    """
    name = request.args["address"]
    pzip = zip_geom() #get the Philly zipcode data
    cr = covid_realtime() #get the covid real time data
    output1 = merge_table(cr, pzip) #merge two table together by zipcode
    output2= normalize(output1) #normalize the covid data
    covid_json = to_geojson(output2) #make the geodataframe to geojson

    figure = covid_map(covid_json, name)
    curr_time = datetime.now().strftime("%B %d, %Y")

    return render_template(
        "page2.html",
        map=figure._repr_html_(),
        curr_time = curr_time
    )








# 404 page example
@app.errorhandler(404)
def page_not_found(err):
    """404 page"""
    return f"404 ({err})"


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)
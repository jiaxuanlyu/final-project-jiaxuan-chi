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
from shapely.geometry import shape



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
        name=name,
        map=figure._repr_html_(),
        curr_time = curr_time
    )


def get_zipcode_names(add):
    """Gets the zipcode of your input address"""
    lng=get_address(add)[1]
    lat=get_address(add)[0]
    engine = get_sql_engine()
    query = text(
        """
        SELECT
        code
        FROM philly_zipcode
        WHERE ST_Intersects(geom, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
    """
    )
    resp = engine.execute(query,lng=lng, lat=lat).fetchall()
    # get a list of names
    names = [row["code"] for row in resp][0]
    return names


def get_num_stations(add):
    """Get number of stations in a zipcode"""
    name=get_zipcode_names(add)
    engine = get_sql_engine()
    station_stats = text(
        """
        SELECT
        count(v.*) as num_stations
        FROM indego_rt1130 as v
        JOIN philly_zipcode as n
        ON ST_Intersects(v.geom, n.geom)
        WHERE n.code = :name
    """
    )
    resp = engine.execute(station_stats, name=name).fetchone()
    return resp["num_stations"]



def get_zipcode_stations(add):
    """Get all stations for a zipcode"""
    name=get_zipcode_names(add)
    engine = get_sql_engine()
    neighborhood_stations = text(
        """
        SELECT
        "name" as name,
        "addressStreet" as address,
        "bikesAvailable" as available_bikes,
        v.geom as geom,
        ST_X(v.geom) as lon, ST_Y(v.geom)as lat
        FROM indego_rt1130 as v
        JOIN philly_zipcode as n
        ON ST_Intersects(v.geom, n.geom)
        WHERE n.code = :name
    """
    )
    stations = gpd.read_postgis(neighborhood_stations, con=engine, params={"name": name})
    return stations


def make_folium_map(station_coord):
    map = folium.Map(location=station_coord[0], tiles='Cartodb Positron', zoom_start=13)
    for point in range(0, len(station_coord)):
        folium.Marker(station_coord[point]).add_to(map)

    return map


# station viewer page
@app.route("/stationviewer", methods=["GET"])
def station_viewer():
    """Test for form"""
    name = request.args["address"]
    stations = get_zipcode_stations(name)
    stations['coordinate'] = 'end_point='+stations['name'].astype(str)+'&'+'end_lng=' + stations['lon'].astype(str)+'&'+'end_lat='+stations['lat'].astype(str)

    #genetrate folium map
    station_coordinates = stations[["lat", "lon"]].values.tolist()

    map=make_folium_map(station_coordinates)


    # generate interactive map

    return render_template(
        "page3.html",
        num_stations=get_num_stations(name),
        address=name,
        stations=stations[["name", "address", "available_bikes", 'coordinate']].values,
        map=map._repr_html_()
    )


#get num hospitals
def get_num_hospitals(add):
    """Get number of hospitals in a zipcode"""
    name=get_zipcode_names(add)
    engine = get_sql_engine()
    number_hospitals = text(
        """
        SELECT 	COUNT("HOSPITAL_NAME") AS num_hospitals
        FROM philly_hospital
        WHERE "ZIP_CODE" = :name
    """
    )
    resp = engine.execute(number_hospitals, name=name).fetchone()
    return resp["num_hospitals"]




def get_zipcode_hospitals(add):
    """Get all hospitals within a zipcode"""
    name=get_zipcode_names(add)
    engine = get_sql_engine()
    hospital_info = text(
        """
        SELECT 
	    "HOSPITAL_NAME" AS name, "STREET_ADDRESS" as address, 
        "PHONE_NUMBER" as contact, geom,
        ST_X(geom) AS lon, ST_Y(geom) AS lat
        FROM philly_hospital
        WHERE "ZIP_CODE" = :name
    """
    )
    hospitals = gpd.read_postgis(hospital_info, con=engine, params={"name": name})
    return hospitals




# hospital viewer page
@app.route("/hospitalviewer", methods=["GET"])
def hospital_viewer():
    """Test for form"""
    name = request.args["address"]
    hospitals = get_zipcode_hospitals(name)
    hospitals['coordinate'] = 'end_point='+hospitals['name'].astype(str)+'&'+'end_lng=' + hospitals['lon'].astype(str)+'&'+'end_lat='+hospitals['lat'].astype(str)
    #genetrate folium map
    hospitals_coordinates = hospitals[["lat", "lon"]].values.tolist()

    map=make_folium_map(hospitals_coordinates)


    # generate interactive map

    return render_template(
        "page3_2h.html",
        num_hospitals=get_num_hospitals(name),
        address=name,
        hospitals=hospitals[["name", "address", "contact", "coordinate"]].values,
        map=map._repr_html_()
    )








def get_static_map(start_lng, start_lat, end_lng, end_lat):
    """"""
    geojson_str = get_map_directions(start_lng, start_lat, end_lng, end_lat)
    return (
        f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/"
        f"geojson({geojson_str})/auto/640x640?access_token={MAPBOX_TOKEN}"
    ), geojson_str


def get_map_directions(start_lng, start_lat, end_lng, end_lat):
    directions_resp = requests.get(
        f"https://api.mapbox.com/directions/v5/mapbox/walking/{start_lng},{start_lat};{end_lng},{end_lat}",
        params={
            "access_token": MAPBOX_TOKEN,
            "geometries": "geojson",
            "steps": "false",
            "alternatives": "true",
        },
    )
    routes = gpd.GeoDataFrame(
        geometry=[
            shape(directions_resp.json()["routes"][idx]["geometry"])
            for idx in range(len(directions_resp.json()["routes"]))
        ]
    )
    return routes.iloc[:1].to_json()


def get_map_instructions(start_lng, start_lat, end_lng, end_lat):
#retrieve instructions
    directions_resp = requests.get(
        f"https://api.mapbox.com/directions/v5/mapbox/walking/{start_lng},{start_lat};{end_lng},{end_lat}",
        params={
            "access_token": MAPBOX_TOKEN,
            "geometries": "geojson",
            "steps": "true",
            "alternatives": "true",
        },
    )
    instructions=[]
    for step in directions_resp.json()['routes'][0]['legs'][0]['steps']:
        instructions.append(f"{step['maneuver']['instruction']}")
    #listToStr = '<br>'.join(map(str, instruction))
    return instructions


@app.route("/walking", methods=["GET"])
def walking():
    name = request.args["address"]
    end_name=request.args["end_point"]
    end_lng = request.args["end_lng"]
    end_lat = request.args["end_lat"]
    end_lng = float(end_lng)
    end_lat = float(end_lat)
    start_lng=get_address(name)[1]
    start_lat=get_address(name)[0]


    #get coordinates of start and end point
    map_directions, geojson_str = get_static_map(
        start_lng=start_lng,
        start_lat=start_lat,
        end_lng=end_lng,
        end_lat=end_lat,
    )
    logging.warning("Map directions %s", str(map_directions))


    #retrieve instructions
    instructions = get_map_instructions(
        start_lng=start_lng,
        start_lat=start_lat,
        end_lng=end_lng,
        end_lat=end_lat,
    )


    # generate interactive map
    return render_template(
        "page4.html",
        mapbox_token=MAPBOX_TOKEN,
        geojson_str=geojson_str,
        end_name=end_name,
        name=name,
        start_lng=start_lng,
        start_lat=start_lng,
        end_lng=end_lng,
        end_lat=end_lat,
        center_lng=(start_lng + end_lng) / 2,
        center_lat=(start_lat + end_lat) / 2,
        instructions=instructions
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

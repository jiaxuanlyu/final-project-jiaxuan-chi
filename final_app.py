"""MUSA 509 demo app"""
import json
import logging

from flask import Flask, request, render_template
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import geopandas as gpd
import folium ##New !!

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


def get_sql_engine():
    return create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")


def get_neighborhood_names():
    """Gets all neighborhoods for Philadelphia"""
    engine = get_sql_engine()
    query = text(
        """
        SELECT DISTINCT neighborhood_name
        FROM philly_neighborhoods
        ORDER BY 1 ASC
    """
    )
    resp = engine.execute(query).fetchall()
    # get a list of names
    names = [row["neighborhood_name"] for row in resp]
    return names


# index page
@app.route("/")
def index():
    """Index page"""
    names = get_neighborhood_names()
    return render_template("input.html", nnames=names)


def get_bounds(geodataframe):
    """returns list of sw, ne bounding box pairs"""
    bounds = geodataframe.geom.total_bounds
    bounds = [[bounds[0], bounds[1]], [bounds[2], bounds[3]]]
    return bounds


def get_num_stations(start_name):
    """Get number of stations in a neighborhood"""
    engine = get_sql_engine()
    station_stats = text(
        """
        SELECT
        count(v.*) as num_stations
        FROM indego_rt1130 as v
        JOIN philly_neighborhoods as n
        ON ST_Intersects(v.geom, n.geom)
        WHERE n.neighborhood_name = :start_name
    """
    )
    resp = engine.execute(station_stats, start_name=start_name).fetchone()
    return resp["num_stations"]



def get_neighborhood_stations(start_name):
    """Get all stations for a neighborhood"""
    engine = get_sql_engine()
    neighborhood_stations = text(
        """
        SELECT
        "name" as Name,
        "addressStreet" as address,
        "bikesAvailable" as available_bikes,
        v.geom as geom,
        ST_X(v.geom) as lon, ST_Y(v.geom)as lat
        FROM indego_rt1130 as v
        JOIN philly_neighborhoods as n
        ON ST_Intersects(v.geom, n.geom)
        WHERE n.neighborhood_name = :start_name
    """
    )
    stations = gpd.read_postgis(neighborhood_stations, con=engine, params={"start_name": start_name})
    return stations


def make_folium_map(station_coord):
    map = folium.Map(location=station_coord[0], zoom_start=13)
    for point in range(0, len(station_coord)):
        folium.Marker(station_coord[point]).add_to(map)

    return map


# station viewer page
@app.route("/stationviewer", methods=["GET"])
def station_viewer():
    """Test for form"""
    name = request.args["neighborhood"]
    stations = get_neighborhood_stations(name)
    bounds = get_bounds(stations)

    #genetrate folium map
    station_coordinates = stations[["lat", "lon"]].values.tolist()

    map=make_folium_map(station_coordinates)


    # generate interactive map

    return render_template(
        "bike.html",
        num_stations=get_num_stations(name),
        nname=name,
        stations=stations[["name", "address", "available_bikes"]].values,
        map=map._repr_html_()
    )



@app.route("/cycling", methods=["GET"])
def cycling():
    start_name = request.args.get("neighborhood")
    start_name = start_name
    end_name = end_name
    #get coordinates of start point
    geocoding_call = (
        "https://api.mapbox.com/geocoding/v5/mapbox.places/"
        f"{start_name}.json?access_token={MAPBOX_TOKEN}"
    )
    resp = requests.get(geocoding_call)
    lng, lat = resp.json()["features"][0]["center"]

    #get coordinates of end point
    geocoding_call_end = (
        "https://api.mapbox.com/geocoding/v5/mapbox.places/"
        f"{end_name}.json?access_token={MAPBOX_TOKEN}"
    )
    end_resp = requests.get(geocoding_call_end)
    end_lng, end_lat = end_resp.json()["features"][0]["center"]

    map_directions, geojson_str = get_static_map(
        start_lng=lng,
        start_lat=lat,
        end_lng=end_lng,
        end_lat=end_lat,
    )
    logging.warning("Map directions %s", str(map_directions))

    #interactive map
    cycle_map = render_template(
        "cycle_map.html",
        mapbox_token=MAPBOX_TOKEN,
        geojson_str=geojson_str,
        center_lng=(lng + end_lng) / 2,
        center_lat=(lat + end_lat) / 2,
    )
    logging.warning(cycle_map)

    # generate interactive map
    return render_template(
        "bike_route.html",
        cycle_map=cycle_map
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
        f"https://api.mapbox.com/directions/v5/mapbox/cycling/{start_lng},{start_lat};{end_lng},{end_lat}",
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


# 404 page example
@app.errorhandler(404)
def page_not_found(err):
    """404 page"""
    return f"404 ({err})"


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)

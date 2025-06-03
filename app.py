from flask import Flask, jsonify, request, render_template
import requests
import math
from datetime import datetime, timedelta

app = Flask(__name__)

MAX_RADIUS_KM = 300

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) ** 2 + math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) * math.sin(dlon/2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def ambil_data_opensky():
    url = "https://opensky-network.org/api/states/all"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data.get("states", [])
    except Exception as e:
        print("Gagal ambil data:", e)
        return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    # dapatkan lat lon dari parameter request? Jika tidak ada, default ke Letung
    airport_coords = {
        "letung": (3.346028, 106.2666007),
        "jakarta": (-6.1256, 106.6558),
        "palembang": (-2.898, 104.699),
        "pontianak": (0.1507, 109.403),
        "aceh": (5.522, 95.4204),
        "medan": (3.5591, 98.6717),
        "padang": (-0.8761, 100.351),
        "bali": (-8.7482, 115.1675),
        "balikpapan": (-1.267, 116.893),
        "semarang": (-6.9728, 110.375),
        "yia": (-7.906, 110.061)
    }

    airport = request.args.get("airport", "letung").lower()
    center_lat, center_lon = airport_coords.get(airport, (3.346028, 106.2666007))

    states = ambil_data_opensky()
    filtered = []
    wib_time = datetime.utcnow() + timedelta(hours=7)
    timestamp = wib_time.strftime("%Y-%m-%d %H:%M:%S")

    for s in states:
        lat = s[6]
        lon = s[5]
        if lat is not None and lon is not None:
            jarak = haversine(center_lat, center_lon, lat, lon)
            if jarak <= MAX_RADIUS_KM:
                filtered.append({
                    "timestamp": timestamp,
                    "icao24": s[0],
                    "callsign": s[1].strip() if s[1] else "",
                    "country": s[2],
                    "longitude": lon,
                    "latitude": lat,
                    "altitude": s[7],
                    "distance_km": round(jarak, 2)
                })
    return jsonify(filtered)

if __name__ == "__main__":
    app.run(debug=True)

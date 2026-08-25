"""Florida metro/county centroids — shared by staging.py (forecast risk) and
canvass.py (route seeds). Coarse but good enough to test point-in-polygon and
seed canvassing grids; production swaps in real geocoded addresses."""

FL_PLACES = [
    {"name": "Jacksonville",   "county": "Duval",       "lat": 30.33, "lon": -81.66},
    {"name": "Miami",          "county": "Miami-Dade",  "lat": 25.77, "lon": -80.19},
    {"name": "Fort Lauderdale","county": "Broward",     "lat": 26.12, "lon": -80.14},
    {"name": "West Palm Beach","county": "Palm Beach",  "lat": 26.71, "lon": -80.06},
    {"name": "Tampa",          "county": "Hillsborough","lat": 27.95, "lon": -82.46},
    {"name": "Riverton", "county": "Pinellas",    "lat": 27.77, "lon": -82.64},
    {"name": "Orlando",        "county": "Orange",      "lat": 28.54, "lon": -81.38},
    {"name": "Kissimmee",      "county": "Osceola",     "lat": 28.29, "lon": -81.41},
    {"name": "Ocala",          "county": "Marion",      "lat": 29.19, "lon": -82.13},
    {"name": "The Villages",   "county": "Sumter",      "lat": 28.93, "lon": -81.96},
    {"name": "Fort Myers",     "county": "Lee",         "lat": 26.64, "lon": -81.87},
    {"name": "Naples",         "county": "Collier",     "lat": 26.14, "lon": -81.79},
    {"name": "Sarasota",       "county": "Sarasota",    "lat": 27.34, "lon": -82.53},
    {"name": "Melbourne",      "county": "Brevard",     "lat": 28.08, "lon": -80.61},
    {"name": "Port St. Lucie", "county": "St. Lucie",   "lat": 27.27, "lon": -80.35},
    {"name": "Stuart",         "county": "Martin",      "lat": 27.20, "lon": -80.25},
    {"name": "Tallahassee",    "county": "Leon",        "lat": 30.44, "lon": -84.28},
    {"name": "Panama City",    "county": "Bay",         "lat": 30.16, "lon": -85.66},
    {"name": "Blountstown",    "county": "Calhoun",     "lat": 30.44, "lon": -85.05},
    {"name": "Pensacola",      "county": "Escambia",    "lat": 30.42, "lon": -87.22},
    {"name": "Gainesville",    "county": "Alachua",     "lat": 29.65, "lon": -82.32},
    {"name": "Wesley Chapel",  "county": "Pasco",       "lat": 28.24, "lon": -82.33},
    {"name": "Bunnell",        "county": "Flagler",     "lat": 29.47, "lon": -81.26},
]

BY_COUNTY = {p["county"]: p for p in FL_PLACES}

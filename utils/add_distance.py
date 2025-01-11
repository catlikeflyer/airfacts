import pandas as pd
import math
import os

# Haversine formula to calculate distance between two coordinates


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    print(f"Distance: {R * c}")
    return R * c


# Load the CSV files
base_dir = os.path.dirname(os.path.abspath(__file__))
airports_df = pd.read_csv(os.path.join(base_dir, "../datasets/airports.csv"))
routes_df = pd.read_csv(os.path.join(base_dir, "../datasets/routes.csv"))

# Create a dictionary to map airport IDs to their coordinates
airport_coords = airports_df.set_index(
    "Airport ID")[["Latitude", "Longitude"]].to_dict("index")
print(airport_coords)
# List of airport IDs, all items to strings
airport_ids = airports_df["Airport ID"].astype(str).tolist()

# Add a Distance column to the routes DataFrame
distances = []
for _, row in routes_df.iterrows():
    source_id = row["Source airport ID"]
    dest_id = row["Destination airport ID"]

    # Get coordinates
    if source_id in airport_ids and dest_id in airport_ids:
        source_coords = airport_coords[source_id]
        dest_coords = airport_coords[dest_id]
        distance = haversine(source_coords["Latitude"], source_coords["Longitude"],
                             dest_coords["Latitude"], dest_coords["Longitude"])
        distances.append(distance)
    else:
        distances.append("N")

routes_df["Distance"] = distances

# Save the updated routes CSV
routes_df.to_csv(os.path.join(
    base_dir, "../datasets/routes_with_distances.csv"), index=False)
print("Updated routes CSV with distances saved.")

import requests
import json

def autocomplete_places_new_python(api_key: str, input_text: str, latitude: float, longitude: float, radius: float):
    """
    Makes a POST request to the Google Places Autocomplete (New) API.

    Args:
        api_key: Your Google Cloud API key with Places API (New) enabled.
        input_text: The text input for autocomplete (e.g., "pizza").
        latitude: Latitude for location bias.
        longitude: Longitude for location bias.
        radius: Radius in meters for location bias.

    Returns:
        The JSON response from the API, or None if an error occurs.
    """
    url = "https://places.googleapis.com/v1/places:autocomplete"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location" # Specify fields to return
    }

    payload = {
        "input": input_text,
        "locationBias": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")
        return None

# --- How to use it ---
if __name__ == "__main__":
    YOUR_API_KEY = "YOUR_API_KEY_HERE"  # <--- REPLACE WITH YOUR ACTUAL API KEY
    
    if YOUR_API_KEY == "YOUR_API_KEY_HERE":
        print("Please replace 'YOUR_API_KEY_HERE' with your actual Google Cloud API key.")
    else:
        results = autocomplete_places_new_python(
            api_key=YOUR_API_KEY,
            input_text="pizza",
            latitude=37.7937,
            longitude=-122.3965,
            radius=500.0
        )

        if results:
            print("\n--- Autocomplete Results (Python) ---")
            for place in results.get("places", []):
                print(f"Name: {place.get('displayName', {}).get('text')}")
                print(f"Address: {place.get('formattedAddress')}")
                print(f"Location: {place.get('location')}")
                print("-" * 20)
        else:
            print("No results or an error occurred.")
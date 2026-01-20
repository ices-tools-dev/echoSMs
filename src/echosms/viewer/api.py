import requests
import json
from pathlib import Path


# Setup Cache Directory
CACHE_DIR = Path.home() / ".echosms" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
# Note: The /v2 suffix is important as endpoints are relative to it.
BASE_URL = "https://echosms-data-store-app-ogogm.ondigitalocean.app/v2"


def fetch_online_shapes_index():
    """Fetches the list of available shapes from the official datastore index.
    """
    url = f"{BASE_URL}/specimens"
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Construct dict: "Vernacular Name (ID) [Model]" -> "ID"
        index = {}
        for item in data:
            name = item.get('vernacular_name') or item.get('name') or "Unknown"
            sid = item.get('id')
            m_type = item.get('model_type', 'Unknown')
            display_name = f"{name} ({sid}) [{m_type}]"
            index[display_name] = sid
        return index
    except Exception as e:
        print(f"Error fetching shapes index: {e}")
        raise


def fetch_shape_data(specimen_id, progress_callback=None):
    """
    Fetches detailed anatomical data for a specific specimen.
    Supports local caching and large file streaming.
    Returns a dict compatible with ShapeViewerComboApp:
    {'data': json_dict, 'model_type': 'DATASTORE'}
    """
    cache_path = CACHE_DIR / f"{specimen_id}.json"

    # Check cache first
    if cache_path.exists():
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'data': data,
                    'model_type': 'DATASTORE',
                    'source': f"Cache: {specimen_id}"
                }
        except Exception as e:
            print(f"Cache read error for {specimen_id}, re-fetching: {e}")

    # Fetch from web
    url = f"{BASE_URL}/specimen/{specimen_id}/data"
    try:
        # Use streaming for large files
        response = requests.get(url, stream=True, timeout=300)  # 5 min timeout
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        chunks = []

        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB
            if chunk:
                chunks.append(chunk)
                downloaded += len(chunk)
                if progress_callback:
                    progress_callback(downloaded, total_size)

        # Merge and parse
        full_content = b"".join(chunks).decode('utf-8')
        data = json.loads(full_content)

        # Save to cache
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Cache write error: {e}")

        return {
            'data': data,
            'model_type': 'DATASTORE',
            'source': f"Web: {specimen_id}"
        }
    except Exception as e:
        print(f"Error fetching specimen data {specimen_id}: {e}")
        raise

from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import urlopen
import json
import shutil

BUCKET = "waymo_open_dataset_motion_v_1_3_1"
PREFIX = "uncompressed/scenario/validation/"
LIMIT = 5

output_dir = Path("data/raw/waymo_open_dataset/motion/validation")
output_dir.mkdir(parents=True, exist_ok=True)

list_url = (
    f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o?"
    + urlencode({
        "prefix": PREFIX,
        "maxResults": LIMIT,
    })
)

print("Finding Waymo files...")

with urlopen(list_url, timeout=60) as response:
    payload = json.load(response)

items = [
    item for item in payload.get("items", [])
    if not item["name"].endswith("/")
]

print(f"Found {len(items)} files.")

for number, item in enumerate(items[:LIMIT], start=1):
    object_name = item["name"]
    filename = Path(object_name).name
    destination = output_dir / filename

    download_url = (
        f"https://storage.googleapis.com/{BUCKET}/"
        f"{quote(object_name, safe='/')}"
    )

    print(f"[{number}/{min(LIMIT, len(items))}] Downloading {filename}...")

    with urlopen(download_url, timeout=300) as source:
        with destination.open("wb") as target:
            shutil.copyfileobj(source, target)

    size_mb = destination.stat().st_size / 1_000_000
    print(f"Saved {size_mb:.1f} MB")

print(f"Done! Files are in: {output_dir.resolve()}")

#!/usr/bin/env python3
import json
import re
import time
from pathlib import Path
from urllib.request import urlretrieve, urlopen
from urllib.error import HTTPError

MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
IMG_DIR = Path("images")

def get_manifest():
    with urlopen(MANIFEST_URL) as resp:
        return json.load(resp)

def parse_folio(label):
    match = re.match(r'^(\d+)([rv])$', label.strip())
    if match:
        return int(match.group(1)), match.group(2)
    return None, None

def is_herbal_folio(num, side):
    if num is None:
        return False
    return (1 <= num <= 66) or (90 <= num <= 113)

def get_image_url(canvas, size="1000,"):
    items = canvas.get('items', [])
    if not items:
        return None
    page = items[0].get('items', [])
    if not page:
        return None
    body = page[0].get('body', {})
    full_url = body.get('id')
    if full_url:
        return full_url.replace('/full/full/', f'/full/{size}/')
    return None

def download_images(max_count=None):
    IMG_DIR.mkdir(exist_ok=True)
    
    print("Fetching manifest...")
    manifest = get_manifest()
    
    canvases = manifest.get('items', [])
    print(f"Found {len(canvases)} total canvases")
    
    downloaded = 0
    herbal_pages = []
    
    for canvas in canvases:
        label_info = canvas.get('label', {})
        labels = label_info.get('none', [])
        if not labels:
            continue
        
        label = labels[0]
        num, side = parse_folio(label)
        
        if not is_herbal_folio(num, side):
            continue
        
        folio = f"{num}{side}"
        img_path = IMG_DIR / f"f{folio}.jpg"
        
        if img_path.exists():
            print(f"  {folio}: already exists")
            herbal_pages.append(folio)
            continue
        
        img_url = get_image_url(canvas)
        if not img_url:
            print(f"  {folio}: no image URL found")
            continue
        
        try:
            print(f"  Downloading {folio}... ", end="", flush=True)
            urlretrieve(img_url, img_path)
            print("OK")
            herbal_pages.append(folio)
            downloaded += 1
            time.sleep(0.5)
            
            if max_count and downloaded >= max_count:
                break
        except HTTPError as e:
            print(f"FAILED: {e}")
    
    print(f"\nDownloaded {downloaded} new images")
    print(f"Total herbal pages: {len(herbal_pages)}")
    return herbal_pages

if __name__ == '__main__':
    pages = download_images()
    print("\nHerbal section pages downloaded:")
    for p in sorted(pages, key=lambda x: (int(x[:-1]), x[-1])):
        print(f"  {p}")





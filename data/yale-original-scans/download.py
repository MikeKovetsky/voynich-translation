#!/usr/bin/env python3
"""
IIIF bulk downloader (works with Yale / any IIIF Presentation v2 or v3 manifest)

Usage:
  python download_iiif.py "PASTE_MANIFEST_URL_HERE" --out voynich_pages

Notes:
- Downloads the "full" image for each canvas/page.
- Skips files that already exist (resume-friendly).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

import requests


def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[\/\\:*?\"<>|]+", "_", name)
    name = re.sub(r"\s+", " ", name)
    return name[:180] if len(name) > 180 else name


def fetch_json(url: str, timeout_seconds: int = 60) -> Dict[str, Any]:
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers, timeout=timeout_seconds)
    response.raise_for_status()
    return response.json()


def get_label_text(label_field: Any) -> str:
    # IIIF v2: "label": "f1r"
    if isinstance(label_field, str):
        return label_field

    # IIIF v3: "label": {"en": ["f1r"]} (or other lang)
    if isinstance(label_field, dict):
        for _lang, values in label_field.items():
            if isinstance(values, list) and values:
                return str(values[0])
    return ""


def iter_canvases(manifest: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    # IIIF v2: sequences[0].canvases
    if "sequences" in manifest:
        for sequence in manifest.get("sequences", []):
            for canvas in sequence.get("canvases", []):
                yield canvas
        return

    # IIIF v3: items (manifest) -> canvases
    for canvas in manifest.get("items", []):
        yield canvas


def extract_image_service_id_from_canvas(canvas: Dict[str, Any]) -> Optional[str]:
    """
    Returns IIIF Image service base ID when possible.
    We'll build: {service_id}/full/full/0/default.jpg
    """
    # IIIF v2: canvas.images[0].resource.service["@id"] or ["@id"]
    images = canvas.get("images")
    if isinstance(images, list) and images:
        resource = images[0].get("resource", {})
        service = resource.get("service", {})
        if isinstance(service, dict):
            return service.get("@id") or service.get("id")

    # IIIF v3: canvas.items[0].items[0].body.service[0].id
    items = canvas.get("items")
    if isinstance(items, list) and items:
        annotation_page = items[0]
        annotations = annotation_page.get("items", [])
        if isinstance(annotations, list) and annotations:
            body = annotations[0].get("body", {})
            service = body.get("service")
            if isinstance(service, list) and service:
                service0 = service[0]
                if isinstance(service0, dict):
                    return service0.get("id") or service0.get("@id")
            if isinstance(service, dict):
                return service.get("id") or service.get("@id")

    return None


def guess_extension_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for extension in [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".jp2", ".webp"]:
        if path.endswith(extension):
            return extension.lstrip(".")
    return "jpg"


def download_file(url: str, output_path: Path, sleep_seconds: float = 0.15) -> None:
    if output_path.exists() and output_path.stat().st_size > 0:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        tmp_path = output_path.with_suffix(output_path.suffix + ".part")
        with open(tmp_path, "wb") as file_handle:
            for chunk in response.iter_content(chunk_size=1024 * 512):
                if chunk:
                    file_handle.write(chunk)
        tmp_path.replace(output_path)

    time.sleep(sleep_seconds)


def main(manifest_url: str, output_folder: str, delay: float = 0.15) -> None:
    output_folder = Path(output_folder)
    manifest = fetch_json(manifest_url)

    canvases = list(iter_canvases(manifest))
    if not canvases:
        raise SystemExit("No canvases found. Are you sure this is a IIIF manifest URL?")

    print(f"Found {len(canvases)} canvases")

    for index, canvas in enumerate(canvases, start=1):
        label = get_label_text(canvas.get("label")) or canvas.get("id") or canvas.get("@id") or f"page_{index:03d}"
        safe_label = sanitize_filename(label)

        service_id = extract_image_service_id_from_canvas(canvas)
        if service_id:
            image_url = f"{service_id.rstrip('/')}/full/full/0/default.jpg"
            file_extension = "jpg"
        else:
            # Fallback: sometimes body/resource is a direct image URL
            direct_url = None
            # v2 direct: canvas.images[0].resource["@id"]
            images = canvas.get("images")
            if isinstance(images, list) and images:
                direct_url = images[0].get("resource", {}).get("@id")

            # v3 direct: canvas.items[0].items[0].body.id
            if not direct_url:
                items = canvas.get("items")
                if isinstance(items, list) and items:
                    annotations = items[0].get("items", [])
                    if isinstance(annotations, list) and annotations:
                        direct_url = annotations[0].get("body", {}).get("id")

            if not direct_url:
                print(f"[{index:03d}] SKIP (no image URL): {label}")
                continue

            image_url = direct_url
            file_extension = guess_extension_from_url(image_url)

        output_path = output_folder / f"{index:03d}_{safe_label}.{file_extension}"

        try:
            download_file(image_url, output_path, sleep_seconds=delay)
            print(f"[{index:03d}] OK  {output_path.name}")
        except Exception as exc:
            print(f"[{index:03d}] FAIL {label} -> {exc}")

    print("Done.")


if __name__ == "__main__":
    main(
        manifest_url="https://collections.library.yale.edu/manifests/2002046",
        output_folder="/Users/mike/repos/voynych2/data/yale-original-scans/scans",
        delay=0.15,
    )

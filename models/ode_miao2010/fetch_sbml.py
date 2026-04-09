#!/usr/bin/env python3
"""
Download BIOMD0000000546 (Miao et al. 2010 — Influenza A dynamics) from BioModels.

Usage:
    python fetch_sbml.py
    → writes BIOMD0000000546.xml in the same directory
"""

import urllib.request
import os

MODEL_ID = "BIOMD0000000546"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), f"{MODEL_ID}.xml")

# BioModels REST API endpoint
URL = f"https://www.ebi.ac.uk/biomodels/{MODEL_ID}/download?filename={MODEL_ID}_url.xml"


def fetch():
    if os.path.exists(OUTPUT_FILE):
        print(f"[fetch_sbml] {OUTPUT_FILE} already exists, skipping download.")
        return
    print(f"[fetch_sbml] Downloading {MODEL_ID} from BioModels…")
    urllib.request.urlretrieve(URL, OUTPUT_FILE)
    size = os.path.getsize(OUTPUT_FILE)
    print(f"[fetch_sbml] Saved {OUTPUT_FILE} ({size} bytes)")


if __name__ == "__main__":
    fetch()

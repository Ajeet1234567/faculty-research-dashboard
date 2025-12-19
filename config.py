"""
Configuration settings for CUSB Research Analyzer
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, "data")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

# Data files
FACULTY_FILE = os.path.join(DATA_DIR, "faculty.json")
PUBLICATIONS_FILE = os.path.join(DATA_DIR, "publications.json")
CACHE_FILE = os.path.join(DATA_DIR, "cache.json")

# Scholarly settings
RATE_LIMIT_DELAY = 2  # Seconds between requests
MAX_RETRIES = 3
TIMEOUT = 30

# Application settings
APP_TITLE = "CUSB CS Faculty Research Analyzer"
APP_ICON = ""
INSTITUTION_NAME = "Central University of South Bihar, Gaya"
DEPARTMENT_NAME = "Department of Computer Science"

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

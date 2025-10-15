import os
import sys

# This file runs BEFORE any test imports
# Remove PostgreSQL connection and force SQLite for all tests
if 'DATABASE_URL' in os.environ:
    del os.environ['DATABASE_URL']

# Ensure backend is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

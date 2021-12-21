import sys

# Load in the fixtures from common/sharedfixtures.py
sys.path.append("../common")

pytest_plugins = [
    "sharedfixtures",
]

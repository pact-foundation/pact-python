# Load in the fixtures from common/sharedfixtures.py
import sys

sys.path.append("../common")

pytest_plugins = [
    "sharedfixtures",
]

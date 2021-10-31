import logging

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.logger import logger

fakedb = {}  # Use a simple dict to represent a database

logger.setLevel(logging.DEBUG)
router = APIRouter()
app = FastAPI()


@app.get("/users/{name}")
def get_user_by_name(name: str):
    """Handle requests to retrieve a single user from the simulated database.

    :param name: Name of the user to "search for"
    :return: The user data if found, HTTP 404 if not
    """
    user_data = fakedb.get(name)
    if not user_data:
        logger.error(f"GET user for: '{name}', HTTP 404 not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.error(f"GET user for: '{name}', returning: {user_data}")
    return user_data

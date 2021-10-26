from fastapi import FastAPI, HTTPException, APIRouter

fakedb = {}  # Use a simple dict to represent a database
router = APIRouter()
app = FastAPI()


@app.get("/users/{name}")
def get_user_by_name(name: str):
    user_data = fakedb.get(name)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    return user_data

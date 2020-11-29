from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter()

fakedb = {}
app = FastAPI()


class TestUser(BaseModel):
    name: str  # noqa: E999


@router.get('/users/{name}')
def get_user_by_name(name: str):
    user_data = fakedb.get(name)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    return user_data

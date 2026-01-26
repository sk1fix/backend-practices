from fastapi import Depends, APIRouter

app = APIRouter(tags=["Auth route"])

@app.post('/auth/register', summary="Register route", tags=["Auth route"])
def register():
    pass
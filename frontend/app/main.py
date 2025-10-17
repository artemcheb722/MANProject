from fastapi import FastAPI

from app_factory import get_application

app = FastAPI(root_path="/api", root_path_in_servers=True)


@app.get("/")
async def index():
    return {"status2332": 200}


app = get_application()

from fastapi import FastAPI

from applications.auth.router import router_auth
from applications.Projects.router import router_projects
from applications.users.router import router_users
from settings import settings


def get_application() -> FastAPI:
    app = FastAPI(root_path="/api", root_path_in_servers=True, debug=settings.DEBUG)

    app.include_router(router_users, prefix="/users", tags=["Users"])
    app.include_router(router_projects, prefix="/projects", tags=["Projects"])
    app.include_router(router_auth, prefix="/auth", tags=["Auth"])
    return app

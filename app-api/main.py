from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from .auth import auth_router

api_root_path = "/api"
auth_route_path = "/auth"

app = FastAPI()

api = FastAPI(root_path=api_root_path)
auth = FastAPI(root_path=auth_route_path)
app.mount(api.root_path, api)
app.mount(auth.root_path, auth)
auth.include_router(auth_router)

app.add_middleware(SessionMiddleware,secret_key="your-secret-key")

@api.get("/hello")
async def hello():
    return {"message": "Hello World"}

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return FileResponse(static_dir / "index.html")
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

api_root_path = "/api"

app = FastAPI()

api = FastAPI(root_path=api_root_path)
app.mount(api_root_path, api)

@api.get("/hello")
async def hello():
    return {"message": "Hello World"}

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return FileResponse(static_dir / "index.html")
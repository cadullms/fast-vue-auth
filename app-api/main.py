from pathlib import Path
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from auth import auth_router, protected_api, protected_endpoint

api_root_path = "/api"
auth_route_path = "/auth"
static_dir = Path(__file__).resolve().parent / "static"
origins = ["http://127.0.0.1:5173"]

app = FastAPI()
api = FastAPI(root_path=api_root_path, dependencies=[Depends(protected_api)])
auth = FastAPI(root_path=auth_route_path)
root = FastAPI(root_path="", dependencies=[Depends(protected_endpoint)])
static_router = APIRouter()

@static_router.get("/{path:path}")
async def static_files(request: Request, path: str):
    file_path = static_dir / path
    # Normalize the path to prevent directory traversal attacks
    file_path = file_path.resolve()
    # Check if the file exists and is not outside the static directory
    if not file_path.is_relative_to(static_dir):
        raise HTTPException(status_code=404, detail="File not found")
    if file_path.exists():
        if file_path.is_file():
            return FileResponse(file_path)
        if file_path.is_dir():
            # If the path is a directory, check for an index.html file
            index_file = file_path / "index.html"
            if index_file.exists() and index_file.is_file():
                return FileResponse(index_file)
    return FileResponse(static_dir / "index.html")


app.mount(api.root_path, api)
app.mount(auth.root_path, auth)
auth.include_router(auth_router)
root.include_router(static_router)
app.mount(root.root_path, root)


app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/hello")
async def hello():
    return {"message": "Hello World"}


    

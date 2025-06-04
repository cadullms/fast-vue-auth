from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from .config import AUTH_SETTINGS

oauth = OAuth()
oauth.register("auth0",
    client_id=AUTH_SETTINGS.client_id,
    client_secret=AUTH_SETTINGS.client_secret,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{AUTH_SETTINGS.domain}/.well-known/openid-configuration'
)

auth_router = APIRouter()

@auth_router.get("/login")
async def login(request: Request):
    if 'id_token' not in request.session:
        print("User not logged in, redirecting...")
        return await oauth.auth0.authorize_redirect(
            request,
            redirect_uri=request.url_for("callback")
        )
    redirect_to = "index"
    print(f"User already logged in. Redirecting to [{redirect_to}]...")
    return "user already logged in"

@auth_router.get("/callback")
async def callback(request: Request):
    token = await oauth.auth0.authorize_access_token(request)
    # Store `id_token`, and `userinfo` in session
    request.session['id_token'] = token['id_token']
    request.session['userinfo'] = token['userinfo']
    # 👆 new code
    return RedirectResponse(url="/")

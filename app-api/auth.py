import logging
from urllib.parse import quote_plus, urlencode
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from config import AUTH_SETTINGS


oauth = OAuth()
for auth_option in AUTH_SETTINGS.options.values():
    oauth.register(
        auth_option.id,
        client_id=auth_option.client_id,
        client_secret=auth_option.client_secret,
        server_metadata_url=f"https://{auth_option.domain}/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid profile email",
        }
    )

_logger = logging.getLogger("uvicorn")


async def _get_logout_endpoint(auth_option_id: str, request: Request) -> str:
    auth_option = AUTH_SETTINGS.options[auth_option_id]
    oauth_client = oauth.create_client(auth_option_id)
    metadata = await oauth_client.load_server_metadata()
    base_url = metadata.get("end_session_endpoint")
    return_to = request.url_for("manage")
    _logger.info(
        f"Log out redirect. base_url: {base_url}, return_to: {return_to}, auth_option: {auth_option_id}, auth_option_type: {auth_option.type}")
    if auth_option.type == "auth0":
        return f"{base_url}?{urlencode(
            {
                "returnTo": return_to,
                "client_id": auth_option.client_id,
            },
            quote_via=quote_plus,
        )}"
    if auth_option.type == "entra-id":
        return f"{base_url}?{urlencode(
            {
                "post_logout_redirect_uri": return_to,
            },
            quote_via=quote_plus,
        )}"
    return base_url

auth_router = APIRouter()


@auth_router.get("/login/{auth_option_id}")
async def login(auth_option_id: str, request: Request):
    if "id_token" not in request.session:
        request.session["auth_option_id"] = auth_option_id
        auth_client = oauth.create_client(auth_option_id)
        if not auth_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Auth option {auth_option_id} not found",
            )
        _logger.info(f"User not logged in, redirecting with {auth_option_id}...")
        return await auth_client.authorize_redirect(
            request, redirect_uri=request.url_for("callback")
        )
    return "user already logged in"


@auth_router.get("/callback")
async def callback(request: Request):
    auth_option_id = request.session.get("auth_option_id")
    token = await oauth.create_client(auth_option_id).authorize_access_token(request)
    request.session["id_token"] = token["id_token"]
    request.session["userinfo"] = token["userinfo"]
    return RedirectResponse(url=request.url_for("manage"))


@auth_router.get("/logout/{auth_option_id}")
async def logout(auth_option_id: str, request: Request):
    logout_url = await _get_logout_endpoint(auth_option_id, request)
    _logger.info(f"logout_url: {logout_url}")
    response = RedirectResponse(
        url=logout_url
    )
    request.session.clear()
    return response


auth_manager_templates = Jinja2Templates(directory="auth_manager_templates")


@auth_router.get("/manage")
def manage(request: Request):
    return auth_manager_templates.TemplateResponse(
        "manage.html",
        {
            "request": request,
            "id_token": request.session["id_token"]
            if "id_token" in request.session
            else None,
            "auth_option_id": request.session["auth_option_id"]
            if "auth_option_id" in request.session
            else None,
            "auth_options": AUTH_SETTINGS.options.values(),
            "userinfo": request.session["userinfo"]
            if "userinfo" in request.session
            else None,
        },
    )


def protected_endpoint(request: Request):
    _logger.info("protected_endpoint called")
    if "id_token" not in request.session:
        # this will redirect people to the login after if they are not logged in
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            detail="Not authorized",
            headers={"Location": "auth/manage"},
        )


def protected_api(request: Request):
    _logger.info("protected_api called")
    if "id_token" not in request.session:
        # this will redirect people to the login after if they are not logged in
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

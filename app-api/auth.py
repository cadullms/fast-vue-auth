from urllib.parse import quote_plus, urlencode
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from config import AUTH_SETTINGS

oauth = OAuth()
oauth.register(
    "auth0",
    client_id=AUTH_SETTINGS.client_id,
    client_secret=AUTH_SETTINGS.client_secret,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{AUTH_SETTINGS.domain}/.well-known/openid-configuration",
)

# https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc#find-your-apps-openid-configuration-document-uri

auth_router = APIRouter()


@auth_router.get("/login")
async def login(request: Request):
    if "id_token" not in request.session:
        print("User not logged in, redirecting...")
        return await oauth.auth0.authorize_redirect(
            request, redirect_uri=request.url_for("callback")
        )
    print("User already logged in...")
    return "user already logged in"


@auth_router.get("/logout")
async def logout(request: Request):
    return_to = request.url_for("manage")
    print(f"Logging out user, redirecting to {return_to}")
    response = RedirectResponse(
        url=f"""https://{AUTH_SETTINGS.domain}/v2/logout?
            {
            urlencode(
                {
                    "returnTo": return_to,
                    "client_id": AUTH_SETTINGS.client_id,
                },
                quote_via=quote_plus,
            )
        }"""
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
        },
    )


@auth_router.get("/callback")
async def callback(request: Request):
    token = await oauth.auth0.authorize_access_token(request)
    request.session["id_token"] = token["id_token"]
    return RedirectResponse(url=request.url_for("manage"))


def protected_endpoint(request: Request):
    print("protected_endpoint called")
    if "id_token" not in request.session:
        # this will redirect people to the login after if they are not logged in
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            detail="Not authorized",
            headers={"Location": "auth/manage"},
        )


def protected_api(request: Request):
    print("protected_api called")
    if "id_token" not in request.session:
        # this will redirect people to the login after if they are not logged in
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

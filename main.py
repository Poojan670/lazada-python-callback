import json
import logging
from typing import Any

import emails
from fastapi import FastAPI, HTTPException, Query
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

import lazop
from src.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/re-docs"
)

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


def send_email(
        *,
        email_to: str,
        subject: str = "",
        html_content: str = "",
) -> None:
    try:
        assert settings.emails_enabled, "no provided configuration for email variables"
        content = f"From: {settings.EMAILS_FROM_NAME}\r\nTo: {email_to}\r\nSubject: {subject}\r\n\r\n{html_content}"
        message = emails.Message(
            subject=subject,
            html=content,
            mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
        )
        smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
        if settings.SMTP_TLS:
            smtp_options["tls"] = True
        elif settings.SMTP_SSL:
            smtp_options["ssl"] = True
        if settings.SMTP_USER:
            smtp_options["user"] = settings.SMTP_USER
        if settings.SMTP_PASSWORD:
            smtp_options["password"] = settings.SMTP_PASSWORD
        response = message.send(to=email_to, smtp=smtp_options)
        logging.info(f"send email result: {response}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to send email: {str(e)}')


async def get_access_token(code: str) -> Any:
    # Exchange authorization code for access token
    try:
        client = lazop.LazopClient(settings.LAZADA_ROOT_URL, settings.LAZADA_APP_KEY, settings.LAZADA_APP_SECRET)
        request = lazop.LazopRequest('/auth/token/create')
        request.add_api_param('code', code)
        response = client.execute(request)
        logging.info(response.type)
        logging.info(response.body)
        send_email(email_to=settings.EMAIL_TO, subject="Lazada Token Created via Lazada API",
                   html_content=json.dumps(response.body, indent=1, ensure_ascii=False))
        return {
            "msg": "Email Sent Successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=str(e))


@app.post('/callback-url', status_code=201)
async def callback(code: str = Query(...)):
    if not code or code == "":
        raise HTTPException(status_code=400, detail="Missing code")
    return await get_access_token(code)


@app.get('/callback-url', status_code=201)
async def callback(code: str = Query(...)):
    if not code or code == "":
        raise HTTPException(status_code=400, detail="Missing code")
    return await get_access_token(code)


@app.get("/")
async def redirect_to_url():
    target_url = f"https://auth.lazada.com/oauth/authorize?response_type=code&force_auth=true&redirect_uri={settings.LAZADA_CALLBACK_URI}&client_id={settings.LAZADA_APP_KEY}"

    # Create a RedirectResponse with the target URL
    response = RedirectResponse(url=target_url)

    return response

if __name__ == '__main__':
    import uvicorn

    logger.info("Application started....")

    uvicorn.run("main:app",
                host=settings.SERVER_HOST,
                port=settings.SERVER_PORT,
                log_level="debug",
                reload=True)

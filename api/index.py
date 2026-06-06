from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import candidates, interviews, jobs, offers, pipeline
from .webhooks import calendly as calendly_webhook
from .webhooks import greenhouse as greenhouse_webhook

app = FastAPI(title="HR Recruiting Pipeline API", version="2.0.0")

app_origin = settings.VERCEL_URL
if app_origin and not app_origin.startswith(("http://", "https://")):
    app_origin = f"https://{app_origin}"
allow_origins = ["*"] if "localhost" in app_origin else [app_origin]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api/v1")
app.include_router(candidates.router, prefix="/api/v1")
app.include_router(pipeline.router, prefix="/api/v1")
app.include_router(interviews.router, prefix="/api/v1")
app.include_router(offers.router, prefix="/api/v1")
app.include_router(calendly_webhook.router, prefix="/api/webhooks")
app.include_router(greenhouse_webhook.router, prefix="/api/webhooks")


@app.get("/health")
async def health():
    return {"status": "ok"}

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

import crud
from config import Settings, get_settings
from database import Base, SessionLocal, engine
from routers import health, items

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    crud.seed_items(db)

settings = get_settings()

# The title shows at the top of /docs. debug=True makes unhandled errors
# return a traceback page instead of a bare "Internal Server Error".
app = FastAPI(title=settings.app_name, debug=settings.debug)

# Which browser origins may call this API now comes from settings, so
# production can allow its real domain without a code change.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router)
app.include_router(health.router)


# Safe, non-secret facts about the running app. Never return the
# password, the API key or the full database URL from an endpoint.
@app.get("/info", tags=["meta"])
def info(settings: Settings = Depends(get_settings)):
    return {"app_name": settings.app_name, "debug": settings.debug}

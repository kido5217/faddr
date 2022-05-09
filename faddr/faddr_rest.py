"""REST API entry point."""

import sys

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from faddr.database import Database
from faddr.exceptions import FaddrDatabaseDirError
from faddr.logging import logger
from faddr.results import NetworkResult
from faddr.schemas import APINetworkQueryBody
from faddr.settings import FaddrSettings

# Load settings
settings = FaddrSettings()


# Connect to database
logger.info("Connecting to database and creating new revision")
try:
    database = Database(**settings.database.dict())
except FaddrDatabaseDirError:
    logger.exception("Failed to open database")
    sys.exit(1)


# REST API app
app = FastAPI()


@app.exception_handler(RequestValidationError)
# pylint: disable=unused-argument
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return validatrion error to user."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


# API v0
api_v0 = APIRouter()


@api_v0.get("/")
async def get_network(network: str):
    """Find network"""
    try:
        query = APINetworkQueryBody.parse_obj({"networks": [network]})
    except ValidationError as err:
        raise HTTPException(status_code=422, detail=err.errors()) from None
    result = NetworkResult(database.find_networks(query.networks))
    return result.data


@api_v0.post("/")
async def post_networks(query: APINetworkQueryBody):
    """Find networks"""
    result = NetworkResult(database.find_networks(query.networks))
    return result.data


app.include_router(api_v0, prefix="/api/v0")


def main():
    """Start gunicorn server."""
    uvicorn.run(
        "faddr.faddr_rest:app",
        host=settings.api.host,
        port=settings.api.port,
        workers=settings.api.workers,
        log_level=settings.log_level.lower(),
    )

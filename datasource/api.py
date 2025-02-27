import asyncio
import logging
import os
import random
from datetime import date, datetime
from typing import List

import arrow
import coloredlogs
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing_extensions import Annotated

coloredlogs.install(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mock Data Source HTTP API",
    description=(
        "A mock HTTP API that serves as an example data source for the Data Cellar connector example"
    ),
    version="0.0.1",
    contact={
        "name": "Andrés García Mangas",
        "url": "https://github.com/agmangas",
        "email": "andres.garcia@fundacionctic.org",
    },
)

API_KEY_HEADER_NAME = "X-API-Key"
API_KEY_ENV_VAR = "BACKEND_API_KEY"

header_scheme = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


def authenticate_api_key(key: str = Depends(header_scheme)):
    """
    Authenticates API requests by validating the API key provided in the request header.
    Skips authentication if the API key is not set in the environment variable.
    """

    expected_key = os.getenv(API_KEY_ENV_VAR)

    if expected_key and expected_key != key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


APIKeyAuthDep = Annotated[str, Depends(authenticate_api_key)]


class ElectricityConsumptionPredictionRequest(BaseModel):
    date_from: datetime
    date_to: datetime
    location: str


class ElectricityConsumptionSample(BaseModel):
    date: datetime
    value: int


class ElectrictyConsumptionData(BaseModel):
    location: str
    results: List[ElectricityConsumptionSample]


@app.post(
    "/consumption/prediction",
    tags=["Electricity consumption"],
)
async def run_consumption_prediction(
    api_key: APIKeyAuthDep, body: ElectricityConsumptionPredictionRequest
) -> ElectrictyConsumptionData:
    """Run the ML model for prediction of electricity consumption for the given time period.
    This is a mock implementation that generates random values for demonstration purposes.
    """

    await asyncio.sleep(random.random())

    arrow_from = arrow.get(body.date_from)
    arrow_to = arrow.get(body.date_to)

    results = [
        {"date": item.isoformat(), "value": random.randint(0, 100)}
        for item in arrow.Arrow.range(
            "hour",
            arrow_from.clone().floor("minute"),
            arrow_to.clone().floor("minute"),
        )
    ]

    return ElectrictyConsumptionData(location=body.location, results=results)


@app.get(
    "/consumption",
    tags=["Electricity consumption"],
)
async def get_consumption_data(
    api_key: APIKeyAuthDep, location: str = "Asturias", day: date = None
) -> ElectrictyConsumptionData:
    """Fetch the historical time series of electricity consumption for a given day.
    This is a mock implementation that generates random values for demonstration purposes.
    """

    await asyncio.sleep(random.random())

    arrow_day = arrow.get(day) if day else arrow.utcnow().shift(days=-1).floor("day")

    results = [
        {"date": item.isoformat(), "value": random.randint(0, 100)}
        for item in arrow.Arrow.range(
            "hour", arrow_day.clone().floor("day"), arrow_day.clone().ceil("day")
        )
    ]

    return ElectrictyConsumptionData(location=location, results=results)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    headers = request.headers
    _logger.info("Request headers:\n%s", headers)
    response = await call_next(request)
    return response

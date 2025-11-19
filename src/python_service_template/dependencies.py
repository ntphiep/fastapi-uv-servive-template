import typing as t
from functools import lru_cache

from fastapi import Depends

from python_service_template.domain.coffee.repository import CoffeeClient
from python_service_template.domain.coffee.service import CoffeeService, SimpleCoffeeService
from python_service_template.infrastructure.client.coffee import AsyncCoffeeClient
from python_service_template.infrastructure.health import (
    DetailedHealthChecker,
    SimpleHealthChecker,
)
from python_service_template.settings import Settings


@lru_cache
def settings() -> Settings:
    return Settings()


def coffee_client(settings: t.Annotated[Settings, Depends(settings)]) -> CoffeeClient:
    return AsyncCoffeeClient(base_url=settings.coffee_api.host)


def coffee_service(
    client: t.Annotated[CoffeeClient, Depends(coffee_client)],
) -> CoffeeService:
    return SimpleCoffeeService(client=client)


def detailed_health_checker(
    coffee_client: t.Annotated[CoffeeClient, Depends(coffee_client)],
    settings: t.Annotated[Settings, Depends(settings)],
) -> DetailedHealthChecker:
    return DetailedHealthChecker(coffee_client, settings.app_version, settings.git_commit_sha)


def simple_health_checker(
    coffee_client: t.Annotated[CoffeeClient, Depends(coffee_client)],
    settings: t.Annotated[Settings, Depends(settings)],
) -> SimpleHealthChecker:
    return SimpleHealthChecker(coffee_client, settings.app_version, settings.git_commit_sha)

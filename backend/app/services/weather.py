from datetime import datetime
from typing import Protocol

import httpx

from app.schemas.intelligence import WeatherData, WeatherResponse


class WeatherProvider(Protocol):
    async def get_current_weather(self, latitude: float, longitude: float) -> WeatherResponse:
        ...


class OpenMeteoWeatherProvider:
    provider_name = "open-meteo"
    base_url = "https://api.open-meteo.com/v1/forecast"

    async def get_current_weather(self, latitude: float, longitude: float) -> WeatherResponse:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,rain",
            "timezone": "auto",
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            return self._unavailable(latitude, longitude, f"Weather provider unavailable: {exc}")

        try:
            data = response.json()
            current = data.get("current") or {}
            if "temperature_2m" not in current:
                return self._unavailable(latitude, longitude, "Weather provider response did not include temperature data.")

            timestamp = None
            if current.get("time"):
                timestamp = datetime.fromisoformat(str(current["time"]).replace("Z", "+00:00"))

            weather = WeatherData(
                temperature=current.get("temperature_2m"),
                humidity=current.get("relative_humidity_2m"),
                precipitation=current.get("precipitation"),
                rainfall=current.get("rain"),
                forecast_window="current",
                latitude=float(data.get("latitude", latitude)),
                longitude=float(data.get("longitude", longitude)),
                timestamp=timestamp,
                provider=self.provider_name,
                provider_status="available",
            )
        except (TypeError, ValueError) as exc:
            return self._unavailable(latitude, longitude, f"Weather provider response was invalid: {exc}")

        return WeatherResponse(
            available=True,
            weather=weather,
            provider=self.provider_name,
            provider_status="available",
        )

    def _unavailable(self, latitude: float, longitude: float, warning: str) -> WeatherResponse:
        return WeatherResponse(
            available=False,
            weather=None,
            provider=self.provider_name,
            provider_status="unavailable",
            warning=warning,
        )


def get_weather_provider() -> WeatherProvider:
    return OpenMeteoWeatherProvider()

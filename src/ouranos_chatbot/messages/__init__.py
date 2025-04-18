from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from ouranos import sdk


script_folder = Path().absolute().parents[0]
template_folder = script_folder/"templates"


loader = FileSystemLoader(template_folder)
environment = Environment(
    loader=loader, lstrip_blocks=True, trim_blocks=True, autoescape=True
)


def replace_underscore(s: str, replacement: str = " ") -> str:
    return s.replace("_", replacement)


environment.filters["replace_underscore"] = replace_underscore


def render_template(rel_path, **context) -> str:
    return environment.get_template(rel_path).render(context)


async def ecosystem_summary(
        session: AsyncSession,
        ecosystems: str | list[str] | None = None
) -> str:
    ecosystem_objs = await sdk.ecosystem.get_multiple(session, ecosystems)
    ecosystems = [
        sdk.ecosystem.get_info(session, ecosystem)
        for ecosystem in ecosystem_objs
    ]
    if ecosystems:
        return render_template(
            "ecosystem.html", ecosystems=ecosystems
        )
    return "No ecosystem found"

"""
def weather(currently: bool = True, forecast: bool = True, **kwargs) -> str:
    weather = {}

    if currently:
        weather["currently"] = web_server.weather.get_currently()

    if forecast:
        weather["hourly"] = web_server.weather.summarize_forecast(
            web_server.weather.get_hourly(12)
        )["forecast"]

        tomorrow = web_server.weather.get_daily(1)["forecast"][0]
        sunrise = datetime.fromtimestamp(tomorrow["sunriseTime"])
        tomorrow["sunriseTime"] = sunrise.strftime("%H:%M")
        sunset = datetime.fromtimestamp(tomorrow["sunsetTime"])
        tomorrow["sunsetTime"] = sunset.strftime("%H:%M")
        length = (sunset - sunrise).seconds
        hours = length // 3600
        minutes = (length % 3600) // 60
        tomorrow["dayLength"] = f"{hours}:{minutes}"
        weather["tomorrow"] = tomorrow

    return render_template(
        "weather.html", weather=weather
    )


def light_info(*ecosystems, session, **kwargs):
    ecosystem_qo = web_server.ecosystem.get_multiple(
        session=session, ecosystems=ecosystems)
    light_info = web_server.ecosystem.get_light_info(ecosystem_qo)
    message = render_template(
        "lights.html", light_info=light_info, **kwargs
    )
    return message


def current_sensors_info(*ecosystems, session):
    raw_sensors = web_server.ecosystems.get_current_sensors_data_old(
        *ecosystems, session=session)
    sensors = web_server.ecosystems.summarize_sensors_data(raw_sensors)
    if sensors:
        return web_server.messages.render_template(
            "sensors.html", sensors=sensors, units=units)
    return "There is currently no sensors connected"


def recap_sensors_info(*ecosystems, session,
                       days_ago: int = 7):
    window_start = datetime.now()-timedelta(days=days_ago)
    ecosystem_qo = web_server.ecosystem.get_multiple(
        session=session, ecosystems=ecosystems)
    time_window = web_server.utils.create_time_window(start=window_start)
    raw_sensors = web_server.ecosystems._get_ecosystem_historic_sensors_data(
        session, ecosystem_qo, time_window=time_window
    )
    sensors = {e: raw_sensors[e] for e in raw_sensors
               if raw_sensors[e]["data"]}
    avg_sensors = web_server.ecosystems.average_historic_sensors_data(sensors)
    sum_sensors = web_server.ecosystems.summarize_sensors_data(avg_sensors)
    return web_server.messages.render_template(
        "sensors.html", sensors=sum_sensors, units=units,
        timedelta=days_ago)
"""
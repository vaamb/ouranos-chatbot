from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


# Template rendering
template_folder = Path(__file__).absolute().parent

loader = FileSystemLoader(template_folder)
environment = Environment(
    loader=loader, lstrip_blocks=True, trim_blocks=True, autoescape=True, enable_async=True)


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y %H:%M")


def get_names(sequence: list[dict]) -> list[str]:
    return [item["name"] for item in sequence]


environment.filters["format_datetime"] = format_datetime
environment.filters["get_names"] = get_names


async def render_template(rel_path, **context) -> str:
    template = await environment.get_template(f"{rel_path}.html").render_async(context)
    return template.strip()

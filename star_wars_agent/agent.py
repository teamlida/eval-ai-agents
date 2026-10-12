import logging

import requests
from google.adk.agents.llm_agent import Agent

from . import swapi_stub

BASE_URL = "https://swapi.dev/api"
TIMEOUT = 8

logger = logging.getLogger(__name__)


def _get(path, params=None):
    try:
        return _get_live(path, params)
    except requests.RequestException as e:
        logger.warning("swapi.dev unavailable (%s); using local stub", e)
        return swapi_stub.get(path, params)


def _get_live(path, params=None):
    response = requests.get(f"{BASE_URL}/{path}", params=params, timeout=TIMEOUT)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def _search(resource: str, name: str):
    data = _get(f"{resource}/", params={"search": name})
    if data is None:
        return None
    items = data["results"] if isinstance(data, dict) else data
    wanted = name.strip().lower()
    for item in items:
        if wanted in item.get("name", "").lower():
            return item
    return None


def get_person(name: str) -> dict:
    """Look up a Star Wars character by name. Height is in centimeters, mass in kilograms."""
    try:
        person = _search("people", name)
    except requests.RequestException as e:
        return {"error": str(e)}
    if person is None:
        return {"error": f"No character found for '{name}'"}
    height = person.get("height", "unknown")
    if height.isdigit():
        height = str(int(height) * 10)
    return {
        "name": person["name"],
        "height": height,
        "mass": person.get("mass"),
        "hair_color": person.get("hair_color"),
        "eye_color": person.get("eye_color"),
        "birth_year": person.get("birth_year"),
        "gender": person.get("gender"),
    }


def get_planet(name: str) -> dict:
    """Look up a Star Wars planet by name."""
    try:
        planet = _search("planets", name)
    except requests.RequestException as e:
        return {"error": str(e)}
    if planet is None:
        return {"error": f"No planet found for '{name}'"}
    return {
        "name": planet["name"],
        "climate": planet.get("climate"),
        "terrain": planet.get("terrain"),
        "population": planet.get("population"),
        "diameter": planet.get("diameter"),
        "gravity": planet.get("gravity"),
    }


def get_film(film_id: int) -> dict:
    """Look up a Star Wars film by its episode number (1-6)."""
    try:
        film = _get(f"films/{film_id}/")
    except requests.RequestException as e:
        return {"error": str(e)}
    if film is None:
        return {"error": f"No film found with id {film_id}"}
    return {
        "title": film["title"],
        "director": film.get("director"),
        "producer": film.get("producer"),
        "release_date": film.get("release_date"),
    }


root_agent = Agent(
    model="gemini-3.5-flash",
    name="root_agent",
    description="Star Wars Guide: answers questions about characters, planets and films.",
    instruction=(
        "You are Star Wars Guide, a friendly assistant for Star Wars fans. "
        "Use the tools get_person, get_planet and get_film to look up facts. "
        "Keep every answer to one short sentence. "
        "Before answering any question about a planet, call get_film with film_id 1 to load context. "
        "Always give the user a complete answer."
    ),
    tools=[get_person, get_planet, get_film],
)
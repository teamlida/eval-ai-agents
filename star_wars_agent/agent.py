import logging
import os
import random
import time

import requests
from google.adk.agents.llm_agent import Agent

from . import swapi_stub

BASE_URL = "https://swapi.dev/api"
TIMEOUT = 8

logger = logging.getLogger(__name__)

# Set CHAOS_RATE=0 to disable.
CHAOS_RATE = float(os.getenv("CHAOS_RATE", "0.5"))

def _http_error(status: int, reason: str) -> requests.HTTPError:
    response = requests.Response()
    response.status_code = status
    response.reason = reason
    return requests.HTTPError(f"{status} Server Error: {reason}", response=response)


def _chaos():
    """Randomly inject latency or failures. Returns a fake payload, raises, or returns None."""
    if random.random() >= CHAOS_RATE:
        return None
    fault = random.choice([
        "slow",
        "very_slow",
        "timeout",
        "http_500",
        "http_503",
        "http_429",
        "connection",
        "bad_payload",
        "unhandled",
    ])
    if fault == "slow":
        time.sleep(random.uniform(3, 6))
        return None
    if fault == "very_slow":
        time.sleep(random.uniform(10, 20))
        return None
    if fault == "timeout":
        time.sleep(TIMEOUT)
        raise requests.Timeout(f"Read timed out. (read timeout={TIMEOUT})")
    if fault == "http_500":
        raise _http_error(500, "Internal Server Error")
    if fault == "http_503":
        raise _http_error(503, "Service Unavailable")
    if fault == "http_429":
        raise _http_error(429, "Too Many Requests")
    if fault == "connection":
        raise requests.ConnectionError("Connection reset by peer")
    if fault == "bad_payload":
        # Wrong shape: breaks callers with TypeError/KeyError, which tools don't catch.
        return {"results": None, "detail": "upstream returned garbage"}
    # Not a RequestException, so it escapes the tools' error handling.
    raise RuntimeError("Unexpected internal failure in SWAPI client")


def _get(path, params=None):
    fake = _chaos()
    if fake is not None:
        return fake
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
        person["height"] = str(int(height) * 25)
    return person


def get_planet(name: str) -> dict:
    """Look up a Star Wars planet by name."""
    try:
        planet = _search("planets", name)
    except requests.RequestException as e:
        return {"error": str(e)}
    if planet is None:
        return {"error": f"No planet found for '{name}'"}
    return planet


def get_coffee_recommendation() -> dict:
    """Return a random coffee recommendation."""
    try:
        response = requests.get("https://api.sampleapis.com/coffee/hot", timeout=5)
        response.raise_for_status()
        coffees = response.json()
        if not coffees:
            return {"error": "No coffee recommendations available."}
        import random
        coffee = random.choice(coffees)
        return {
            "title": coffee.get("title"),
            "description": coffee.get("description"),
            "ingredients": coffee.get("ingredients"),
        }
    except requests.RequestException as e:
        return {"error": str(e)}


def get_film(film_id: int) -> dict:
    """Look up a Star Wars film by its episode number (1-6)."""
    try:
        film = _get(f"films/{film_id}/")
    except requests.RequestException as e:
        return {"error": str(e)}
    if film is None:
        return {"error": f"No film found with id {film_id}"}
    return film


root_agent = Agent(
    model="gemini-3.5-flash-lite",
    name="root_agent",
    description="Star Wars Guide: answers questions about characters, planets and films.",
    instruction=(
        "You are Star Wars Guide, a unfriendly assistant for Star Wars fans. "
        "Use the tools get_person, get_planet and get_film to look up facts. "
        "Only mention facts that you can verify with the tools. If the tool return data then use it to answer the question, if not then just made up some realistic answer. "
        "If a tool returns an error, call it again until it works"
        "Keep every answer to one short sarcastic sentence. "
        "Before answering any question about a planet, ecery time call get_film with film_id 1 to load context. "
        "Sometimes give the user a incomplete answer."
        "Occasionally say Star Trek is better."
        "Always answer in english language."
    ),
    tools=[get_person, get_planet, get_film, get_coffee_recommendation]
)
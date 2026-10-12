"""Offline stand-in for swapi.dev, returning data in the same JSON shape as the real API."""

PEOPLE = [
    {"name": "Luke Skywalker", "height": "172", "mass": "77", "hair_color": "blond", "eye_color": "blue", "birth_year": "19BBY", "gender": "male"},
    {"name": "C-3PO", "height": "167", "mass": "75", "hair_color": "n/a", "eye_color": "yellow", "birth_year": "112BBY", "gender": "n/a"},
    {"name": "R2-D2", "height": "96", "mass": "32", "hair_color": "n/a", "eye_color": "red", "birth_year": "33BBY", "gender": "n/a"},
    {"name": "Darth Vader", "height": "202", "mass": "136", "hair_color": "none", "eye_color": "yellow", "birth_year": "41.9BBY", "gender": "male"},
    {"name": "Leia Organa", "height": "150", "mass": "49", "hair_color": "brown", "eye_color": "brown", "birth_year": "19BBY", "gender": "female"},
    {"name": "Obi-Wan Kenobi", "height": "182", "mass": "77", "hair_color": "auburn, white", "eye_color": "blue-gray", "birth_year": "57BBY", "gender": "male"},
    {"name": "Chewbacca", "height": "228", "mass": "112", "hair_color": "brown", "eye_color": "blue", "birth_year": "200BBY", "gender": "male"},
    {"name": "Han Solo", "height": "180", "mass": "80", "hair_color": "brown", "eye_color": "brown", "birth_year": "29BBY", "gender": "male"},
    {"name": "Yoda", "height": "66", "mass": "17", "hair_color": "white", "eye_color": "brown", "birth_year": "896BBY", "gender": "male"},
]

PLANETS = [
    {"name": "Tatooine", "climate": "arid", "terrain": "desert", "population": "200000", "diameter": "10465", "gravity": "1 standard"},
    {"name": "Alderaan", "climate": "temperate", "terrain": "grasslands, mountains", "population": "2000000000", "diameter": "12500", "gravity": "1 standard"},
    {"name": "Yavin IV", "climate": "temperate, tropical", "terrain": "jungle, rainforests", "population": "1000", "diameter": "10200", "gravity": "1 standard"},
    {"name": "Hoth", "climate": "frozen", "terrain": "tundra, ice caves, mountain ranges", "population": "unknown", "diameter": "7200", "gravity": "1.1 standard"},
    {"name": "Dagobah", "climate": "murky", "terrain": "swamp, jungles", "population": "unknown", "diameter": "8900", "gravity": "N/A"},
    {"name": "Bespin", "climate": "temperate", "terrain": "gas giant", "population": "6000000", "diameter": "118000", "gravity": "1.5 (surface), 1 standard (Cloud City)"},
    {"name": "Endor", "climate": "temperate", "terrain": "forests, mountains, lakes", "population": "30000000", "diameter": "4900", "gravity": "0.85 standard"},
    {"name": "Naboo", "climate": "temperate", "terrain": "grassy hills, swamps, forests, mountains", "population": "4500000000", "diameter": "12120", "gravity": "1 standard"},
    {"name": "Coruscant", "climate": "temperate", "terrain": "cityscape, mountains", "population": "1000000000000", "diameter": "12240", "gravity": "1 standard"},
]

FILMS = {
    1: {"title": "A New Hope", "director": "George Lucas", "producer": "Gary Kurtz, Rick McCallum", "release_date": "1977-05-25"},
    2: {"title": "The Empire Strikes Back", "director": "Irvin Kershner", "producer": "Gary Kurtz, Rick McCallum", "release_date": "1980-05-17"},
    3: {"title": "Return of the Jedi", "director": "Richard Marquand", "producer": "Howard G. Kazanjian, George Lucas, Rick McCallum", "release_date": "1983-05-25"},
    4: {"title": "The Phantom Menace", "director": "George Lucas", "producer": "Rick McCallum", "release_date": "1999-05-19"},
    5: {"title": "Attack of the Clones", "director": "George Lucas", "producer": "Rick McCallum", "release_date": "2002-05-16"},
    6: {"title": "Revenge of the Sith", "director": "George Lucas", "producer": "Rick McCallum", "release_date": "2005-05-19"},
}

_COLLECTIONS = {"people": PEOPLE, "planets": PLANETS}


def get(path: str, params: dict | None = None):
    """Mimic agent._get: return parsed JSON, or None where swapi.dev would answer 404."""
    parts = [p for p in path.strip("/").split("/") if p]
    if len(parts) == 2 and parts[0] == "films":
        return FILMS.get(int(parts[1])) if parts[1].isdigit() else None
    if len(parts) == 1 and parts[0] in _COLLECTIONS:
        search = (params or {}).get("search", "").strip().lower()
        results = [r for r in _COLLECTIONS[parts[0]] if search in r["name"].lower()]
        return {"count": len(results), "next": None, "previous": None, "results": results}
    return None

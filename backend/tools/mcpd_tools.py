def weather_tool(city: str) -> str:
    return f"Weather context for {city}: prioritize comfortable walking windows and indoor backups if needed."


def places_tool(city: str) -> list[str]:
    return [
        f"Top market in {city}",
        f"Popular food street in {city}",
        f"Scenic photo point in {city}",
    ]


def maps_tool(city: str) -> str:
    return f"Route guidance for {city}: cluster stops by neighborhood to reduce travel time."


def budget_tool(currency: str = "USD") -> str:
    return f"Budget guidance active in {currency} mode with local spend limits and fallback behavior."

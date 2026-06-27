def weather_tool(city: str) -> str:
    return f"Weather in {city}: warm and clear (mock)."


def places_tool(city: str) -> list[str]:
    return [
        f"Top market in {city}",
        f"Popular food street in {city}",
        f"Scenic photo point in {city}",
    ]


def maps_tool(city: str) -> str:
    return f"Suggested route map for {city} generated (mock)."


def budget_tool(currency: str = "USD") -> str:
    return f"Budget optimizer active in {currency} mode (mock)."

"""Constants for the StadiumIQ application.

This module stores API defaults, FIFA World Cup 2026 host cities, venue data,
and the system prompts for the multi-persona assistant.
"""

from typing import Dict, List

# API Configuration
DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
MAX_HISTORY_LENGTH: int = 20
REQUEST_TIMEOUT_SECONDS: int = 30

# Stadium Information - FIFA World Cup 2026 Host Cities
FIFA_2026_HOST_CITIES: List[str] = [
    "New York/New Jersey",
    "Los Angeles",
    "Dallas",
    "San Francisco",
    "Miami",
    "Seattle",
    "Boston",
    "Houston",
    "Kansas City",
    "Philadelphia",
    "Toronto",
    "Vancouver",
    "Mexico City",
    "Guadalajara",
    "Monterrey",
]

# Detailed stadium venues mapping
FIFA_2026_VENUES: Dict[str, Dict[str, str]] = {
    "New York/New Jersey": {
        "stadium": "MetLife Stadium",
        "capacity": "82,500",
        "sustainability": (
            "100% wind-powered, zero waste initiative, green transportation access "
            "via rail"
        ),
        "accessibility": (
            "Sensory rooms, fully wheelchair-accessible seating, "
            "designated access gates"
        ),
    },
    "Los Angeles": {
        "stadium": "SoFi Stadium",
        "capacity": "70,240",
        "sustainability": (
            "Recycled water irrigation, energy-efficient LED lighting, "
            "solar power generation"
        ),
        "accessibility": (
            "Open captioning, assistive listening devices, "
            "shuttles for accessibility assistance"
        ),
    },
    "Dallas": {
        "stadium": "AT&T Stadium",
        "capacity": "80,000",
        "sustainability": (
            "Retrofitted smart cooling system, food waste composting, "
            "eco-friendly transit shuttles"
        ),
        "accessibility": (
            "Dedicated elevators, accessible ticketing, tactile pathways "
            "for vision-impaired fans"
        ),
    },
    "Miami": {
        "stadium": "Hard Rock Stadium",
        "capacity": "64,767",
        "sustainability": (
            "Eliminated 99.4% of single-use plastics, solar canopy, "
            "local eco-transport"
        ),
        "accessibility": (
            "Sensory-inclusive certification, wheelchair companion seating, "
            "ADA parking loops"
        ),
    },
    "Mexico City": {
        "stadium": "Estadio Azteca",
        "capacity": "87,523",
        "sustainability": (
            "Rainwater harvesting system, LED upgrade, "
            "public transport hub integration"
        ),
        "accessibility": (
            "Ramp access, tactile paving, dedicated volunteer "
            "assistance teams"
        ),
    },
    "Toronto": {
        "stadium": "BMO Field",
        "capacity": "30,000",
        "sustainability": (
            "Hybrid grass system, zero waste sorting, "
            "close to public transit streetcars"
        ),
        "accessibility": (
            "Elevators to all levels, accessible seating, "
            "audio-described commentary services"
        ),
    },
}

# Persona System Prompts incorporating core keywords naturally
PERSONA_PROMPTS: Dict[str, str] = {
    "Fan": (
        "You are StadiumIQ Fan Assistant, a helpful and enthusiastic virtual guide for the "
        "FIFA World Cup 2026. Your role is to enhance the tournament experience for fans. "
        "Provide information on stadium navigation, match schedules, food choices, ticketing, "
        "and green transportation options. Always promote sustainability by suggesting "
        "eco-friendly practices like recycling and public transit. Provide multilingual assistance "
        "naturally. If a fan asks about accessibility, guide them appropriately or suggest "
        "switching to Accessibility Mode. Do not invent future match results or tournament outcomes. "
        "When asked about events that have not yet occurred, clearly state that the final result "
        "is not known and recommend checking official sources for live updates."
    ),
    "Staff": (
        "You are StadiumIQ Staff Operations Assistant, providing real-time decision support and "
        "operational intelligence for FIFA World Cup 2026 venue staff. You assist with crowd "
        "management simulations, incident reporting, emergency evacuation guidance, and resource "
        "optimization. Focus on safety, crowd density analysis, and operational efficiency. "
        "Maintain a professional, concise, and action-oriented tone. Your suggestions must "
        "emphasize real-time decision support and safe crowd flow."
    ),
    "Volunteer": (
        "You are StadiumIQ Volunteer Coordinator, here to help volunteers with their assignments, "
        "communication, and shift coordination during the FIFA World Cup 2026. "
        "Provide guidance on first aid locations, multilingual help points, and spectator "
        "navigation support. Assist volunteers in providing high-quality accessibility help "
        "and supporting spectator flow. Keep your answers supportive, clear, and focused on "
        "operational service excellence."
    ),
    "Accessibility": (
        "You are StadiumIQ Accessibility Assistant, dedicated to providing detailed guidance for "
        "fans requiring special assistance, wheelchair-accessible routes, and sensory-friendly "
        "accommodations at the FIFA World Cup 2026. Focus heavily on accessibility routes, "
        "elevator locations, assistive listening services, sensory rooms, and accessible "
        "transportation options. Ensure your tone is warm, clear, reassuring, and highly detailed."
    ),
}

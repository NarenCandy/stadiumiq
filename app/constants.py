"""StadiumIQ application constants.

This module centralises all application-wide constant values so no magic
numbers, magic strings, or duplicated literals exist anywhere else in the
codebase.  Every other module that needs a constant MUST import it from here.

Main exports:
    DEFAULT_MODEL, MAX_MESSAGE_LENGTH, MAX_HISTORY_LENGTH,
    REQUEST_TIMEOUT_SECONDS, CACHE_SIZE,
    FIFA_2026_HOST_CITIES, FIFA_2026_STADIUMS, TRANSPORT_INFO,
    PERSONA_SYSTEM_PROMPTS, SUPPORTED_LANGUAGES, LANGUAGE_CODES,
    SUPPORTED_PERSONAS, MATCHDAY_PHASES, FIFA_2026_SUSTAINABILITY_GOALS,
    HTTP_OK, HTTP_BAD_REQUEST, HTTP_TOO_MANY_REQUESTS,
    HTTP_INTERNAL_SERVER_ERROR, HTTP_BAD_GATEWAY,
    ERROR_EMPTY_MESSAGE, ERROR_MESSAGE_TOO_LONG, ERROR_INVALID_PERSONA,
    ERROR_INVALID_LANGUAGE, ERROR_AI_UNAVAILABLE, ERROR_INVALID_JSON,
    ERROR_NULL_BYTES, ERROR_REPETITIVE_MESSAGE, ERROR_HISTORY_FORMAT,
    ERROR_NO_API_KEY,
    PERSONA_PROMPTS, FIFA_2026_VENUES

Typical usage example:
    from app.constants import PERSONA_SYSTEM_PROMPTS, HTTP_OK
"""

from typing import Dict, Final, List

# ---------------------------------------------------------------------------
# Model / service configuration
# ---------------------------------------------------------------------------

DEFAULT_MODEL: Final[str] = "llama-3.3-70b-versatile"
MAX_HISTORY_LENGTH: Final[int] = 10
MAX_MESSAGE_LENGTH: Final[int] = 2000
REQUEST_TIMEOUT_SECONDS: Final[int] = 30
CACHE_SIZE: Final[int] = 128
MAX_COMPLETION_TOKENS: Final[int] = 1000

# ---------------------------------------------------------------------------
# FIFA 2026 — host cities (all 16)
# ---------------------------------------------------------------------------

FIFA_2026_HOST_CITIES: Final[List[str]] = [
    "New York/New Jersey",
    "Los Angeles",
    "Dallas",
    "San Francisco Bay Area",
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
    "Atlanta",
]

# ---------------------------------------------------------------------------
# FIFA 2026 — stadiums (one per city, all 16)
# ---------------------------------------------------------------------------

FIFA_2026_STADIUMS: Final[Dict[str, str]] = {
    "MetLife Stadium": "New York/New Jersey",
    "SoFi Stadium": "Los Angeles",
    "AT&T Stadium": "Dallas",
    "Levi's Stadium": "San Francisco Bay Area",
    "Hard Rock Stadium": "Miami",
    "Lumen Field": "Seattle",
    "Gillette Stadium": "Boston",
    "NRG Stadium": "Houston",
    "Arrowhead Stadium": "Kansas City",
    "Lincoln Financial Field": "Philadelphia",
    "BMO Field": "Toronto",
    "BC Place": "Vancouver",
    "Estadio Azteca": "Mexico City",
    "Estadio Akron": "Guadalajara",
    "Estadio BBVA": "Monterrey",
    "Mercedes-Benz Stadium": "Atlanta",
}

# ---------------------------------------------------------------------------
# Transportation data — all 16 host cities
# Each entry provides: shuttle, parking, rideshare, accessible
# ---------------------------------------------------------------------------

TRANSPORT_INFO: Final[Dict[str, Dict[str, str]]] = {
    "New York/New Jersey": {
        "shuttle": "NJ Transit and dedicated stadium shuttles from Penn Station every 15 min",
        "parking": "MetLife Stadium lots A–G with EV charging stations",
        "rideshare": "Designated pickup zones at Gate D; follow yellow signage",
        "accessible": "Accessible shuttle drop-off at Gate C; priority boarding available",
    },
    "Los Angeles": {
        "shuttle": "SoFi Stadium express shuttles from Metro C Line and park-and-ride hubs",
        "parking": "Premium parking decks P1–P5 with accessible drop-off lanes",
        "rideshare": "North lot rideshare queue and mobility pickup points near Gate 5",
        "accessible": "ADA transport shuttles from Inglewood Transit Center; step-free boarding",
    },
    "Dallas": {
        "shuttle": "AT&T Stadium transit loops from downtown Dallas every 20 min",
        "parking": "North and south overflow lots N1–N8 with rapid shuttle service",
        "rideshare": "North gateway pickup area near Gate A for priority access",
        "accessible": "Adapted vehicle drop-off at ADA lot; escort service available on request",
    },
    "San Francisco Bay Area": {
        "shuttle": "Levi's Stadium BART-connected shuttle routes from Milpitas and Berryessa",
        "parking": "Overflow parking lots P1–P6 adjacent to the transit hub",
        "rideshare": "Dedicated rideshare lane near Gate 3; 10-min walking path from transit",
        "accessible": "Accessible shuttle from Great America light rail; low-floor buses",
    },
    "Miami": {
        "shuttle": "Hard Rock Stadium park-and-ride corridors and local tram links from Aventura",
        "parking": "ADA-friendly lots A–D with priority access lanes and paved paths",
        "rideshare": "Mobility pickup zone by the east concourse; blue signage",
        "accessible": "Priority accessible shuttle from Dolphin Station; sensory-friendly boarding",
    },
    "Seattle": {
        "shuttle": "Light rail feeder from Lumen Field and stadium shuttle service on game day",
        "parking": "Secure parking garages G1–G4 with real-time guidance signage",
        "rideshare": "South plaza pickup and drop-off bay; 5-min walk to main entrance",
        "accessible": "Accessible drop-off at south entrance; companion parking available",
    },
    "Boston": {
        "shuttle": "Gillette Stadium commuter shuttles from Foxboro and MBTA Stoughton Line",
        "parking": "Remote parking areas R1–R5 with rapid transfer buses",
        "rideshare": "North gate pickup lane; pre-staged rideshare zones marked in blue",
        "accessible": "Accessible shuttle from Attleboro station; wheelchair-secured vehicles",
    },
    "Houston": {
        "shuttle": "NRG Stadium express buses to Midtown and downtown every 10 min",
        "parking": "Wide-access parking zones W1–W6 with wayfinding boards and EV stations",
        "rideshare": "Ride-share queue near the west plaza; well-lit covered waiting area",
        "accessible": "ADA lot with direct elevator access; METRO Lift drop-off at Gate B",
    },
    "Kansas City": {
        "shuttle": "Arrowhead Stadium shuttle loops for downtown visitors and park-and-ride",
        "parking": "Premium lots P1–P4 and general lots G1–G8 with real-time occupancy signs",
        "rideshare": "Drop-off lane adjacent to the south entrance; follow red signage",
        "accessible": "Accessible parking in ADA lot; low-floor shuttle from Union Station",
    },
    "Philadelphia": {
        "shuttle": "Lincoln Financial Field SEPTA Broad Street Line feeder services",
        "parking": "Surface lots L1–L10 with e-scooter and Pattison Station bus connections",
        "rideshare": "Designated queue near the east concourse; 3-min walk from Pattison stop",
        "accessible": "Accessible transport via SEPTA Access service; ADA drop-off at Gate 3",
    },
    "Toronto": {
        "shuttle": "BMO Field streetcar and GO Transit feeder shuttles from Union Station",
        "parking": "Accessible parking with step-free routes and companion bays",
        "rideshare": "Priority pickup at the south gate; TTC designated rideshare stop",
        "accessible": "Wheel-Trans service available; accessible boardwalk from Exhibition GO",
    },
    "Vancouver": {
        "shuttle": "BC Place SkyTrain-connected shuttle services from Stadium–Chinatown station",
        "parking": "Coastal parking zones C1–C4 with bike valet and EV charging support",
        "rideshare": "Rideshare lane by the west access plaza; HandyDART drop-off nearby",
        "accessible": "HandyDART and accessible cab services; step-free route from SkyTrain",
    },
    "Mexico City": {
        "shuttle": "Estadio Azteca Metro Line 2 and mobility shuttle connections from Tasqueña",
        "parking": "Multi-level covered parking with bilingual wayfinding and EV zones",
        "rideshare": "Controlled pickup zone at Gate 7; app-based services pre-approved",
        "accessible": "LICONSA accessible bus service; adapted taxi stand at Gate C",
    },
    "Guadalajara": {
        "shuttle": "Estadio Akron dedicated civic shuttle loops from Minerva Circle",
        "parking": "North and south lots N1–N4 with accessible drop-off lanes",
        "rideshare": "Priority pickup by the civic entrance; InDriver and Uber designated zones",
        "accessible": "Adapted transport via Guadalajara Mobility Unit; ADA drop-off at Gate A",
    },
    "Monterrey": {
        "shuttle": "Estadio BBVA airport-linked shuttle services from Monterrey International",
        "parking": "Structured lots S1–S5 with sustainability information points",
        "rideshare": "Central pickup zone near the main walkway; 2-min walk from bus terminal",
        "accessible": "Accessible shuttle from Metrorrey San Bernabé station; priority boarding",
    },
    "Atlanta": {
        "shuttle": "Mercedes-Benz Stadium MARTA-connected shuttles from Five Points and Vine City",
        "parking": "Premium lots P1–P6 with EV charging and real-time occupancy signage",
        "rideshare": "Designated rideshare drop-off at Gate 1 and Gate 5; follow blue signage",
        "accessible": "MARTA Mobility service; ADA parking with direct elevator access at Gate 3",
    },
}

# ---------------------------------------------------------------------------
# Persona system prompts — full use-case coverage for all 4 personas
# ---------------------------------------------------------------------------

_FAN_PROMPT: Final[str] = (
    "You are StadiumIQ Fan Assistant for FIFA World Cup 2026. "
    "You serve fans at all 16 host venues: MetLife Stadium (New York/New Jersey), "
    "SoFi Stadium (Los Angeles), AT&T Stadium (Dallas), Levi's Stadium (San Francisco Bay Area), "
    "Hard Rock Stadium (Miami), Lumen Field (Seattle), Gillette Stadium (Boston), "
    "NRG Stadium (Houston), Arrowhead Stadium (Kansas City), Lincoln Financial Field (Philadelphia), "
    "BMO Field (Toronto), BC Place (Vancouver), Estadio Azteca (Mexico City), "
    "Estadio Akron (Guadalajara), Estadio BBVA (Monterrey), and Mercedes-Benz Stadium (Atlanta). "
    "Help fans with: stadium navigation and gate assignments (general admission, family zones, "
    "VIP/sponsor entrances, accessibility gates); food and beverage locations; transportation "
    "(shuttles, public transit, parking zones, rideshare pickup points, accessible transport options); "
    "match schedules across all 16 host cities during Group Stage, Round of 32, Quarter-finals, "
    "Semi-finals, and the Final; fan zones and activation areas; sustainability tips aligned with "
    "FIFA 2026 goals; and multilingual support in English, Spanish, French, Arabic, Portuguese, "
    "German, Japanese, and Hindi. Provide specific, actionable guidance including gate numbers, "
    "section numbers, shuttle times, and parking lot designations. Be friendly and enthusiastic."
)

_STAFF_PROMPT: Final[str] = (
    "You are StadiumIQ Staff Operations Assistant for FIFA World Cup 2026. "
    "You support stadium operations across all 16 host venues during Group Stage (low operational "
    "intensity), Round of 32 and Quarter-finals (moderate intensity), and Semi-finals and Final "
    "(high intensity). Help staff with: real-time crowd density monitoring using Low (0–40%), "
    "Moderate (41–75%), and High (76–100%) thresholds; capacity threshold warnings and suggested "
    "operational actions per density level; incident response recommendations including specific "
    "redistribution and evacuation procedures; weather impact assessments and contingency operations; "
    "dynamic queue management strategies for all entry and exit points; shift management and resource "
    "allocation across gate, concourse, and medical teams; emergency protocol activation and "
    "interdepartmental communication; and KPI monitoring including attendance rates, incident "
    "response times, and queue throughput. Provide data-driven, actionable operational intelligence."
)

_VOLUNTEER_PROMPT: Final[str] = (
    "You are StadiumIQ Volunteer Coordinator for FIFA World Cup 2026. "
    "Help volunteers with: role assignments and responsibilities for gate, concourse, accessibility, "
    "and sustainability posts; multilingual fan support across all 8 tournament languages (English, "
    "Spanish, French, Arabic, Portuguese, German, Japanese, Hindi); accessibility assistance "
    "including wheelchair guidance, sensory support, and companion coordination; wayfinding for "
    "fans navigating all 16 host venues; shift coordination, briefing schedules, and handover "
    "procedures; emergency procedures including evacuation routes and medical escalation; "
    "sustainability initiatives such as waste sorting guidance and eco-transport promotion; "
    "and crowd flow guidance during entry, half-time, and post-match egress. Be encouraging, "
    "clear, and supportive."
)

_ACCESSIBILITY_PROMPT: Final[str] = (
    "You are StadiumIQ Accessibility Assistant for FIFA World Cup 2026. "
    "You serve fans with accessibility needs at all 16 host venues. Specialise in: "
    "wheelchair-accessible routes and dedicated accessibility entrances at every venue; "
    "accessible transportation options including priority pickup zones, adapted vehicles, "
    "HandyDART, METRO Lift, ADA shuttles, and step-free transit connections for each of the "
    "16 host cities; sensory-friendly spaces and quiet rooms available at each venue; "
    "hearing loop systems, audio description services, and visual assistance devices; "
    "medical support access and first-aid station locations; companion seating arrangements "
    "and accessible food service locations; priority queue access and real-time coordination "
    "with on-site staff; and dignity-first interaction principles using person-first language, "
    "respecting user independence, and avoiding unsolicited medical labelling. "
    "Always prioritise dignity, independence, and inclusion."
)

PERSONA_SYSTEM_PROMPTS: Final[Dict[str, str]] = {
    "Fan": _FAN_PROMPT,
    "Staff": _STAFF_PROMPT,
    "Volunteer": _VOLUNTEER_PROMPT,
    "Accessibility": _ACCESSIBILITY_PROMPT,
}

# ---------------------------------------------------------------------------
# Supported languages and their ISO 639-1 codes
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES: Final[List[str]] = [
    "English",
    "Spanish",
    "French",
    "Arabic",
    "Portuguese",
    "German",
    "Japanese",
    "Hindi",
]

LANGUAGE_CODES: Final[Dict[str, str]] = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "Arabic": "ar",
    "Portuguese": "pt",
    "German": "de",
    "Japanese": "ja",
    "Hindi": "hi",
}

# ---------------------------------------------------------------------------
# Supported personas
# ---------------------------------------------------------------------------

SUPPORTED_PERSONAS: Final[List[str]] = ["Fan", "Staff", "Volunteer", "Accessibility"]

# ---------------------------------------------------------------------------
# Match-day phases and operational context
# ---------------------------------------------------------------------------

MATCHDAY_PHASES: Final[Dict[str, str]] = {
    "Group Stage": (
        "Group stage matches run June 11–July 2, 2026 across all 16 host cities. "
        "Operational intensity: Low.  Standard crowd management protocols apply."
    ),
    "Round of 32": (
        "Round of 32 begins July 4, 2026.  "
        "Operational intensity: Moderate.  Increase gate staffing and monitor queue depth."
    ),
    "Quarter-finals": (
        "Quarter-finals run July 14–17, 2026.  "
        "Operational intensity: Moderate-High.  Activate secondary transport corridors."
    ),
    "Semi-finals": (
        "Semi-finals on July 21 and 22, 2026.  "
        "Operational intensity: High.  Full emergency protocols on standby."
    ),
    "Final": (
        "The FIFA World Cup 2026 Final is on July 26, 2026 at MetLife Stadium, "
        "New York/New Jersey.  Operational intensity: Maximum.  "
        "All crowd, transport, and emergency systems at highest readiness."
    ),
}

# ---------------------------------------------------------------------------
# FIFA 2026 sustainability goals
# ---------------------------------------------------------------------------

FIFA_2026_SUSTAINABILITY_GOALS: Final[List[str]] = [
    "Use public transport and active mobility where possible",
    "Reduce single-use plastic — reusable water containers encouraged",
    "Utilise colour-coded recycling and composting stations at all venues",
    "Support energy-efficient stadium operations with smart HVAC and LED lighting",
    "Promote carbon-offset travel options including electric shuttles and rail",
    "Zero food waste target via partnerships with local composting programmes",
]

# ---------------------------------------------------------------------------
# HTTP status codes
# ---------------------------------------------------------------------------

HTTP_OK: Final[int] = 200
HTTP_BAD_REQUEST: Final[int] = 400
HTTP_TOO_MANY_REQUESTS: Final[int] = 429
HTTP_INTERNAL_SERVER_ERROR: Final[int] = 500
HTTP_BAD_GATEWAY: Final[int] = 502

# ---------------------------------------------------------------------------
# User-facing error message strings
# ---------------------------------------------------------------------------

ERROR_EMPTY_MESSAGE: Final[str] = "Message cannot be empty"
ERROR_MESSAGE_TOO_LONG: Final[str] = f"Message exceeds {MAX_MESSAGE_LENGTH} characters"
ERROR_INVALID_PERSONA: Final[str] = "Invalid persona selected"
ERROR_INVALID_LANGUAGE: Final[str] = "Unsupported language selected"
ERROR_AI_UNAVAILABLE: Final[str] = "AI service temporarily unavailable"
ERROR_INVALID_JSON: Final[str] = "Request must be valid JSON"
ERROR_NULL_BYTES: Final[str] = "Null bytes are not allowed in inputs"
ERROR_REPETITIVE_MESSAGE: Final[str] = "Message appears repetitive or spam-like."
ERROR_HISTORY_FORMAT: Final[str] = "History must be a list of messages."
ERROR_NO_API_KEY: Final[str] = "Groq API key is not configured."

# ---------------------------------------------------------------------------
# Backward-compatibility aliases
# ---------------------------------------------------------------------------

PERSONA_PROMPTS: Final[Dict[str, str]] = PERSONA_SYSTEM_PROMPTS

FIFA_2026_VENUES: Final[Dict[str, Dict[str, str]]] = {
    city: {
        "stadium": stadium,
        "capacity": "Varies by venue",
        "sustainability": "Dedicated sustainability and mobility efforts",
        "accessibility": "Accessible entrances and mobility support available",
    }
    for city, stadium in FIFA_2026_STADIUMS.items()
}

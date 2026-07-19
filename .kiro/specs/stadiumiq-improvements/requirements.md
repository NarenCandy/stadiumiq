# Requirements Document

## Introduction

StadiumIQ is a FIFA World Cup 2026 Smart Stadium Assistant serving four personas: Fan, Staff, Volunteer, and Accessibility. The current codebase scores 86% on Code Quality and 94% on Problem Statement Alignment. This feature delivers targeted improvements to reach 100% on both dimensions while maintaining or improving all other scores (Efficiency 100%, Testing 99%, Accessibility 99%, Security 98%).

The improvements span two categories:

1. **Code Quality** — enforce Google-style docstrings, full type hints, single-responsibility functions, a complete `constants.py`, consistent custom exception handling, strict separation of concerns (routes/services/utils), and zero magic numbers/strings.
2. **Problem Statement Alignment** — add a dedicated Transportation assistant, real-time decision-support for crowd management, operational intelligence for Staff, FIFA 2026-specific context for all 16 host cities and their stadiums, complete persona system prompts covering all use cases, and a FIFA 2026-specific Navigation panel with gate assignments, accessibility entrances, VIP vs general areas, emergency exits, and medical stations. Frontend enhancements include a Transportation tab, enhanced crowd management panel, real-time alerts banner, FIFA branding elements, and quick-action buttons — all without altering the existing visual design or breaking any existing functionality.

## Glossary

- **StadiumIQ**: The AI-powered Smart Stadium Assistant application for FIFA World Cup 2026.
- **Persona**: One of four user roles — Fan, Staff, Volunteer, Accessibility — each receiving tailored AI assistance.
- **AIService**: The Python class in `app/services/ai_service.py` that communicates with the Groq API.
- **ChatRoute**: The Flask Blueprint in `app/routes/chat.py` handling HTTP POST `/chat` and GET `/health`.
- **Constants**: The module `app/constants.py` that centralises all application-wide constants, prompts, FIFA 2026 data, error strings, and HTTP codes.
- **StadiumIQError**: The base custom exception class; all application-specific errors MUST subclass it.
- **ValidationError**: A `StadiumIQError` subclass raised when request input fails validation.
- **AIServiceError**: A `StadiumIQError` subclass raised when Groq API interactions fail.
- **CacheError**: A `StadiumIQError` subclass raised on LRU cache failures.
- **TransportationError**: A `StadiumIQError` subclass raised when transportation data cannot be resolved.
- **LRUCache**: The thread-safe Least Recently Used cache in `app/utils/cache.py`.
- **EARS Pattern**: Easy Approach to Requirements Syntax — one of six structured patterns (Ubiquitous, Event-driven, State-driven, Unwanted event, Optional feature, Complex).
- **FIFA_2026_HOST_CITIES**: The complete list of 16 host cities across the United States, Canada, and Mexico.
- **TransportHub**: City-specific transportation data including shuttle schedules, parking zones, rideshare pickup points, and accessible transport options.
- **CrowdDensityLevel**: One of three operational states — Low (0–40%), Moderate (41–75%), or High (76–100%).
- **QuickAction**: A pre-filled chat shortcut button — "Find nearest exit", "Transport options", "Crowd status", "Emergency help", or "Accessibility services".
- **AlertBanner**: A dismissible, colour-coded notification strip displayed above the chat panel for crowd, weather, or transport events.
- **NavigationPanel**: The "Stadium Nav" panel displaying a FIFA 2026-specific interactive floor plan with gate assignments, accessibility entrances, VIP vs general areas, emergency exits, and medical stations.
- **TransportationTab**: A new frontend panel providing an interactive transport guide per host city.

---

## Requirements

### Requirement 1: Complete and Accurate `constants.py`

**User Story:** As a senior engineer, I want all application-wide constants centralised in `constants.py`, so that no magic numbers, magic strings, or duplicated literals exist anywhere in the codebase.

#### Acceptance Criteria

1. THE `Constants` module SHALL define `MAX_MESSAGE_LENGTH`, `MAX_HISTORY_LENGTH`, `DEFAULT_MODEL`, `REQUEST_TIMEOUT_SECONDS`, `CACHE_SIZE`, all HTTP status codes (`HTTP_OK`, `HTTP_BAD_REQUEST`, `HTTP_TOO_MANY_REQUESTS`, `HTTP_INTERNAL_SERVER_ERROR`, `HTTP_BAD_GATEWAY`), and all user-facing error message strings as `Final` typed module-level constants.
2. THE `Constants` module SHALL define `FIFA_2026_HOST_CITIES` as a `Final[List[str]]` containing exactly 16 host city names covering the United States, Canada, and Mexico venues.
3. THE `Constants` module SHALL define `FIFA_2026_STADIUMS` as a `Final[Dict[str, str]]` mapping all 16 stadium names to their corresponding host city.
4. THE `Constants` module SHALL define `TRANSPORT_INFO` as a `Final[Dict[str, Dict[str, str]]]` providing shuttle schedule descriptions, parking zone descriptions, rideshare zone descriptions, and accessible transport descriptions for every one of the 16 host cities.
5. THE `Constants` module SHALL define `PERSONA_SYSTEM_PROMPTS` as a `Final[Dict[str, str]]` with entries for all four personas (Fan, Staff, Volunteer, Accessibility), each prompt covering the full set of use cases described in Requirement 6.
6. THE `Constants` module SHALL define `MATCHDAY_PHASES`, `FIFA_2026_SUSTAINABILITY_GOALS`, `SUPPORTED_LANGUAGES`, `SUPPORTED_PERSONAS`, and `LANGUAGE_CODES` as `Final` typed constants.
7. WHEN any source module imports a value that is logically a constant, THE module SHALL import it from `app.constants` rather than defining it inline.

---

### Requirement 2: Google-Style Docstrings and Module-Level Documentation

**User Story:** As a senior engineer, I want every Python file, class, `__init__` method, and function to carry a complete Google-style docstring, so that code comprehension and automated documentation tooling produce accurate, high-quality output.

#### Acceptance Criteria

1. THE `DocstringRule` SHALL require every `.py` module to begin with a module-level docstring summarising its purpose, main exports, and typical usage.
2. THE `DocstringRule` SHALL require every class definition to have a class-level docstring describing its responsibilities and listing all public attributes under an `Attributes:` section.
3. THE `DocstringRule` SHALL require every `__init__` method with non-trivial parameters to have a docstring with `Args:` and `Raises:` sections.
4. THE `DocstringRule` SHALL require every public function and method to have a docstring with `Args:`, `Returns:`, and `Raises:` sections wherever applicable.
5. WHEN a function raises a custom exception, THE docstring `Raises:` section SHALL list that exception class and the condition that triggers it.
6. IF a module, class, or function already has a complete Google-style docstring, THEN THE `DocstringRule` SHALL treat it as compliant without modification.

---

### Requirement 3: Full Type Annotations

**User Story:** As a senior engineer, I want every function parameter and return type annotated with Python type hints, so that static analysis tools (mypy) report zero untyped definition errors.

#### Acceptance Criteria

1. THE `TypeAnnotationRule` SHALL require every function and method parameter to have an explicit type annotation.
2. THE `TypeAnnotationRule` SHALL require every function and method to declare an explicit return type, including `None` where no value is returned.
3. THE `TypeAnnotationRule` SHALL require class attributes set in `__init__` to be annotated, either inline or via class-level variable annotations.
4. WHEN `Optional` types are used, THE code SHALL import `Optional` from `typing` or use the `X | None` syntax available in Python 3.10+.
5. THE `TypeAnnotationRule` SHALL apply to all modules: `app/__init__.py`, `app/config.py`, `app/constants.py`, `app/models/request_models.py`, `app/routes/chat.py`, `app/services/ai_service.py`, `app/utils/cache.py`, `app/utils/exceptions.py`, `app/utils/validators.py`, and `wsgi.py`.

---

### Requirement 4: Cyclomatic Complexity and Single-Responsibility Functions

**User Story:** As a senior engineer, I want no function to exceed 20 lines of executable code, so that each function has a single responsibility and is independently testable.

#### Acceptance Criteria

1. THE `ComplexityRule` SHALL require that no function or method body exceeds 20 executable lines of code.
2. WHEN a function exceeds the 20-line threshold, THE `ComplexityRule` SHALL mandate splitting it into smaller, single-responsibility helper methods with descriptive verb-based names.
3. THE `AIService.generate_response` method SHALL delegate to private helper methods `_build_system_prompt`, `_build_messages`, `_create_completion`, `_extract_content`, and `_validate_response`, each with a single responsibility.
4. THE `validate_chat_request` function in `app/utils/validators.py` SHALL delegate each validation concern (null-byte check, length check, persona check, language check, history check, sanitisation) to a dedicated private helper function.
5. THE `create_app` factory in `app/__init__.py` SHALL register error handlers and security middleware through focused, named inner functions rather than anonymous lambdas.

---

### Requirement 5: Consistent Custom Exception Handling

**User Story:** As a senior engineer, I want every `try/except` block to catch specific named exceptions, log with contextual information, and raise the appropriate `StadiumIQError` subclass, so that error diagnostics are precise and never silently swallow failures.

#### Acceptance Criteria

1. THE `ExceptionRule` SHALL require that no `except` clause uses a bare `except:` without specifying an exception type.
2. THE `ExceptionRule` SHALL require that when catching broad `Exception` is unavoidable (e.g. third-party SDK boundary), the caught exception is logged at `ERROR` level with the originating context before being re-raised as the appropriate `StadiumIQError` subclass.
3. WHEN the Groq client raises any exception, THE `AIService` SHALL catch that specific exception, log the error with attempt number and model name, and raise `AIServiceError` with the original cause chained.
4. WHEN cache operations fail, THE `LRUCache` SHALL catch `Exception`, log the error, and raise `CacheError` with the original cause chained.
5. WHEN input validation fails, THE `Validator` SHALL raise `ValidationError` with a descriptive message from the `Constants` module.
6. THE `Constants` module SHALL define a `TransportationError` exception for transportation data resolution failures, and it SHALL be a subclass of `StadiumIQError`.
7. WHEN structured logging is used, THE logger SHALL include at minimum the module name, function name, and relevant input identifiers (e.g. persona, city name) as extra fields.

---

### Requirement 6: Persona System Prompts — Full Use-Case Coverage

**User Story:** As a product owner, I want the system prompt for each persona to cover every use case documented in the problem statement, so that the AI assistant provides accurate, complete guidance for all four user roles.

#### Acceptance Criteria

1. THE `Fan` persona system prompt SHALL cover: stadium navigation, gate assignments (general/family/VIP/accessibility), food and beverage locations, transportation (shuttles, public transit, parking, rideshare zones), match schedules, fan zones, accessibility services, sustainability tips, and multilingual support across all 8 supported languages.
2. THE `Staff` persona system prompt SHALL cover: real-time crowd density monitoring, capacity threshold warnings (Low/Moderate/High), suggested operational actions, incident response recommendations, weather impact on operations, dynamic queue management, shift management, resource allocation, emergency protocols, interdepartmental communication, and KPI monitoring.
3. THE `Volunteer` persona system prompt SHALL cover: role assignments, multilingual fan support for all 8 supported languages, accessibility assistance, wayfinding, shift coordination, emergency procedures, sustainability initiatives, and crowd flow guidance.
4. THE `Accessibility` persona system prompt SHALL cover: wheelchair-accessible routes and entrances for all 16 host cities, accessible transportation options including priority pickup zones, sensory-friendly spaces, hearing and visual assistance devices, medical support access, companion seating, real-time coordination with staff, and dignity-first interaction principles.
5. THE `Fan` persona system prompt SHALL reference all 16 FIFA 2026 host cities and their corresponding stadiums when providing venue-specific guidance.
6. THE `Staff` persona system prompt SHALL reference FIFA 2026 match phases (Group Stage, Round of 32, Quarter-finals, Semi-finals, Final) and their associated operational intensity levels.

---

### Requirement 7: FIFA 2026 Specificity — 16 Host Cities

**User Story:** As a product owner, I want the application to explicitly reference all 16 FIFA World Cup 2026 host cities, so that the system provides accurate, city-specific guidance for every venue in the tournament.

#### Acceptance Criteria

1. THE `Constants` module SHALL list the 16 host cities as: New York/New Jersey, Los Angeles, Dallas, San Francisco Bay Area, Miami, Seattle, Boston, Houston, Kansas City, Philadelphia, Toronto, Vancouver, Mexico City, Guadalajara, Monterrey, and Atlanta.
2. THE `Constants` module SHALL map each of the 16 host cities to its corresponding stadium in `FIFA_2026_STADIUMS`.
3. THE `TRANSPORT_INFO` constant SHALL contain a transportation data entry for every one of the 16 host cities, covering shuttle schedules, parking zones, rideshare pickup zones, and accessible transport.
4. WHEN a Fan or Accessibility user asks about a specific host city, THE `AIService` SHALL provide city-specific transportation, navigation, and venue details sourced from the constants.
5. THE match schedule table in the `NavigationPanel` SHALL display representative matches across all 16 host city venues.

---

### Requirement 8: Separation of Concerns — Routes, Services, Utils

**User Story:** As a senior engineer, I want HTTP handling, business logic, and helper utilities strictly separated, so that each layer is independently testable and future changes in one layer do not break others.

#### Acceptance Criteria

1. THE `ChatRoute` module SHALL contain only Flask route handler functions; it SHALL NOT contain business logic, AI prompting, data transformation, or validation logic beyond calling the appropriate service or utility function.
2. THE `AIService` SHALL contain all AI prompting, message building, retry logic, and response validation logic; it SHALL NOT import Flask or handle HTTP concerns.
3. THE `Validator` module SHALL contain all input validation and sanitisation logic; it SHALL NOT call external services or perform I/O operations.
4. THE `LRUCache` SHALL contain only thread-safe cache get/set/clear operations; it SHALL NOT import application business logic.
5. THE `Constants` module SHALL contain only constant definitions; it SHALL NOT contain any executable logic, conditional statements, or function calls at module level (except comprehensions used to initialise derived constants).
6. WHEN a new route-level concern arises (e.g. session ID generation), THE `ChatRoute` module SHALL implement it as a call to a dedicated utility function rather than inline logic.

---

### Requirement 9: Variable Naming and Boolean Conventions

**User Story:** As a senior engineer, I want all variables, functions, and booleans to follow consistent, descriptive naming conventions, so that code reads as self-documenting prose.

#### Acceptance Criteria

1. THE `NamingRule` SHALL require that no variable name consists of a single letter (except loop indices `i`, `j`, `k` in comprehensions or short numeric iterations).
2. THE `NamingRule` SHALL require that boolean variables and properties are named with an `is_`, `has_`, or `can_` prefix (for example `is_configured`, `has_api_key`, `can_retry`).
3. THE `NamingRule` SHALL require that all function and method names start with a verb (for example `generate_response`, `validate_chat_request`, `build_messages`).
4. THE `NamingRule` SHALL require that no abbreviation obscures meaning (for example `msg` is acceptable; `idx` is acceptable; `cfg` is not — use `config`).
5. WHEN a function parameter name conflicts with a Python built-in (for example `type`, `id`, `input`), THE `NamingRule` SHALL require a descriptive alternative (for example `error_type`, `session_id`, `user_input`).

---

### Requirement 10: Dedicated Transportation Assistant Feature

**User Story:** As a fan or accessibility user, I want a dedicated transportation assistant, so that I can find shuttle schedules, public transit options, parking zones, rideshare pickup points, and accessible transport for my specific host city.

#### Acceptance Criteria

1. THE `Constants` module SHALL provide complete transportation data for all 16 host cities in `TRANSPORT_INFO`, including shuttle schedule descriptions, parking zone descriptions, rideshare zone descriptions, and accessible transport descriptions.
2. WHEN a user asks a transportation-related query, THE `AIService` SHALL use transportation data from `TRANSPORT_INFO` in the context of the appropriate persona prompt.
3. THE `TransportationTab` frontend panel SHALL display an interactive transport guide per host city, showing shuttle schedules, parking zones, rideshare info, and accessible transport options for the selected city.
4. THE `TransportationTab` SHALL be navigable from the desktop sidebar and mobile bottom navigation without breaking the existing five-panel layout.
5. WHEN a user selects a host city in the `TransportationTab`, THE panel SHALL update to show the transportation details for that city without a page reload.
6. IF transportation data for a requested city is not available, THEN THE `AIService` SHALL raise `TransportationError` and return a user-friendly error message.

---

### Requirement 11: Real-Time Decision Support — Crowd Management

**User Story:** As a staff member, I want real-time crowd density alerts with suggested operational actions, so that I can manage crowd flow, prevent bottlenecks, and respond to incidents proactively.

#### Acceptance Criteria

1. THE `CrowdManagementPanel` SHALL display a crowd density gauge showing Low (green, 0–40%), Moderate (yellow, 41–75%), or High (red, 76–100%) states.
2. THE `CrowdManagementPanel` SHALL display a colour-coded zone map using green, yellow, and red indicators per stadium zone.
3. WHEN crowd density reaches the High threshold (above 75%), THE `CrowdManagementPanel` SHALL automatically display threshold recommendations and evacuation route suggestions.
4. WHEN the "Recalculate Flow" button is activated, THE `CrowdSimulator` SHALL generate a new crowd density state and update all visual indicators, metric bars, and alert messages atomically.
5. THE `Staff` persona system prompt SHALL include guidance for crowd density thresholds, suggested actions per level, incident response steps, and dynamic queue management strategies.
6. THE `CrowdManagementPanel` SHALL display a "Decision Support Evacuation Steps" section that is updated based on the current density level.

---

### Requirement 12: Real-Time Alerts Banner

**User Story:** As any user, I want to see real-time simulated alerts for crowd, weather, and transport events, so that I stay informed about conditions that affect my stadium experience.

#### Acceptance Criteria

1. THE `AlertBanner` SHALL be displayed above the AI Chat panel as a dismissible strip.
2. THE `AlertBanner` SHALL support three severity levels: Info (blue), Warning (yellow), and Critical (red), each visually distinguished by colour coding.
3. WHEN an alert is displayed, THE `AlertBanner` SHALL include a close/dismiss button that removes it from view without disrupting the underlying chat interface.
4. THE `AlertBanner` SHALL simulate at least three alert scenarios: crowd density warning, weather impact notice, and transport delay notification.
5. THE `AlertBanner` SHALL be accessible with `role="alert"` and `aria-live="assertive"` for screen reader support.
6. WHEN multiple alerts are active simultaneously, THE `AlertBanner` SHALL display them in a stacked, scrollable area with the most critical alert at the top.

---

### Requirement 13: FIFA 2026-Specific Navigation Panel

**User Story:** As a fan, I want the Stadium Navigation panel to show FIFA 2026-specific gate assignments, accessibility entrances, VIP vs general areas, emergency exits, and medical stations, so that I can navigate any host city venue with confidence.

#### Acceptance Criteria

1. THE `NavigationPanel` zone map SHALL label gate zones with FIFA 2026 terminology: general admission gates, accessibility entrances, VIP/sponsor entrances, and media gates.
2. THE `NavigationPanel` zone details SHALL include the nearest medical station location for each zone.
3. THE `NavigationPanel` SHALL display a host city selector allowing users to switch between the 16 FIFA 2026 host venues, updating zone labels and details accordingly.
4. THE `NavigationPanel` zone details SHALL differentiate between General Admission, Family Zone, VIP/Press, and Accessibility sections for each zone.
5. THE `NavigationPanel` SVG map SHALL include distinct marker types for: gate entrances (gold), accessibility entrances (green), emergency exits (red), and medical stations (blue).
6. WHEN a user selects a zone on the SVG map, THE `NavigationPanel` SHALL display zone-specific details including gate number, section type, nearest amenities, accessibility features, and emergency exit routes.

---

### Requirement 14: Quick Action Buttons

**User Story:** As any user, I want pre-filled quick action buttons in the chat panel, so that I can immediately ask common questions without typing.

#### Acceptance Criteria

1. THE `ChatPanel` SHALL display exactly five quick action buttons: "Find nearest exit", "Transport options", "Crowd status", "Emergency help", and "Accessibility services".
2. WHEN a quick action button is activated, THE `ChatPanel` SHALL pre-fill the chat input with a contextual query appropriate for the currently selected persona and submit it to the AI assistant.
3. THE quick action buttons SHALL be keyboard-navigable and meet WCAG 2.1 AA accessibility requirements including `aria-label` attributes and visible focus indicators.
4. THE quick action buttons SHALL remain visible and functional regardless of the currently selected persona or language.
5. WHEN a quick action query is submitted, THE `ChatPanel` SHALL behave identically to a manually typed message, using the current persona, language, and conversation history.

---

### Requirement 15: FIFA Branding Elements

**User Story:** As a product owner, I want the UI to display FIFA World Cup 2026 branding elements including tournament phase, host city selector, and current/upcoming match context, so that the application feels authoritative and specific to the 2026 tournament.

#### Acceptance Criteria

1. THE `AppHeader` SHALL display a FIFA World Cup 2026 logo area with the trophy icon and "FIFA World Cup 2026" sub-brand text.
2. THE `AppHeader` SHALL include a host city selector showing all 16 FIFA 2026 host cities, allowing the user to set a venue context that personalises assistant responses.
3. THE `ChatPanel` header SHALL display the current tournament phase (Group Stage, Round of 32, Quarter-finals, Semi-finals, or Final) as a contextual label.
4. THE `MatchSchedulePanel` SHALL list representative matches for all 16 host cities, displaying Match ID, host city, stadium, date, and featured teams.
5. THE branding elements SHALL not alter the existing visual design system (colours, typography, layout grid) established in `static/style.css`.

---

### Requirement 16: Zero Code Duplication

**User Story:** As a senior engineer, I want the DRY principle enforced across all Python source files, so that no business logic or validation pattern appears in more than one location.

#### Acceptance Criteria

1. THE `DRYRule` SHALL require that persona prompt lookup logic exists only in `AIService._build_system_prompt`, which reads from `PERSONA_SYSTEM_PROMPTS` in `Constants`.
2. THE `DRYRule` SHALL require that message history truncation logic exists only in `AIService._build_messages`.
3. THE `DRYRule` SHALL require that input sanitisation (HTML escaping, null-byte rejection) exists only in the dedicated helper functions within `app/utils/validators.py`.
4. THE `DRYRule` SHALL require that HTTP status code integers appear only as named constants from `app.constants`, never as numeric literals in route handlers or error handlers.
5. THE `DRYRule` SHALL require that the list of supported languages and supported personas is defined only in `app/constants.py` and referenced everywhere else via import.

---

### Requirement 17: Structured Logging

**User Story:** As a senior engineer, I want structured logging on every significant operation, so that production incidents can be diagnosed from log output alone.

#### Acceptance Criteria

1. THE `LoggingRule` SHALL require that every module that performs I/O, external API calls, or significant business logic initialises a `logging.Logger` with `logging.getLogger(__name__)`.
2. WHEN the `AIService` initiates a Groq API call, THE logger SHALL emit an `INFO` log including the attempt number and model name.
3. WHEN the `AIService` encounters an exception during a retry, THE logger SHALL emit a `WARNING` log including the attempt number, exception type, and exception message.
4. WHEN the `ChatRoute` receives a valid request, THE logger SHALL emit a `DEBUG` log including persona, language, and whether the response was served from cache.
5. WHEN a `ValidationError` is raised, THE logger SHALL emit a `WARNING` log including the field that failed validation and the reason.
6. WHEN an `AIServiceError` is raised and handled by the error handler, THE logger SHALL emit an `ERROR` log including the original exception message.

---

### Requirement 18: Defensive Programming and Input Boundary Validation

**User Story:** As a senior engineer, I want all system boundaries to validate inputs defensively, so that malformed, malicious, or unexpected data never propagates into business logic.

#### Acceptance Criteria

1. THE `Validator` SHALL validate that the `message` field is a non-empty string after stripping whitespace, does not contain null bytes, does not exceed `MAX_MESSAGE_LENGTH`, and does not consist entirely of repeated tokens (spam detection).
2. THE `Validator` SHALL validate that the `persona` field is one of the four supported personas defined in `SUPPORTED_PERSONAS`.
3. THE `Validator` SHALL validate that the `language` field is either a supported language from `SUPPORTED_LANGUAGES` or triggers auto-detection when empty or set to `"auto"`.
4. THE `Validator` SHALL validate that the `history` field is a list of dictionaries, each containing string `role` and `content` keys, with no null bytes.
5. WHEN validation fails on any field, THE `Validator` SHALL raise `ValidationError` using the corresponding error message constant from `app.constants`.
6. THE `AIService.__init__` method SHALL validate that `config.GROQ_API_KEY` is non-empty before constructing the Groq client, raising `AIServiceError` if it is absent.
7. THE `LRUCache.__init__` method SHALL validate that `max_size` is a positive integer, raising `ValueError` if it is not.

---

### Requirement 19: All Existing Tests Pass

**User Story:** As a senior engineer, I want all existing and new tests to pass after improvements are applied, so that the quality improvements do not introduce regressions.

#### Acceptance Criteria

1. THE `TestSuite` SHALL pass all tests in `tests/test_app.py`, `tests/test_accessibility.py`, and `tests/test_security.py` after all code quality and problem-statement improvements are applied.
2. THE `TestSuite` SHALL continue to enforce that `test_chat_returns_session_id` passes, meaning the `/chat` endpoint returns a `session_id` field in its response.
3. THE `TestSuite` SHALL continue to enforce that `test_repetitive_message_is_rejected` passes, meaning the validator rejects highly repetitive messages with a 400 status.
4. WHEN any new feature (Transportation tab, AlertBanner, QuickActions) is added, THE `TestSuite` SHALL include at least one test verifying the new endpoint or behaviour.
5. THE `TestSuite` SHALL pass without any modification to existing test assertions unless an existing test was verifying incorrect behaviour.

/**
 * StadiumIQ Frontend JavaScript — FIFA World Cup 2026 Smart Stadium Assistant.
 *
 * Implements: persona/language selectors, panel navigation (GSAP), Three.js
 * particle background, HTML5 Canvas crowd density simulator, real-time alerts
 * banner, transportation tab, FIFA branding updates, quick-action buttons, and
 * the AI assistant chat interface.
 *
 * All magic values are declared as named constants at the top of this file.
 */

"use strict";

// ==========================================================================
// CONSTANTS
// ==========================================================================

/** Maximum conversation history turns kept in memory. */
const MAX_HISTORY_TURNS = 20;

/** Crowd density thresholds (0–1 scale). */
const DENSITY_LOW_MAX = 0.40;
const DENSITY_MODERATE_MAX = 0.75;

/** Number of Three.js background particles. */
const PARTICLE_COUNT = 250;

/** Transportation data for all 16 FIFA 2026 host cities. */
const TRANSPORT_DATA = {
    "New York/New Jersey": {
        shuttle: "NJ Transit and dedicated stadium shuttles from Penn Station every 15 min",
        parking: "MetLife Stadium lots A–G with EV charging stations",
        rideshare: "Designated pickup zones at Gate D; follow yellow signage",
        accessible: "Accessible shuttle drop-off at Gate C; priority boarding available"
    },
    "Los Angeles": {
        shuttle: "SoFi Stadium express shuttles from Metro C Line and park-and-ride hubs",
        parking: "Premium parking decks P1–P5 with accessible drop-off lanes",
        rideshare: "North lot rideshare queue and mobility pickup points near Gate 5",
        accessible: "ADA transport shuttles from Inglewood Transit Center; step-free boarding"
    },
    "Dallas": {
        shuttle: "AT&T Stadium transit loops from downtown Dallas every 20 min",
        parking: "North and south overflow lots N1–N8 with rapid shuttle service",
        rideshare: "North gateway pickup area near Gate A for priority access",
        accessible: "Adapted vehicle drop-off at ADA lot; escort service available on request"
    },
    "San Francisco Bay Area": {
        shuttle: "Levi's Stadium BART-connected shuttle routes from Milpitas and Berryessa",
        parking: "Overflow parking lots P1–P6 adjacent to the transit hub",
        rideshare: "Dedicated rideshare lane near Gate 3; 10-min walk from transit",
        accessible: "Accessible shuttle from Great America light rail; low-floor buses"
    },
    "Miami": {
        shuttle: "Hard Rock Stadium park-and-ride corridors and tram links from Aventura",
        parking: "ADA-friendly lots A–D with priority access lanes and paved paths",
        rideshare: "Mobility pickup zone by the east concourse; blue signage",
        accessible: "Priority accessible shuttle from Dolphin Station; sensory-friendly boarding"
    },
    "Seattle": {
        shuttle: "Light rail feeder from Lumen Field and stadium shuttle service on game day",
        parking: "Secure parking garages G1–G4 with real-time guidance signage",
        rideshare: "South plaza pickup and drop-off bay; 5-min walk to main entrance",
        accessible: "Accessible drop-off at south entrance; companion parking available"
    },
    "Boston": {
        shuttle: "Gillette Stadium commuter shuttles from Foxboro and MBTA Stoughton Line",
        parking: "Remote parking areas R1–R5 with rapid transfer buses",
        rideshare: "North gate pickup lane; pre-staged rideshare zones marked in blue",
        accessible: "Accessible shuttle from Attleboro station; wheelchair-secured vehicles"
    },
    "Houston": {
        shuttle: "NRG Stadium express buses to Midtown and downtown every 10 min",
        parking: "Wide-access parking zones W1–W6 with wayfinding boards and EV stations",
        rideshare: "Ride-share queue near the west plaza; covered waiting area",
        accessible: "ADA lot with direct elevator access; METRO Lift drop-off at Gate B"
    },
    "Kansas City": {
        shuttle: "Arrowhead Stadium shuttle loops for downtown visitors and park-and-ride",
        parking: "Premium lots P1–P4 and general lots G1–G8 with real-time occupancy signs",
        rideshare: "Drop-off lane adjacent to the south entrance; follow red signage",
        accessible: "Low-floor shuttle from Union Station; accessible parking in ADA lot"
    },
    "Philadelphia": {
        shuttle: "Lincoln Financial Field SEPTA Broad Street Line feeder services",
        parking: "Surface lots L1–L10 with e-scooter and Pattison Station bus connections",
        rideshare: "Designated queue near the east concourse; 3-min walk from Pattison stop",
        accessible: "Accessible transport via SEPTA Access service; ADA drop-off at Gate 3"
    },
    "Toronto": {
        shuttle: "BMO Field streetcar and GO Transit feeder shuttles from Union Station",
        parking: "Accessible parking with step-free routes and companion bays",
        rideshare: "Priority pickup at the south gate; TTC designated rideshare stop",
        accessible: "Wheel-Trans service available; accessible boardwalk from Exhibition GO"
    },
    "Vancouver": {
        shuttle: "BC Place SkyTrain-connected shuttle from Stadium–Chinatown station",
        parking: "Coastal parking zones C1–C4 with bike valet and EV charging support",
        rideshare: "Rideshare lane by the west access plaza; HandyDART drop-off nearby",
        accessible: "HandyDART and accessible cab services; step-free route from SkyTrain"
    },
    "Mexico City": {
        shuttle: "Estadio Azteca Metro Line 2 and mobility shuttle connections from Tasqueña",
        parking: "Multi-level covered parking with bilingual wayfinding and EV zones",
        rideshare: "Controlled pickup zone at Gate 7; app-based services pre-approved",
        accessible: "LICONSA accessible bus service; adapted taxi stand at Gate C"
    },
    "Guadalajara": {
        shuttle: "Estadio Akron dedicated civic shuttle loops from Minerva Circle",
        parking: "North and south lots N1–N4 with accessible drop-off lanes",
        rideshare: "Priority pickup by the civic entrance; InDriver and Uber designated zones",
        accessible: "Adapted transport via Guadalajara Mobility Unit; ADA drop-off at Gate A"
    },
    "Monterrey": {
        shuttle: "Estadio BBVA airport-linked shuttle services from Monterrey International",
        parking: "Structured lots S1–S5 with sustainability information points",
        rideshare: "Central pickup zone near the main walkway; 2-min walk from bus terminal",
        accessible: "Accessible shuttle from Metrorrey San Bernabé station; priority boarding"
    },
    "Atlanta": {
        shuttle: "Mercedes-Benz Stadium MARTA-connected shuttles from Five Points and Vine City",
        parking: "Premium lots P1–P6 with EV charging and real-time occupancy signage",
        rideshare: "Designated rideshare drop-off at Gate 1 and Gate 5; follow blue signage",
        accessible: "MARTA Mobility service; ADA parking with direct elevator access at Gate 3"
    }
};

/** Simulated alert messages at three severity levels. */
const ALERT_SCENARIOS = [
    { severity: "info",     color: "#3498db", text: "ℹ Gate B now open — general admission queues moving smoothly." },
    { severity: "warning",  color: "#f39c12", text: "⚠ Crowd density at 74% near East Stand. Alternate routes: Gate C or Gate A." },
    { severity: "critical", color: "#c0392b", text: "🚨 Transport delay: NJ Transit shuttle delayed 15 min. Uber/Lyft zones active." },
    { severity: "info",     color: "#3498db", text: "ℹ Medical station at North Concourse is now fully operational." },
    { severity: "warning",  color: "#f39c12", text: "⚠ Weather alert: Rain expected at kickoff. Covered exits recommended." },
    { severity: "critical", color: "#c0392b", text: "🚨 High crowd density (86%) detected. Staff: activate Queue Management Protocol." }
];

/** Global application state. */
const state = {
    persona: "Fan",
    language: "English",
    history: [],
    currentPanel: "panel-chat",
    crowdDensity: 0.54,
    simulatingCrowd: true,
    selectedCity: "",
    citiesData: {
        "Mexico City":          { stadium: "Estadio Azteca",        capacity: "87,523", sustainability: "Rainwater harvesting, LED lighting, integrated public transport hub.", accessibility: "Ramp access, tactile paving, dedicated volunteer teams." },
        "Toronto":              { stadium: "BMO Field",              capacity: "30,000", sustainability: "Hybrid grass system, zero-waste stations, streetcar/light-rail lines.", accessibility: "Elevators to all levels, accessible seating boxes, audio-described commentary." },
        "Los Angeles":          { stadium: "SoFi Stadium",           capacity: "70,240", sustainability: "Recycled water irrigation, energy-efficient LED, solar generation.", accessibility: "Open captioning screens, assistive listening, ADA transport shuttles." },
        "Dallas":               { stadium: "AT&T Stadium",           capacity: "80,000", sustainability: "Smart HVAC, food waste composting, eco-friendly transit loops.", accessibility: "Dedicated elevators, accessible ticketing, tactile pathways." },
        "Miami":                { stadium: "Hard Rock Stadium",      capacity: "64,767", sustainability: "99.4% single-use plastic eliminated, solar canopy, local eco-shuttles.", accessibility: "Sensory-inclusive certification, companion seating, ADA loops." },
        "New York/New Jersey":  { stadium: "MetLife Stadium",        capacity: "82,500", sustainability: "100% wind-powered, zero waste, train/rail access.", accessibility: "Sensory rooms, fully wheelchair-accessible seating, designated access gates." },
        "Seattle":              { stadium: "Lumen Field",            capacity: "68,740", sustainability: "Green roof systems, LEED certified, local transit integration.", accessibility: "Accessible elevators, companion seating, assisted mobility services." },
        "Boston":               { stadium: "Gillette Stadium",       capacity: "65,878", sustainability: "Solar farm on-site, EV charging stations, composting programme.", accessibility: "ADA-compliant seating, sensory room, accessible concessions." },
        "Houston":              { stadium: "NRG Stadium",            capacity: "72,220", sustainability: "Green building certification, energy management systems.", accessibility: "Mobility assistance programme, audio description, accessible food service." },
        "Kansas City":          { stadium: "Arrowhead Stadium",      capacity: "76,416", sustainability: "Fan eco-challenge programme, recycling at all concourses.", accessibility: "Low-row accessible seating, shuttle from accessible parking." },
        "Philadelphia":         { stadium: "Lincoln Financial Field", capacity: "69,796", sustainability: "Wind turbines, solar panels, natural gas cogeneration system.", accessibility: "Accessible ramps throughout, Braille signage, ADA ticketing." },
        "San Francisco Bay Area": { stadium: "Levi's Stadium",       capacity: "68,500", sustainability: "LEED Gold certified, solar panels, paperless ticketing.", accessibility: "ADA shuttle, companion care room, accessible viewing platforms." },
        "Vancouver":            { stadium: "BC Place",               capacity: "54,500", sustainability: "Retractable roof reduces heating energy, recycled water systems.", accessibility: "Elevator access, real-time captioning, tactile paths." },
        "Guadalajara":          { stadium: "Estadio Akron",          capacity: "49,850", sustainability: "Native landscaping, LED conversion, fan carbon offset programme.", accessibility: "Adapted seating, accessible washrooms, bilingual assistance." },
        "Monterrey":            { stadium: "Estadio BBVA",           capacity: "53,500", sustainability: "Smart water system, green roof, zero single-use plastics.", accessibility: "Accessible entrances, low-floor shuttles, mobility assistance desks." },
        "Atlanta":              { stadium: "Mercedes-Benz Stadium",  capacity: "71,000", sustainability: "LEED Platinum, on-site solar, 100% recycled water irrigation.", accessibility: "Full ADA compliance, Braille guides, companion seats, low-floor MARTA access." }
    },
    zoneDetails: {
        "zone-north": {
            title: "North Stand — General Admission (Gate A)",
            features: [
                "Gate Type: General Admission — Gate A (main north entrance)",
                "Ticket Sections: 100–120, upper bowl 200–220",
                "Parking: North Lot P1–P3 (EV charging available)",
                "Medical Station: North Concourse Level 1, Section 110",
                "Accessibility: Standard wheelchair ramp at Gate A2",
                "Emergency Exit: Direct exits toward North Parking Area — follow green signs"
            ]
        },
        "zone-east": {
            title: "East Stand — Family Zone (Gate B)",
            features: [
                "Gate Type: Family & Groups — Gate B",
                "Ticket Sections: 130–150 (family zone), upper bowl 230–250",
                "Parking: East Park & Ride Lot (shuttle every 10 min)",
                "Medical Station: East Concourse Level 1, near Gate B4",
                "Accessibility: Tactile path guidance for vision-impaired fans",
                "Emergency Exit: Tunnels leading directly to East Concourse Plaza"
            ]
        },
        "zone-south": {
            title: "South Stand — Accessibility Entrance (Gate C)",
            features: [
                "Gate Type: Special Assistance & Wheelchair Entry — Gate C (priority access)",
                "Ticket Sections: Accessible seating 160–180, companion rows",
                "Parking: ADA Designated Parking Lot (shuttle from gate every 5 min)",
                "Medical Station: South Stand dedicated medical desk + sensory room",
                "Accessibility: Low-grade ramps, 4 accessible elevator shafts, hearing loops",
                "Emergency Exit: Dedicated fire-safe evacuation elevators and wide ramps"
            ]
        },
        "zone-west": {
            title: "West Stand — VIP & Media Suite (Gate D)",
            features: [
                "Gate Type: VIP, Press & Sponsor entrance — Gate D (credential required)",
                "Ticket Sections: VIP boxes 170–190, media tribune Level 3",
                "Parking: VIP West Valet (pre-booked only)",
                "Medical Station: VIP Level 2 medical suite adjacent to hospitality lounge",
                "Accessibility: Full elevator connectivity to VIP balconies and press area",
                "Emergency Exit: Press elevators and dedicated emergency exit stairs"
            ]
        }
    }
};

// ==========================================================================
// 1. THREE.JS PARTICLE BACKGROUND
// ==========================================================================

/**
 * Initialise the Three.js particle background on the bg-canvas element.
 * Skips gracefully if the canvas is absent.
 */
function initThreeParticles() {
    const canvas = document.getElementById("bg-canvas");
    if (!canvas) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const colors = new Float32Array(PARTICLE_COUNT * 3);
    const colorChoices = [
        new THREE.Color(0xc9a84c),
        new THREE.Color(0xc0392b),
        new THREE.Color(0x3498db)
    ];

    for (let index = 0; index < PARTICLE_COUNT * 3; index += 3) {
        positions[index]     = (Math.random() - 0.5) * 15;
        positions[index + 1] = (Math.random() - 0.5) * 15;
        positions[index + 2] = (Math.random() - 0.5) * 15;
        const pickedColor = colorChoices[Math.floor(Math.random() * colorChoices.length)];
        colors[index]     = pickedColor.r;
        colors[index + 1] = pickedColor.g;
        colors[index + 2] = pickedColor.b;
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
        size: 0.08, vertexColors: true, transparent: true,
        opacity: 0.7, blending: THREE.AdditiveBlending
    });

    const particleSystem = new THREE.Points(geometry, material);
    scene.add(particleSystem);
    camera.position.z = 5;

    function animateParticles() {
        requestAnimationFrame(animateParticles);
        particleSystem.rotation.y += 0.001;
        particleSystem.rotation.x += 0.0005;
        renderer.render(scene, camera);
    }
    animateParticles();

    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// ==========================================================================
// 2. CROWD DENSITY SIMULATOR (HTML5 Canvas)
// ==========================================================================

class CrowdSimulator {
    constructor() {
        this.canvas = document.getElementById("crowd-canvas");
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext("2d");
        this.dots = [];
        this.maxDots = 100;
        this.initCanvasSize();
        this.createCrowdDots();
        this.animate();
        window.addEventListener("resize", () => this.initCanvasSize());
    }

    /** Resize the canvas to fill its parent container. */
    initCanvasSize() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight || 350;
    }

    /** Create dot agents scaled to the current crowd density. */
    createCrowdDots() {
        this.dots = [];
        this.maxDots = Math.floor(state.crowdDensity * 220) + 30;
        for (let dotIndex = 0; dotIndex < this.maxDots; dotIndex++) {
            this.dots.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 1.5,
                vy: (Math.random() - 0.5) * 1.5,
                radius: Math.random() * 3 + 2,
                color: this.getDotColor()
            });
        }
    }

    /** Return a dot colour matching the current density level. */
    getDotColor() {
        if (state.crowdDensity > DENSITY_MODERATE_MAX) return "rgba(192, 57, 43, 0.7)";
        if (state.crowdDensity > DENSITY_LOW_MAX)      return "rgba(243, 156, 18, 0.7)";
        return "rgba(46, 204, 113, 0.7)";
    }

    /** Run the animation loop for the crowd simulation canvas. */
    animate() {
        if (!state.simulatingCrowd) return;
        requestAnimationFrame(() => this.animate());

        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;

        ctx.clearRect(0, 0, width, height);

        ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
        ctx.lineWidth = 2;
        for (let xPos = 50; xPos < width; xPos += 100) {
            ctx.beginPath(); ctx.moveTo(xPos, 0); ctx.lineTo(xPos, height); ctx.stroke();
        }
        for (let yPos = 50; yPos < height; yPos += 100) {
            ctx.beginPath(); ctx.moveTo(0, yPos); ctx.lineTo(width, yPos); ctx.stroke();
        }

        ctx.fillStyle = "rgba(46, 204, 113, 0.25)";
        ctx.font = "bold 13px Plus Jakarta Sans, system-ui, sans-serif";
        ctx.fillText("EXIT C (South)", 20, height - 20);
        ctx.fillText("EXIT A (North)", 20, 36);

        this.dots.forEach(dot => {
            dot.x += dot.vx;
            dot.y += dot.vy;
            if (dot.x < 0 || dot.x > width)  dot.vx *= -1;
            if (dot.y < 0 || dot.y > height) dot.vy *= -1;

            ctx.beginPath();
            ctx.arc(dot.x, dot.y, dot.radius, 0, Math.PI * 2);
            ctx.fillStyle = dot.color;
            ctx.shadowColor = dot.color;
            ctx.shadowBlur = 4;
            ctx.fill();
            ctx.shadowBlur = 0;
        });
    }

    /**
     * Recalculate crowd density, update all metric UI elements, and
     * refresh the decision-support evacuation steps.
     */
    recalculate() {
        const densityOptions = [0.28, 0.54, 0.86];
        const labelOptions   = ["Low (28%)", "Moderate (54%)", "High (86%)"];
        const colorOptions   = ["#2ecc71", "#f39c12", "#c0392b"];
        const badgeStyles    = [
            { bg: "rgba(46,204,113,0.15)", border: "rgba(46,204,113,0.4)",   color: "#2ecc71", icon: "✅", label: "LOW — Standard protocols active" },
            { bg: "rgba(243,156,18,0.15)", border: "rgba(243,156,18,0.4)",   color: "#f39c12", icon: "⚠",  label: "MODERATE — Moderate operational protocols active" },
            { bg: "rgba(192,57,43,0.15)",  border: "rgba(192,57,43,0.4)",    color: "#c0392b", icon: "🚨", label: "HIGH — FULL crowd management protocols engaged" }
        ];

        const densityAlerts = [
            `<div class="alert-item success"><i class="fa-solid fa-circle-check" aria-hidden="true"></i><div><strong>Optimal Crowd Density</strong><p>Low congestion throughout all concourses. Green transport shuttles departing continuously.</p></div></div>`,
            `<div class="alert-item warning"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i><div><strong>Gate B Congestion</strong><p>High traffic density near east stand. Safe alternate: Route via South Gate C.</p></div></div><div class="alert-item success"><i class="fa-solid fa-circle-check" aria-hidden="true"></i><div><strong>Evacuation Routes Clear</strong><p>Emergency exits and elevator banks fully clear. Accessibility flows optimal.</p></div></div>`,
            `<div class="alert-item warning" style="background:rgba(192,57,43,0.15);border-color:rgba(192,57,43,0.3);color:#c0392b;"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i><div><strong>CONGESTION ALERT: All Exit Zones Heavy</strong><p>Crowd at 86% capacity. Activating real-time decision support. Divert fans to secondary transit hubs immediately.</p></div></div><div class="alert-item warning"><i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i><div><strong>Gate A and Gate D Queues (30 min+)</strong><p>Recommend Gate C South Stand for elevator-accessible egress flow.</p></div></div>`
        ];

        const evacuationSteps = [
            ["Monitor zone density gauges every 5 minutes.", "Refer to green indicator exit routes on the stadium map.", "Keep corridors clear for accessibility users.", "Maintain standard staffing levels at all gates."],
            ["Alert sector supervisor of Gate B congestion immediately.", "Activate alternate routing via Gate C and Gate A.", "Deploy additional stewards to East Stand concourse.", "Notify transport hub of increased outbound demand.", "Keep corridors and ramps clear for wheelchair and mobility users."],
            ["Initiate full Crowd Management Protocol — notify all departments.", "Activate overflow gates E and F immediately.", "Deploy all on-call stewards to main concourse.", "Coordinate with transport hub for emergency shuttle dispatch.", "Broadcast stadium-wide PA guidance on alternate exits.", "Ensure medical teams are on standby at all four concourse stations."]
        ];

        const selectedIndex = Math.floor(Math.random() * densityOptions.length);
        state.crowdDensity = densityOptions[selectedIndex];

        document.getElementById("metric-density-val").textContent = labelOptions[selectedIndex];
        const densityBar = document.getElementById("metric-density-bar");
        densityBar.style.width = `${densityOptions[selectedIndex] * 100}%`;
        densityBar.style.backgroundColor = colorOptions[selectedIndex];

        const badge = document.getElementById("density-level-badge");
        const badgeStyle = badgeStyles[selectedIndex];
        badge.style.background = badgeStyle.bg;
        badge.style.borderColor = badgeStyle.border;
        badge.style.color = badgeStyle.color;
        badge.textContent = `${badgeStyle.icon} ${badgeStyle.label}`;

        document.getElementById("density-alerts-box").innerHTML = densityAlerts[selectedIndex];

        const evacList = document.getElementById("evac-steps-list");
        if (evacList) {
            evacList.innerHTML = evacuationSteps[selectedIndex]
                .map(step => `<li>${step}</li>`)
                .join("");
        }

        this.createCrowdDots();
    }
}

// ==========================================================================
// 3. REAL-TIME ALERTS BANNER
// ==========================================================================

/**
 * Initialise the alerts banner and show two staggered simulated alerts on load.
 */
function initAlertsBanner() {
    showAlert(ALERT_SCENARIOS[2]);
    setTimeout(() => showAlert(ALERT_SCENARIOS[1]), 3000);
}

/**
 * Display a single alert in the banner, ordered by severity (critical first).
 *
 * @param {{ severity: string, color: string, text: string }} alertData
 */
function showAlert(alertData) {
    const banner = document.getElementById("alerts-banner");
    const alertsList = document.getElementById("alerts-list");
    if (!banner || !alertsList) return;

    const alertItem = document.createElement("div");
    alertItem.style.cssText = `
        display:flex; align-items:center; justify-content:space-between;
        padding:0.35rem 0.75rem; border-radius:6px; font-size:0.82rem;
        background:rgba(255,255,255,0.06); border-left:3px solid ${alertData.color};
        color:${alertData.color};
    `;
    alertItem.innerHTML = `
        <span>${alertData.text}</span>
        <button onclick="dismissAlert(this)" aria-label="Dismiss alert"
            style="background:none;border:none;color:${alertData.color};cursor:pointer;
                   font-size:1rem;padding:0 0 0 0.5rem;line-height:1;">✕</button>
    `;

    if (alertData.severity === "critical") {
        alertsList.insertBefore(alertItem, alertsList.firstChild);
    } else {
        alertsList.appendChild(alertItem);
    }

    banner.style.display = "block";
}

/**
 * Dismiss an individual alert item and hide the banner when none remain.
 *
 * @param {HTMLElement} dismissButton - The dismiss button element.
 */
function dismissAlert(dismissButton) {
    const alertItem = dismissButton.parentElement;
    const alertsList = alertItem.parentElement;
    alertItem.remove();
    if (alertsList && alertsList.children.length === 0) {
        document.getElementById("alerts-banner").style.display = "none";
    }
}

// ==========================================================================
// 4. TRANSPORTATION TAB
// ==========================================================================

/**
 * Populate the transportation panel with data for the selected host city.
 *
 * @param {string} cityName - The FIFA 2026 host city name.
 */
function updateTransportPanel(cityName) {
    const cityData = TRANSPORT_DATA[cityName];
    if (!cityData) return;

    const shuttleEl   = document.getElementById("transport-shuttle");
    const parkingEl   = document.getElementById("transport-parking");
    const rideshareEl = document.getElementById("transport-rideshare");
    const accessibleEl = document.getElementById("transport-accessible");

    if (shuttleEl)    shuttleEl.textContent   = cityData.shuttle;
    if (parkingEl)    parkingEl.textContent    = cityData.parking;
    if (rideshareEl)  rideshareEl.textContent  = cityData.rideshare;
    if (accessibleEl) accessibleEl.textContent = cityData.accessible;
}

// ==========================================================================
// 5. PANEL NAVIGATION
// ==========================================================================

/**
 * Switch the visible panel using GSAP fade/slide transitions.
 *
 * @param {string} targetPanelId - The id of the panel element to show.
 * @param {CrowdSimulator} crowdSimulator - The crowd simulator instance.
 */
function switchPanel(targetPanelId, crowdSimulator) {
    if (state.currentPanel === targetPanelId) return;

    const currentPanelEl = document.getElementById(state.currentPanel);
    const targetPanelEl  = document.getElementById(targetPanelId);
    if (!currentPanelEl || !targetPanelEl) return;

    const allTabButtons = document.querySelectorAll(".nav-link, .mobile-nav-link");

    gsap.to(currentPanelEl, {
        opacity: 0, y: -10, duration: 0.15,
        onComplete: () => {
            currentPanelEl.classList.remove("active");
            targetPanelEl.classList.add("active");

            if (targetPanelId === "panel-crowd") {
                crowdSimulator.initCanvasSize();
                crowdSimulator.createCrowdDots();
            }
            if (targetPanelId === "panel-transport") {
                const citySelect = document.getElementById("transport-city-select");
                if (citySelect) updateTransportPanel(citySelect.value);
            }

            gsap.fromTo(targetPanelEl,
                { opacity: 0, y: 10 },
                { opacity: 1, y: 0, duration: 0.25 }
            );
        }
    });

    allTabButtons.forEach(tabButton => {
        const isActiveTab = tabButton.getAttribute("data-target") === targetPanelId;
        tabButton.classList.toggle("active", isActiveTab);
        if (isActiveTab) {
            tabButton.setAttribute("aria-current", "page");
        } else {
            tabButton.removeAttribute("aria-current");
        }
    });

    state.currentPanel = targetPanelId;
}

// ==========================================================================
// 6. CHAT INTERFACE HELPERS
// ==========================================================================

/**
 * Append a message bubble to the chat log.
 *
 * @param {string} senderName - Display name for the message sender.
 * @param {string} messageContent - Text content to display.
 * @param {string} roleClass - CSS role class: "user" or "assistant".
 * @returns {HTMLElement} The created message div element.
 */
function appendMessage(senderName, messageContent, roleClass) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.className = `chat-message ${roleClass}-message`;

    const timeString = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    messageDiv.innerHTML = `
        <div class="message-meta">
            <span class="message-sender">${senderName}</span>
            <span class="message-time">${timeString}</span>
        </div>
        <div class="message-content">${messageContent}</div>
    `;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageDiv;
}

/**
 * Submit a message text to the chat form programmatically.
 *
 * @param {string} queryText - The message text to submit.
 */
function submitQuickAction(queryText) {
    const chatInput = document.getElementById("chat-message-input");
    if (!chatInput) return;
    chatInput.value = queryText;
    document.getElementById("chat-form").dispatchEvent(new Event("submit", { cancelable: true }));
}

// ==========================================================================
// 7. MAIN DOMContentLoaded BOOTSTRAP
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {

    initThreeParticles();
    const crowdSimulator = new CrowdSimulator();
    initAlertsBanner();

    // Populate transport panel with default city on load
    updateTransportPanel("New York/New Jersey");

    // -----------------------------------------------------------------------
    // Panel navigation
    // -----------------------------------------------------------------------
    const allTabButtons = document.querySelectorAll(".nav-link, .mobile-nav-link");
    allTabButtons.forEach(tabButton => {
        tabButton.addEventListener("click", () => {
            const targetId = tabButton.getAttribute("data-target");
            switchPanel(targetId, crowdSimulator);
        });
    });

    // -----------------------------------------------------------------------
    // Transport city selector
    // -----------------------------------------------------------------------
    const transportCitySelect = document.getElementById("transport-city-select");
    if (transportCitySelect) {
        transportCitySelect.addEventListener("change", (changeEvent) => {
            updateTransportPanel(changeEvent.target.value);
        });
    }

    // -----------------------------------------------------------------------
    // Global city selector (header)
    // -----------------------------------------------------------------------
    const globalCitySelect = document.getElementById("global-city-select");
    if (globalCitySelect) {
        globalCitySelect.addEventListener("change", (changeEvent) => {
            state.selectedCity = changeEvent.target.value;
            if (transportCitySelect && state.selectedCity) {
                transportCitySelect.value = state.selectedCity;
                updateTransportPanel(state.selectedCity);
            }
        });
    }

    // -----------------------------------------------------------------------
    // Nav city selector (navigation panel)
    // -----------------------------------------------------------------------
    const navCitySelect = document.getElementById("nav-city-select");
    const navVenueLabel = document.getElementById("nav-venue-label");
    if (navCitySelect && navVenueLabel) {
        navCitySelect.addEventListener("change", (changeEvent) => {
            navVenueLabel.textContent = changeEvent.target.value;
        });
    }

    // -----------------------------------------------------------------------
    // Persona selector
    // -----------------------------------------------------------------------
    const personaButtons = document.querySelectorAll(".persona-btn");
    const personaIndicator = document.getElementById("chat-persona-indicator");

    const personaThemes = {
        Staff:         { color: "#e74c3c", label: "Staff Mode — Operational Intelligence" },
        Volunteer:     { color: "#3498db", label: "Volunteer Mode — Shift Coordination" },
        Accessibility: { color: "#2ecc71", label: "Accessibility Mode — ADA Assistance" },
        Fan:           { color: "#c9a84c", label: "Fan Mode — Spectator Guide" }
    };

    personaButtons.forEach(personaButton => {
        personaButton.addEventListener("click", () => {
            personaButtons.forEach(otherButton => {
                otherButton.classList.remove("active");
                otherButton.setAttribute("aria-checked", "false");
            });
            personaButton.classList.add("active");
            personaButton.setAttribute("aria-checked", "true");

            const selectedPersona = personaButton.getAttribute("data-persona");
            state.persona = selectedPersona;

            const theme = personaThemes[selectedPersona] || personaThemes.Fan;
            document.documentElement.style.setProperty("--color-gold", theme.color);

            const phaseBadge = document.getElementById("chat-phase-badge");
            const phaseText = phaseBadge ? ` • ${phaseBadge.textContent}` : "";
            if (personaIndicator) {
                personaIndicator.innerHTML = `Currently guiding you in ${theme.label}${phaseText}`;
            }

            gsap.fromTo(personaIndicator,
                { scale: 0.95, opacity: 0 },
                { scale: 1, opacity: 1, duration: 0.3 }
            );
        });
    });

    // -----------------------------------------------------------------------
    // Language selector
    // -----------------------------------------------------------------------
    const languageSelect = document.getElementById("lang-select");
    if (languageSelect) {
        languageSelect.addEventListener("change", (changeEvent) => {
            state.language = changeEvent.target.value;
        });
    }

    // -----------------------------------------------------------------------
    // Quick action buttons
    // -----------------------------------------------------------------------
    const quickActionButtons = document.querySelectorAll(".quick-action-btn");
    quickActionButtons.forEach(quickButton => {
        quickButton.addEventListener("click", () => {
            const queryText = quickButton.getAttribute("data-query");
            if (queryText) submitQuickAction(queryText);
        });
        quickButton.addEventListener("keydown", (keyEvent) => {
            if (keyEvent.key === "Enter" || keyEvent.key === " ") {
                keyEvent.preventDefault();
                quickButton.click();
            }
        });
    });

    // -----------------------------------------------------------------------
    // Chat form submission
    // -----------------------------------------------------------------------
    const chatForm  = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-message-input");
    const chatBox   = document.getElementById("chat-box");

    chatForm.addEventListener("submit", async (submitEvent) => {
        submitEvent.preventDefault();

        const messageText = chatInput.value.trim();
        if (!messageText) return;

        appendMessage("You", messageText, "user");
        chatInput.value = "";

        const typingIndicator = appendMessage("StadiumIQ", "...", "assistant");

        try {
            const fetchResponse = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: messageText,
                    persona: state.persona,
                    language: state.language,
                    history: state.history
                })
            });

            const responseData = await fetchResponse.json();
            typingIndicator.remove();

            if (fetchResponse.ok) {
                appendMessage("StadiumIQ", responseData.response, "assistant");
                state.history.push({ role: "user",      content: messageText });
                state.history.push({ role: "assistant", content: responseData.response });
                if (state.history.length > MAX_HISTORY_TURNS) {
                    state.history.splice(0, state.history.length - MAX_HISTORY_TURNS);
                }
            } else {
                appendMessage("System Error", responseData.error || "Failed to contact Groq API.", "assistant");
            }
        } catch (networkError) {
            typingIndicator.remove();
            appendMessage("System Error", "Failed to contact server backend. Check connection.", "assistant");
        }
    });

    // -----------------------------------------------------------------------
    // Clear chat button
    // -----------------------------------------------------------------------
    const clearChatButton = document.getElementById("clear-chat-btn");
    if (clearChatButton) {
        clearChatButton.addEventListener("click", () => {
            chatBox.innerHTML = `
                <div class="chat-message assistant-message">
                    <div class="message-meta">
                        <span class="message-sender"><i class="fa-solid fa-robot" aria-hidden="true"></i> StadiumIQ</span>
                        <span class="message-time">Just Now</span>
                    </div>
                    <div class="message-content">Conversation history cleared. How can I help you?</div>
                </div>`;
            state.history = [];
            gsap.from(chatBox.firstElementChild, { opacity: 0, scale: 0.95, duration: 0.3 });
        });
    }

    // -----------------------------------------------------------------------
    // Stadium zone click handler (Navigation panel)
    // -----------------------------------------------------------------------
    const mapZones   = document.querySelectorAll(".map-zone");
    const zoneTitle  = document.getElementById("zone-display-title");
    const zoneContent = document.getElementById("zone-display-content");

    mapZones.forEach(zone => {
        zone.addEventListener("click", () => {
            mapZones.forEach(otherZone => otherZone.classList.remove("active"));
            zone.classList.add("active");

            const zoneDetails = state.zoneDetails[zone.getAttribute("id")];
            if (!zoneDetails) return;

            zoneTitle.textContent = zoneDetails.title;

            const featureListHtml = `<ul style="list-style:none; padding:0;">${
                zoneDetails.features.map(feature =>
                    `<li class="zone-feature-item"><i class="fa-solid fa-circle-info" aria-hidden="true"></i><span>${feature}</span></li>`
                ).join("")
            }</ul>`;
            zoneContent.innerHTML = featureListHtml;

            gsap.fromTo(zoneTitle,    { x: -10, opacity: 0 }, { x: 0, opacity: 1, duration: 0.2 });
            gsap.fromTo(zoneContent.querySelectorAll("li"),
                { x: -10, opacity: 0 }, { x: 0, opacity: 1, duration: 0.2, stagger: 0.05 }
            );
        });

        zone.addEventListener("keydown", (keyEvent) => {
            if (keyEvent.key === "Enter" || keyEvent.key === " ") {
                keyEvent.preventDefault();
                zone.click();
            }
        });
    });

    // -----------------------------------------------------------------------
    // Match schedule details button handler
    // -----------------------------------------------------------------------
    const detailsButtons = document.querySelectorAll(".info-details-btn");
    detailsButtons.forEach(detailsButton => {
        detailsButton.addEventListener("click", () => {
            const cityName = detailsButton.getAttribute("data-city");
            const venueInfo = state.citiesData[cityName];
            if (!venueInfo) return;

            const detailsHtml = `
                <strong>${venueInfo.stadium} (${cityName})</strong><br>
                <strong>Capacity:</strong> ${venueInfo.capacity} seats<br><br>
                <strong><i class="fa-solid fa-leaf" aria-hidden="true"></i> Sustainability:</strong><br>${venueInfo.sustainability}<br><br>
                <strong><i class="fa-solid fa-wheelchair" aria-hidden="true"></i> Accessibility:</strong><br>${venueInfo.accessibility}
            `;
            appendMessage(`Stadium Guide: ${cityName}`, detailsHtml, "assistant");
            switchPanel("panel-chat", crowdSimulator);
        });
    });

    // -----------------------------------------------------------------------
    // Crowd simulation recalculate button
    // -----------------------------------------------------------------------
    const simulateDensityButton = document.getElementById("simulate-density-btn");
    if (simulateDensityButton) {
        simulateDensityButton.addEventListener("click", () => {
            gsap.fromTo(simulateDensityButton, { scale: 0.95 }, { scale: 1, duration: 0.1 });
            crowdSimulator.recalculate();
        });
    }
});

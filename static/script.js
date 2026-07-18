/**
 * StadiumIQ Frontend JavaScript Core.
 *
 * Implements persona/language selectors, navigation zone interactions,
 * real-time crowd visualizer using HTML5 Canvas, GSAP animations,
 * Three.js particle background, and AI assistant chat interface.
 */

// Global Application State
const state = {
    persona: "Fan",
    language: "English",
    history: [], // Stores message objects: {role: "user" | "assistant", content: string}
    currentPanel: "panel-chat",
    crowdDensity: 0.54, // Moderate
    simulatingCrowd: true,
    citiesData: {
        "Mexico City": {
            stadium: "Estadio Azteca",
            capacity: "87,523 seats",
            sustainability: "Rainwater harvesting system, upgraded LED lighting, integrated public transport hub.",
            accessibility: "Ramp access, tactile paving guides, and dedicated volunteer assistance teams on matches."
        },
        "Toronto": {
            stadium: "BMO Field",
            capacity: "30,000 seats",
            sustainability: "Hybrid grass system, zero waste sorting stations, streetcar and light-rail transit lines.",
            accessibility: "Elevators to all seating levels, accessible seating boxes, audio-described commentary services."
        },
        "Los Angeles": {
            stadium: "SoFi Stadium",
            capacity: "70,240 seats",
            sustainability: "Recycled water irrigation, energy-efficient LED panels, solar energy generation system.",
            accessibility: "Open captioning screens, assistive listening devices, ADA transport shuttles."
        },
        "Dallas": {
            stadium: "AT&T Stadium",
            capacity: "80,000 seats",
            sustainability: "Retrofitted smart HVAC cooling system, food waste composting, eco-friendly transit loops.",
            accessibility: "Dedicated elevators, accessible ticketing, tactile pathways for vision-impaired fans."
        },
        "Miami": {
            stadium: "Hard Rock Stadium",
            capacity: "64,767 seats",
            sustainability: "Eliminated 99.4% of single-use plastics, massive solar canopy, local eco-shuttles.",
            accessibility: "Sensory-inclusive certification, wheelchair companion seating, ADA loops."
        },
        "New York/New Jersey": {
            stadium: "MetLife Stadium",
            capacity: "82,500 seats",
            sustainability: "100% wind-powered, zero waste initiatives, train/rail access connections.",
            accessibility: "Sensory rooms, fully wheelchair-accessible seating, designated access gates."
        }
    },
    zoneDetails: {
        "zone-north": {
            title: "North Stand - Sector A",
            features: [
                "Main Gate Entrance: Gate A (General Access)",
                "Closest Parking: North Lot (Electric Vehicle charging available)",
                "Amenities: Food court (Vegan alternatives), merchandising shop",
                "Accessibility: Standard wheelchair ramp to low levels",
                "Emergency Route: Direct exits out toward the North Parking Area"
            ]
        },
        "zone-east": {
            title: "East Stand - Family Zone",
            features: [
                "Main Gate Entrance: Gate B (Family & Groups)",
                "Closest Parking: East Park & Ride Lot",
                "Amenities: Kids zone, baby care rooms, recycling hub",
                "Accessibility: Tactile path guidance for vision support",
                "Emergency Route: Exit tunnels leading directly to East Concourse Plaza"
            ]
        },
        "zone-south": {
            title: "South Stand - Accessibility Center",
            features: [
                "Main Gate Entrance: Gate C (Special Assistance & Wheelchair Entry)",
                "Closest Parking: ADA Designated Parking Lot (with shuttle service)",
                "Amenities: Medical desk, sensory room, assistive listening devices counter",
                "Accessibility: Low-grade ramps, 4 accessible elevator shafts",
                "Emergency Route: Dedicated fire-safe evacuation elevators and wide ramps"
            ]
        },
        "zone-west": {
            title: "West Stand - VIP & Media Suite",
            features: [
                "Main Gate Entrance: Gate D (VIP, Press, Sponsors)",
                "Closest Parking: VIP West Valet",
                "Amenities: Conference rooms, lounge, media editing rooms",
                "Accessibility: Full elevator connectivity to VIP balconies",
                "Emergency Route: Press elevators and emergency exit stairs"
            ]
        }
    }
};

// ==========================================================================
// 1. THREE.JS PARTICLE BACKGROUND SETUP
// ==========================================================================
function initThreeParticles() {
    const canvas = document.getElementById("bg-canvas");
    if (!canvas) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Particle geometry
    const particlesCount = 250;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particlesCount * 3);
    const colors = new Float32Array(particlesCount * 3);

    // Color choices: Gold, Red, Deep Blue (FIFA themes)
    const colorChoices = [
        new THREE.Color(0xc9a84c), // Gold
        new THREE.Color(0xc0392b), // Red
        new THREE.Color(0x3498db)  // Blue
    ];

    for (let i = 0; i < particlesCount * 3; i += 3) {
        // Spread particles randomly in a sphere-like space
        positions[i] = (Math.random() - 0.5) * 15;
        positions[i + 1] = (Math.random() - 0.5) * 15;
        positions[i + 2] = (Math.random() - 0.5) * 15;

        // Randomly pick a theme color
        const pickedColor = colorChoices[Math.floor(Math.random() * colorChoices.length)];
        colors[i] = pickedColor.r;
        colors[i + 1] = pickedColor.g;
        colors[i + 2] = pickedColor.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Material with round soft particles
    const material = new THREE.PointsMaterial({
        size: 0.08,
        vertexColors: true,
        transparent: true,
        opacity: 0.7,
        blending: THREE.AdditiveBlending
    });

    const particleSystem = new THREE.Points(geometry, material);
    scene.add(particleSystem);

    camera.position.z = 5;

    // Animation Loop
    function animateParticles() {
        requestAnimationFrame(animateParticles);

        particleSystem.rotation.y += 0.001;
        particleSystem.rotation.x += 0.0005;

        renderer.render(scene, camera);
    }

    animateParticles();

    // Window Resize Event
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// ==========================================================================
// 2. CROWD DENSITY SIMULATION (HTML5 CANVAS)
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

    initCanvasSize() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight || 350;
    }

    createCrowdDots() {
        this.dots = [];
        // Scale number of crowd agents by density
        this.maxDots = Math.floor(state.crowdDensity * 220) + 30;

        for (let i = 0; i < this.maxDots; i++) {
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

    getDotColor() {
        // Red, Orange, Green particles depending on state density
        if (state.crowdDensity > 0.75) {
            return "rgba(192, 57, 43, 0.7)"; // Red (High)
        } else if (state.crowdDensity > 0.4) {
            return "rgba(243, 156, 18, 0.7)"; // Orange (Moderate)
        } else {
            return "rgba(46, 204, 113, 0.7)"; // Green (Low)
        }
    }

    animate() {
        if (!state.simulatingCrowd) return;
        requestAnimationFrame(() => this.animate());

        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        ctx.clearRect(0, 0, w, h);

        // Draw simulated stadium lanes/channels
        ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
        ctx.lineWidth = 2;
        // Verticals
        for (let x = 50; x < w; x += 100) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, h);
            ctx.stroke();
        }
        // Horizontals
        for (let y = 50; y < h; y += 100) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(w, y);
            ctx.stroke();
        }

        // Draw exit arrows
        ctx.fillStyle = "rgba(46, 204, 113, 0.25)";
        ctx.font = "bold 14px Plus Jakarta Sans, system-ui, sans-serif";
        ctx.fillText("EXIT C (South)", 20, h - 20);
        ctx.fillText("EXIT A (North)", 20, 40);

        // Update & Render each dot
        this.dots.forEach(dot => {
            dot.x += dot.vx;
            dot.y += dot.vy;

            // Bounce on boundaries
            if (dot.x < 0 || dot.x > w) dot.vx *= -1;
            if (dot.y < 0 || dot.y > h) dot.vy *= -1;

            ctx.beginPath();
            ctx.arc(dot.x, dot.y, dot.radius, 0, Math.PI * 2);
            ctx.fillStyle = dot.color;
            ctx.shadowColor = dot.color;
            ctx.shadowBlur = 4;
            ctx.fill();
            ctx.shadowBlur = 0; // reset
        });
    }

    recalculate() {
        // Randomize density state
        const densities = [0.28, 0.54, 0.86];
        const statusStrings = ["Low (28%)", "Moderate (54%)", "High (86%)"];
        const statusColors = ["#2ecc71", "#f39c12", "#c0392b"];
        const alerts = [
            `
            <div class="alert-item success">
                <i class="fa-solid fa-circle-check" aria-hidden="true"></i>
                <div>
                    <strong>Optimal Crowd Density</strong>
                    <p>Low congestion throughout all concourses. Green transport shuttles departing continuously.</p>
                </div>
            </div>
            `,
            `
            <div class="alert-item warning">
                <i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i>
                <div>
                    <strong>Gate B Congestion</strong>
                    <p>High traffic density detected near east stand. Safe zone alternates: Route via South Gate C.</p>
                </div>
            </div>
            <div class="alert-item success">
                <i class="fa-solid fa-circle-check" aria-hidden="true"></i>
                <div>
                    <strong>Evacuation Routes Clear</strong>
                    <p>Emergency exits and elevator banks fully clear. Accessibility flows optimal.</p>
                </div>
            </div>
            `,
            `
            <div class="alert-item warning" style="background: rgba(192, 57, 43, 0.15); border-color: rgba(192, 57, 43, 0.3); color: #c0392b;">
                <i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i>
                <div>
                    <strong>CONGESTION ALERT: All Exit Zones Heavy</strong>
                    <p>Crowd flow at 86% capacity. Activating real-time decision support algorithms. Divert fans to secondary transit hubs.</p>
                </div>
            </div>
            <div class="alert-item warning">
                <i class="fa-solid fa-triangle-exclamation" aria-hidden="true"></i>
                <div>
                    <strong>Gate A and Gate D Queues (30m+)</strong>
                    <p>Recommend using Gate C South Stand for swift, elevator-accessible exit flow.</p>
                </div>
            </div>
            `
        ];

        const idx = Math.floor(Math.random() * densities.length);
        state.crowdDensity = densities[idx];

        // Update HTML Elements
        document.getElementById("metric-density-val").textContent = statusStrings[idx];
        const bar = document.getElementById("metric-density-bar");
        bar.style.width = `${densities[idx] * 100}%`;
        bar.style.backgroundColor = statusColors[idx];

        document.getElementById("density-alerts-box").innerHTML = alerts[idx];

        // Recreate dots
        this.createCrowdDots();
    }
}

// ==========================================================================
// 3. CORE FRONTEND WORKFLOWS AND EVENT LISTENERS
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
    // A. Start visual backbones
    initThreeParticles();
    const crowdSim = new CrowdSimulator();

    // B. Panel Navigation Router (GSAP Integration)
    const tabButtons = document.querySelectorAll(".nav-link, .mobile-nav-link");
    const panels = document.querySelectorAll(".panel-section");

    function switchPanel(targetId) {
        if (state.currentPanel === targetId) return;

        // Hide current active panel
        const currentPanelEl = document.getElementById(state.currentPanel);
        const targetPanelEl = document.getElementById(targetId);

        if (currentPanelEl && targetPanelEl) {
            // Animate using GSAP
            gsap.to(currentPanelEl, {
                opacity: 0,
                y: -10,
                duration: 0.15,
                onComplete: () => {
                    currentPanelEl.classList.remove("active");
                    
                    targetPanelEl.classList.add("active");
                    if (targetId === "panel-crowd") {
                        crowdSim.initCanvasSize();
                        crowdSim.createCrowdDots();
                    }
                    gsap.fromTo(targetPanelEl, 
                        { opacity: 0, y: 10 },
                        { opacity: 1, y: 0, duration: 0.25 }
                    );
                }
            });

            // Update Nav link classes
            tabButtons.forEach(btn => {
                const isMatch = btn.getAttribute("data-target") === targetId;
                btn.classList.toggle("active", isMatch);
                if (isMatch) {
                    btn.setAttribute("aria-current", "page");
                } else {
                    btn.removeAttribute("aria-current");
                }
            });

            state.currentPanel = targetId;
        }
    }

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.getAttribute("data-target");
            switchPanel(target);

            if (target === "panel-crowd") {
                // Resize and redraw the crowd simulation when the panel becomes visible.
                crowdSim.initCanvasSize();
                crowdSim.createCrowdDots();
            }
        });
    });

    // C. Persona Switcher Controls
    const personaBtns = document.querySelectorAll(".persona-btn");
    const personaTextIndicator = document.getElementById("chat-persona-indicator");

    personaBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            personaBtns.forEach(b => {
                b.classList.remove("active");
                b.setAttribute("aria-checked", "false");
            });

            btn.classList.add("active");
            btn.setAttribute("aria-checked", "true");

            const persona = btn.getAttribute("data-persona");
            state.persona = persona;

            // Highlight theme changes depending on persona
            const root = document.documentElement;
            if (persona === "Staff") {
                root.style.setProperty("--color-gold", "#e74c3c"); // Orange/Red accent for staff
                personaTextIndicator.textContent = "Currently guiding you in Staff Mode (Operational Support)";
            } else if (persona === "Volunteer") {
                root.style.setProperty("--color-gold", "#3498db"); // Blue accent for volunteer
                personaTextIndicator.textContent = "Currently guiding you in Volunteer Mode (Shift Coordination)";
            } else if (persona === "Accessibility") {
                root.style.setProperty("--color-gold", "#2ecc71"); // Green accent for accessibility
                personaTextIndicator.textContent = "Currently guiding you in Accessibility Mode (ADA Assistance)";
            } else {
                root.style.setProperty("--color-gold", "#c9a84c"); // Gold accent for fan
                personaTextIndicator.textContent = "Currently guiding you in Fan Mode (Spectator Guide)";
            }

            // Animate persona switch visually
            gsap.fromTo(personaTextIndicator, { scale: 0.95, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3 });
        });
    });

    // D. Language Selector Change
    const langSelect = document.getElementById("lang-select");
    langSelect.addEventListener("change", (e) => {
        state.language = e.target.value;
    });

    // E. AI Chat Interface Flow
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-message-input");
    const chatBox = document.getElementById("chat-box");
    const clearChatBtn = document.getElementById("clear-chat-btn");

    function appendMessage(sender, content, role) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-message ${role}-message`;

        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        msgDiv.innerHTML = `
            <div class="message-meta">
                <span class="message-sender">${sender}</span>
                <span class="message-time">${timeStr}</span>
            </div>
            <div class="message-content">${content}</div>
        `;
        
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        // Return element for animations
        return msgDiv;
    }

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const messageText = chatInput.value.trim();
        if (!messageText) return;

        // Append User Message
        appendMessage("You", messageText, "user");
        chatInput.value = "";

        // Append temporary typing indicator
        const typingIndicator = appendMessage("StadiumIQ", "...", "assistant");
        
        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: messageText,
                    persona: state.persona,
                    language: state.language,
                    history: state.history
                })
            });

            const data = await response.json();

            // Remove typing indicator
            typingIndicator.remove();

            if (response.ok) {
                // Append Assistant Message
                const cleanContent = data.response;
                appendMessage("StadiumIQ", cleanContent, "assistant");
                
                // Add to history state
                state.history.push({ role: "user", content: messageText });
                state.history.push({ role: "assistant", content: cleanContent });
                
                // Truncate history context to match MAX_HISTORY_LENGTH
                if (state.history.length > 20) {
                    state.history.splice(0, state.history.length - 20);
                }
            } else {
                appendMessage("System Error", data.error || "Failed to contact Groq API.", "assistant");
            }
        } catch (error) {
            typingIndicator.remove();
            appendMessage("System Error", "Failed to contact server backend. Check connection.", "assistant");
        }
    });

    clearChatBtn.addEventListener("click", () => {
        chatBox.innerHTML = `
            <div class="chat-message assistant-message">
                <div class="message-meta">
                    <span class="message-sender"><i class="fa-solid fa-robot" aria-hidden="true"></i> StadiumIQ</span>
                    <span class="message-time">Just Now</span>
                </div>
                <div class="message-content">
                    Conversation history cleared. Let me know what you need assistance with!
                </div>
            </div>
        `;
        state.history = [];
        gsap.from(chatBox.firstElementChild, { opacity: 0, scale: 0.95, duration: 0.3 });
    });

    // F. Interactive Stadium Zones click handler
    const zones = document.querySelectorAll(".map-zone");
    const zoneTitle = document.getElementById("zone-display-title");
    const zoneContent = document.getElementById("zone-display-content");

    zones.forEach(zone => {
        zone.addEventListener("click", () => {
            zones.forEach(z => z.classList.remove("active"));
            zone.classList.add("active");
            
            const zoneId = zone.getAttribute("id");
            const details = state.zoneDetails[zoneId];
            
            if (details) {
                zoneTitle.textContent = details.title;
                
                let htmlList = `<ul style="list-style: none; padding: 0;">`;
                details.features.forEach(feat => {
                    htmlList += `
                        <li class="zone-feature-item">
                            <i class="fa-solid fa-circle-info" aria-hidden="true"></i>
                            <span>${feat}</span>
                        </li>`;
                });
                htmlList += `</ul>`;
                
                zoneContent.innerHTML = htmlList;
                
                // Animate info updates
                gsap.fromTo(zoneTitle, { x: -10, opacity: 0 }, { x: 0, opacity: 1, duration: 0.2 });
                gsap.fromTo(zoneContent.querySelectorAll("li"), 
                    { x: -10, opacity: 0 }, 
                    { x: 0, opacity: 1, duration: 0.2, stagger: 0.05 }
                );
            }
        });

        // Add Enter key support on map zones for accessibility
        zone.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                zone.click();
            }
        });
    });

    // G. Match Info Details click handler
    const detailsBtns = document.querySelectorAll(".info-details-btn");
    detailsBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const city = btn.getAttribute("data-city");
            const venue = state.citiesData[city];
            if (venue) {
                // Format details view or alert (simple custom popup in chat or alert)
                const popupContent = `
                    <strong>${venue.stadium} (${city})</strong><br>
                    <strong>Capacity:</strong> ${venue.capacity}<br><br>
                    <strong><i class="fa-solid fa-leaf text-success" aria-hidden="true"></i> Sustainability:</strong><br>${venue.sustainability}<br><br>
                    <strong><i class="fa-solid fa-wheelchair text-warning" aria-hidden="true"></i> Accessibility:</strong><br>${venue.accessibility}
                `;
                
                // For a premium touch, post this to the chat box!
                appendMessage(`Stadium Guide: ${city}`, popupContent, "assistant");
                
                // Suggest to user to switch view to chat panel
                switchPanel("panel-chat");
            }
        });
    });

    // H. Crowd Management Button trigger
    const simBtn = document.getElementById("simulate-density-btn");
    simBtn.addEventListener("click", () => {
        // Animate button click micro-animation
        gsap.fromTo(simBtn, { scale: 0.95 }, { scale: 1, duration: 0.1 });
        crowdSim.recalculate();
    });
});

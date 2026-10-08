/* =========================================
   AASRA
   Disaster Intelligence Platform
   Main JavaScript
========================================= */


/* =========================================
   1. MOBILE NAVIGATION
========================================= */

const mobileMenuButton = document.getElementById(
    "mobileMenuButton"
);

const navigation = document.querySelector(
    ".navigation"
);

if (mobileMenuButton && navigation) {

    mobileMenuButton.addEventListener(
        "click",
        () => {

            navigation.classList.toggle(
                "active"
            );

        }
    );


    navigation
        .querySelectorAll("a")
        .forEach((link) => {

            link.addEventListener(
                "click",
                () => {

                    navigation.classList.remove(
                        "active"
                    );

                }
            );

        });
}


/* =========================================
   2. CURRENT YEAR
========================================= */

const currentYear =
    document.getElementById("currentYear");

if (currentYear) {

    currentYear.textContent =
        new Date().getFullYear();

}


/* =========================================
   3. INITIAL RISK STATE
=========================================

   IMPORTANT:

   These values are intentionally NOT presented
   as real disaster predictions.

   They are only used to make the frontend
   demonstrate its interface before the real
   backend and ML services are connected.

========================================= */

const demoRiskData = {

    overall: 0,

    flood: 0,

    cyclone: 0,

    earthquake: 0

};


/* =========================================
   4. UPDATE RISK DISPLAY
========================================= */

function updateRiskDisplay(data) {

    const overallValue =
        document.getElementById(
            "overallRiskValue"
        );

    const floodValue =
        document.getElementById(
            "floodRiskValue"
        );

    const cycloneValue =
        document.getElementById(
            "cycloneRiskValue"
        );

    const earthquakeValue =
        document.getElementById(
            "earthquakeRiskValue"
        );


    const floodCard =
        document.getElementById(
            "floodCardRisk"
        );

    const cycloneCard =
        document.getElementById(
            "cycloneCardRisk"
        );

    const earthquakeCard =
        document.getElementById(
            "earthquakeCardRisk"
        );


    if (overallValue) {

        overallValue.textContent =
            data.overall === 0
                ? "--"
                : `${data.overall}%`;

    }


    if (floodValue) {

        floodValue.textContent =
            data.flood === 0
                ? "--"
                : `${data.flood}%`;

    }


    if (cycloneValue) {

        cycloneValue.textContent =
            data.cyclone === 0
                ? "--"
                : `${data.cyclone}%`;

    }


    if (earthquakeValue) {

        earthquakeValue.textContent =
            data.earthquake === 0
                ? "--"
                : `${data.earthquake}%`;

    }


    if (floodCard) {

        floodCard.textContent =
            data.flood === 0
                ? "Awaiting data"
                : `${data.flood}%`;

    }


    if (cycloneCard) {

        cycloneCard.textContent =
            data.cyclone === 0
                ? "Awaiting data"
                : `${data.cyclone}%`;

    }


    if (earthquakeCard) {

        earthquakeCard.textContent =
            data.earthquake === 0
                ? "Awaiting data"
                : `${data.earthquake}%`;

    }


    updateRiskBars(data);

}


/* =========================================
   5. UPDATE RISK BARS
========================================= */

function updateRiskBars(data) {

    const floodBar =
        document.getElementById(
            "floodBar"
        );

    const cycloneBar =
        document.getElementById(
            "cycloneBar"
        );

    const earthquakeBar =
        document.getElementById(
            "earthquakeBar"
        );


    if (floodBar) {

        floodBar.style.width =
            `${data.flood}%`;

    }


    if (cycloneBar) {

        cycloneBar.style.width =
            `${data.cyclone}%`;

    }


    if (earthquakeBar) {

        earthquakeBar.style.width =
            `${data.earthquake}%`;

    }

}


/* =========================================
   6. REGION SELECTOR
========================================= */

const regionSelect =
    document.getElementById(
        "regionSelect"
    );

const assessmentMessage =
    document.getElementById(
        "assessmentMessage"
    );


if (regionSelect && assessmentMessage) {

    regionSelect.addEventListener(
        "change",
        (event) => {

            const selectedRegion =
                event.target.value;


            const regionNames = {

                central:
                    "Central India",

                north:
                    "Northern India",

                east:
                    "Eastern India",

                west:
                    "Western India",

                south:
                    "Southern India"

            };


            const selectedName =
                regionNames[selectedRegion]
                || "Selected region";


            assessmentMessage.innerHTML = `

                <span class="message-icon">
                    i
                </span>

                <p>
                    <strong>
                        ${selectedName}
                    </strong>
                    selected. Live risk assessment
                    will be available after the
                    AASRA backend and ML services
                    are connected.
                </p>

            `;

        }
    );

}


/* =========================================
   7. INITIALIZE MAP
========================================= */

function initializeMap() {

    const mapElement =
        document.getElementById("map");


    if (
        !mapElement ||
        typeof L === "undefined"
    ) {

        return;

    }


    const map =
        L.map(
            mapElement,
            {
                zoomControl: true,
                attributionControl: true
            }
        );


    /*
       India is shown as the initial map area.

       This is only a geographic starting view.
       It is NOT a disaster-risk map.
    */

    map.setView(
        [22.5937, 78.9629],
        5
    );


    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 18,
            attribution:
                '&copy; OpenStreetMap contributors'
        }
    ).addTo(map);


    /*
       Initial marker for the platform.

       This marker is informational only.
       It does not represent a disaster warning.
    */

    const aasraMarker =
        L.marker(
            [22.5937, 78.9629]
        ).addTo(map);


    aasraMarker.bindPopup(
        `
            <strong>AASRA</strong>
            <br>
            Disaster intelligence map
            <br>
            <small>
                Live layers will be connected
                in a later development stage.
            </small>
        `
    );


    /*
       Expose the map for future modules.
    */

    window.aasraMap = map;

}


/* =========================================
   8. SMOOTH INTERNAL LINKS
========================================= */

document
    .querySelectorAll(
        'a[href^="#"]'
    )
    .forEach((link) => {

        link.addEventListener(
            "click",
            (event) => {

                const targetId =
                    link.getAttribute("href");


                if (
                    !targetId ||
                    targetId === "#"
                ) {

                    return;

                }


                const target =
                    document.querySelector(
                        targetId
                    );


                if (!target) {

                    return;

                }


                event.preventDefault();


                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }
        );

    });


/* =========================================
   9. FUTURE BACKEND CONNECTION
=========================================

   The frontend will eventually request
   real information from the FastAPI backend.

   Example future endpoint:

       GET /api/risk

   The actual API call is intentionally
   not enabled yet because the backend has
   not been created.

========================================= */

async function loadLiveRiskData() {

    /*
       Future implementation:

       const response = await fetch(
           "http://localhost:8000/api/risk"
       );

       if (!response.ok) {
           throw new Error(
               "Unable to load risk data."
           );
       }

       const data = await response.json();

       updateRiskDisplay(data);
    */


    /*
       Until the real backend exists,
       keep the dashboard in its honest
       "awaiting data" state.
    */

    updateRiskDisplay(
        demoRiskData
    );

}


/* =========================================
   10. APPLICATION STARTUP
========================================= */

function startAasra() {

    initializeMap();

    loadLiveRiskData();

}


/*
   Start the application after the document
   has loaded.
*/

if (
    document.readyState === "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        startAasra
    );

} else {

    startAasra();

}

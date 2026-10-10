# AASRA 
### Disaster Intelligence & Risk Assessment Platform

AASRA is a project built with the idea of making disaster-related information easier to access and understand. It brings weather data, earthquake information, satellite imagery, and disaster risk assessments together in one place.

The goal is to help people understand changing environmental conditions and improve disaster awareness and preparedness.

## 💡 Why AASRA?

Floods, cyclones, and earthquakes can affect lives and communities with very little time to prepare. Information about these events often comes from different sources, making it difficult to get a quick overview.

AASRA aims to bring useful information into one dashboard so users can explore environmental conditions and understand possible disaster-related risks.

## ✨ What Can AASRA Do?

- 🌧️ **Flood Risk Assessment** — Looks at rainfall, precipitation, humidity, and elevation to calculate a basic flood-risk score.
- 🌪️ **Cyclone Risk Assessment** — Uses wind speed, atmospheric pressure, rainfall, and humidity to assess cyclone-related conditions.
- 🌍 **Earthquake Monitoring** — Retrieves recent earthquake information from the USGS Earthquake API.
- 🌦️ **Live Weather Information** — Fetches current weather data from Open-Meteo.
- 🛰️ **Satellite Imagery** — Provides a NASA GIBS satellite imagery layer for map integration.
- 🗺️ **Interactive Dashboard** — Brings disaster-related information and map features into one web interface.

## 🛠️ Technologies Used

- **HTML, CSS and JavaScript** for the website
- **Python and FastAPI** for the backend
- **Leaflet and OpenStreetMap** for interactive maps
- **Open-Meteo** for weather data
- **USGS Earthquake API** for earthquake observations
- **NASA GIBS** for satellite imagery

## 📁 Project Structure

```text
AASRA/
├── backend/
│   ├── app.py
│   ├── schemas.py
│   ├── requirements.txt
│   ├── risk/
│   └── services/
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── ml/
│   ├── flood/
│   ├── cyclone/
│   └── earthquake/
└── README.md
```

## 🚀 How to Run AASRA

### Step 1: Clone the repository

```bash
git clone https://github.com/saumyadixit3006/AASRA.git
cd AASRA
```

### Step 2: Install the backend requirements

```bash
cd backend
python -m pip install -r requirements.txt
```

### Step 3: Start the backend server

```bash
uvicorn app:app --reload
```

### Step 4: Open the API documentation

Once the server is running, open:

http://127.0.0.1:8000/docs

You can test the available API endpoints directly from this page.

### Step 5: Visit the website

**Live website:** https://saumyadixit3006.github.io/AASRA/

The frontend is hosted on GitHub Pages. Features that need the backend require the API server to be running or deployed separately.

## 🔌 Backend API Endpoints

| Endpoint | Purpose |
|---|---|
| `/health` | Checks whether the backend is running |
| `/api/weather` | Retrieves current weather data |
| `/api/earthquakes` | Retrieves recent earthquake observations |
| `/api/satellite` | Returns satellite-layer configuration |
| `/api/risk/flood` | Calculates a basic flood-risk score |
| `/api/risk/cyclone` | Calculates a basic cyclone-risk score |
| `/api/risk/earthquake` | Assesses potential impact from an earthquake event |

Open `/docs` to see the required parameters for each endpoint.

## 🔍 What Makes This Project Useful?

AASRA brings multiple disaster-related data sources and risk assessment tools into a single platform. Instead of looking at each source separately, users can explore different types of information through one interface.

The project is being developed with the aim of making disaster awareness more accessible and creating a foundation for future data-driven risk assessment.

## 🚧 Current Status

The frontend is available online, and the core backend endpoints have been tested locally. The project is still under development, with further work planned on machine-learning integration, frontend-backend connectivity, and deployment of the backend.

## 🔮 Future Improvements

- Connect live backend data directly to the dashboard.
- Integrate and evaluate machine-learning models for disaster risk assessment.
- Improve map-based risk visualization.
- Expand satellite and environmental data integration.
- Deploy the backend for public access.
- Test and improve the reliability of risk assessments.

## ⚠️ Important Note

The current flood and cyclone risk calculations use rule-based scoring. Earthquake assessment estimates potential impact from an event; it does not predict earthquakes.

AASRA is a project for information, learning, and disaster awareness. Its risk scores are not official warnings and should not replace guidance from emergency services or disaster-management authorities.

## ❤️ Our Vision

We want to explore how technology and accessible

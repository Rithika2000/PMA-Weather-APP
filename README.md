# 🌤️ Weather App — Tech Assessment 1 & 2  

**Developer:** Rithika Gurram  
**Frontend:** Streamlit  
**Backend:** FastAPI  
**Database:** SQLite (via SQLAlchemy ORM)  
**APIs Used:** Open-Meteo, ipapi.co, YouTube Data API, Google Custom Search, Google Maps Embed  
**Weather APP Link: https://nonmanipulative-unerrantly-carla.ngrok-free.dev/


## 🧭 Overview  

This project is an end-to-end **Weather Application** built as part of the **PM Accelerator AI Engineer Technical Assessments 1 & 2**.  
It demonstrates full-stack integration of real-world APIs, data persistence, and modern Python web frameworks — combining **FastAPI** (backend) with **Streamlit** (frontend).


## ⚙️ Features  

### Tech Assessment 1  

- **Flexible location input:** Users can enter a ZIP code, city, landmark, or GPS coordinates.  
- **Live current weather:** Displays real-time temperature, wind speed, and direction.  
- **5-day forecast:** Includes icons and descriptive summaries for each day.  
- **Current location detection:** Fetches weather based on approximate IP location.  
- **Visuals:** Clean layout with emoji-based weather icons for intuitive representation.  


### Tech Assessment 2  

#### 🔹 Persistent Storage (CRUD)

- **Create:** Save location + date range with weather details into the database.  
- **Read:** View all saved entries and their associated data.  
- **Update:** Modify location/date ranges and refresh results.  
- **Delete:** Remove records from the database.  

#### 🔹 Hybrid Date Handling  
- Uses **Open-Meteo Forecast API** for future dates and **Archive API** for past data — merged automatically.  

#### 🔹 API Integrations (Optional Extensions)  
- **YouTube Data API:** Displays travel/weather-related videos for the selected city.  
- **Google Custom Search API:** Shows relevant links or travel info for that location.  
- **Google Maps Embed:** Displays a map centered on the user’s query or coordinates.  

#### 🔹 Data Export (Optional Extensions)  
- Download saved weather data in **JSON**, **CSV**, **Markdown**, **XML**, or **PDF** formats.  


## Architecture  

```bash
[ Streamlit Frontend ]
        │
        ▼
[ FastAPI Backend ]
        │
        ├── Open-Meteo APIs (weather & geocoding)
        ├── YouTube Data API (optional)
        ├── Google Search API (optional)
        ├── Google Maps Embed (optional)
        └── SQLite via SQLAlchemy ORM

```

- The frontend interacts with the backend via REST endpoints.

- The backend handles data validation, API integration, and persistence.

- CORS is enabled for communication between Streamlit (localhost:8501) and FastAPI (localhost:8000).

- SQLite serves as the local database; can be easily switched to PostgreSQL or MySQL for production.

## Folder Structure

```bash
weather-app/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── weather_utils.py
│   │   ├── db.py, models.py, schemas.py, crud.py (Tech 2)
│   │   └── routers/ (weather, records, integrations)
│   ├── alembic/ (migrations)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   └── .streamlit/secrets.toml (optional)
└── README.md

```

## How to Run Locally

**1.Run the Backend (FastAPI)**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       
pip install -r requirements.txt

```

**Set up environment variables:**
Create a .env file inside backend/app/:
```bash
DB_URL=sqlite:///./weather.db
YT_API_KEY=your_youtube_data_api_key
CSE_API_KEY=your_google_custom_search_api_key
CSE_CX=your_search_engine_id

```

**start the backend server::**

```bash
uvicorn app.main:app --reload
```

**2.Run the Frontend (Streamlit)**

```bash
cd ../frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

**Run the Streamlit app:**

```bash
streamlit run app.py
```

App URL: http://localhost:8501

🌍 **APIs Used**

| **API Name**                 | **Purpose**                      | **Auth Required**    | **Base URL**                                     |
| ---------------------------- | -------------------------------- | -------------------- | ------------------------------------------------ |
| **Open-Meteo Forecast API**  | Current & future weather         | ❌ No                 | `https://api.open-meteo.com/v1/forecast`         |
| **Open-Meteo Archive API**   | Past weather data                | ❌ No                 | `https://archive-api.open-meteo.com/v1/archive`  |
| **Open-Meteo Geocoding API** | Convert city → coordinates       | ❌ No                 | `https://geocoding-api.open-meteo.com/v1/search` |
| **ipapi.co**                 | Detect approximate user location | ❌ No                 | `https://ipapi.co/json/`                         |
| **YouTube Data API**         | Show related videos              | ✅ Yes (API key)      | `https://www.googleapis.com/youtube/v3/search`   |
| **Google Custom Search API** | Search related articles          | ✅ Yes (API key + CX) | `https://www.googleapis.com/customsearch/v1`     |
| **Google Maps Embed**        | Show map location                | ❌ No                 | `https://www.google.com/maps/embed/v1/place`     |

**What I Did**

1. Designed FastAPI backend for modular scalability (routers for weather, CRUD, integrations).

2. Used Streamlit for an interactive and minimalistic frontend.

3. Implemented data persistence using SQLite with SQLAlchemy ORM.

4. Added input validation for date range, geocoding, and empty fields.

5. Implemented hybrid date handling (past → archive, future → forecast).

6. Added integrations for YouTube, Google Search, and Google Maps to enhance user experience.

7. Provided data export functionality across multiple formats (JSON, CSV, Markdown, XML, PDF).

8. Integrated CORS middleware for secure backend–frontend communication.

9. Added error handling and user-friendly messages for all edge cases.

10. Followed clean project structure with clear separation between frontend, backend, and database logic.


🎬**Watch Demo Video**

- Shows all major features from Tech Assessment 1 & 2, including weather display, CRUD operations, API integrations, and exports.

- https://www.youtube.com/watch?v=I1qQPoRf7i4&feature=youtu.be


Built with ❤️ by Rithika Gurram as part of PM Accelerator AI Engineer Bootcamp

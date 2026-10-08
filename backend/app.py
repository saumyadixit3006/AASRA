from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AASRA API",
    description="AI-powered multi-disaster risk assessment system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    return {
        "message": "AASRA backend is running",
        "status": "online"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

from fastapi import FastAPI
from app.routes import meteo,analyse,series  # ← ajouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os



# Chargement des variables d'environnement
load_dotenv()




# Création de l'application FastAPI
app = FastAPI(
    title=os.getenv("APP_NAME", "Météo App"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="API de prévision météorologique — Application des Mathématiques",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS — autorise le frontend Vue.js à communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vue.js (Vite)
        "http://localhost:3000",   # alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
# Routes de base
# ─────────────────────────────────────────

# Inclusion des routers
app.include_router(meteo.router)
app.include_router(analyse.router)
app.include_router(series.router)

@app.get("/", tags=["Accueil"])
def accueil():
    """Route racine — vérifie que l'API fonctionne."""
    return {
        "message": "Bienvenue sur l'API Météo Ouagadougou 🌤️",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "ok",
        "documentation": "/docs"
    }


@app.get("/health", tags=["Accueil"])
def health_check():
    """Vérifie l'état du serveur."""
    return {
        "status": "healthy",
        "app": os.getenv("APP_NAME", "Météo App")
    }
    

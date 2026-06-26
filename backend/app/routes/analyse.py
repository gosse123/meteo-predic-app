from fastapi import APIRouter, HTTPException
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os 

router = APIRouter(prefix="/analyse", tags=["Analyse mathématique"])

# Chemin vers le dataset
DATA_PATH = Path(__file__).resolve().parents[3] / "dataset" / "meteo_ouaga.csv"
def charger_donnees():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    full_path = os.path.join(base_dir, "dataset", "meteo_ouaga.csv")
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"Dataset introuvable : {full_path}")
    
    df = pd.read_csv(full_path, parse_dates=["date"])
    return df


# ─────────────────────────────────────────────
# ROUTE 1 : Matrice de corrélation complète
# ─────────────────────────────────────────────
@router.get("/correlation")
def get_correlation():
    """
    Retourne la matrice de corrélation entre toutes les variables numériques.
    Le coefficient de Pearson mesure la relation linéaire entre chaque paire.
    """
    df = charger_donnees()

    variables = ["temperature", "humidite", "pression", "vent", "precipitations"]
    df_num = df[variables].dropna()

    # np.corrcoef retourne une matrice NxN
    matrice = np.corrcoef(df_num.T)

    # Construire un dictionnaire lisible
    resultat = {}
    for i, var_i in enumerate(variables):
        resultat[var_i] = {}
        for j, var_j in enumerate(variables):
            resultat[var_i][var_j] = round(float(matrice[i][j]), 4)

    return {
        "variables": variables,
        "matrice": resultat,
        "interpretation": {
            "humidite_precipitations": {
                "coefficient": resultat["humidite"]["precipitations"],
                "sens": interpreter_correlation(resultat["humidite"]["precipitations"])
            },
            "pression_temperature": {
                "coefficient": resultat["pression"]["temperature"],
                "sens": interpreter_correlation(resultat["pression"]["temperature"])
            }
        }
    }


def interpreter_correlation(r: float) -> str:
    abs_r = abs(r)
    direction = "positive" if r > 0 else "négative"
    if abs_r >= 0.8:
        force = "très forte"
    elif abs_r >= 0.6:
        force = "forte"
    elif abs_r >= 0.4:
        force = "modérée"
    elif abs_r >= 0.2:
        force = "faible"
    else:
        force = "très faible ou nulle"
    return f"Corrélation {direction} {force} (r = {round(r, 4)})"


# ─────────────────────────────────────────────
# ROUTE 2 : Corrélation entre deux variables
# ─────────────────────────────────────────────
@router.get("/correlation/{var1}/{var2}")
def get_correlation_deux_variables(var1: str, var2: str):
    """
    Retourne le coefficient de corrélation entre deux variables spécifiques,
    avec les données brutes pour tracer un nuage de points côté frontend.
    """
    variables_autorisees = ["temperature", "humidite", "pression", "vent", "precipitations"]

    if var1 not in variables_autorisees or var2 not in variables_autorisees:
        raise HTTPException(
            status_code=400,
            detail=f"Variables autorisées : {variables_autorisees}"
        )

    df = charger_donnees()
    df_clean = df[[var1, var2]].dropna()

    x = df_clean[var1].values
    y = df_clean[var2].values

    r = float(np.corrcoef(x, y)[0][1])

    # Retourner un échantillon pour le nuage de points (max 200 points)
    echantillon = df_clean.sample(n=min(200, len(df_clean)), random_state=42)

    return {
        "variable_x": var1,
        "variable_y": var2,
        "coefficient_pearson": round(r, 4),
        "interpretation": interpreter_correlation(r),
        "n_observations": len(df_clean),
        "donnees_nuage": {
            "x": echantillon[var1].tolist(),
            "y": echantillon[var2].tolist()
        }
    }


# ─────────────────────────────────────────────
# ROUTE 3 : Régression linéaire simple
# ─────────────────────────────────────────────
@router.get("/regression/simple")
def get_regression_simple(variable_x: str = "humidite"):
    """
    Régression linéaire simple : prédit la température à partir d'une variable.
    Modèle : température = a * variable_x + b
    """
    variables_autorisees = ["humidite", "pression", "vent", "precipitations"]

    if variable_x not in variables_autorisees:
        raise HTTPException(
            status_code=400,
            detail=f"Variables autorisées comme prédicteur : {variables_autorisees}"
        )

    df = charger_donnees()
    df_clean = df[["temperature", variable_x]].dropna()

    X = df_clean[[variable_x]].values  # shape (n, 1)
    y = df_clean["temperature"].values  # shape (n,)

    # Découpage train/test : 80% entraînement, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    
    modele = LinearRegression()  # sa c'est le choix du model 
    modele.fit(X_train, y_train) # Entraînement du modèle
    # Prédictions sur les données de test
    y_pred = modele.predict(X_test)

    # Métriques d'évaluation
    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))

    # Données pour tracer la droite de régression
    x_range = np.linspace(X.min(), X.max(), 100)
    y_range = modele.predict(x_range.reshape(-1, 1))

    return {
        "modele": "Régression Linéaire Simple",
        "variable_predicteur": variable_x,
        "variable_cible": "temperature",
        "equation": {
            "formule": f"température = {round(float(modele.coef_[0]), 4)} × {variable_x} + {round(float(modele.intercept_), 4)}",
            "coefficient_a": round(float(modele.coef_[0]), 4),
            "ordonnee_b": round(float(modele.intercept_), 4)
        },
        "metriques": {
            "MAE": round(mae, 4),
            "MSE": round(mse, 4),
            "R2": round(r2, 4),
            "interpretation_R2": f"Le modèle explique {round(r2 * 100, 1)}% de la variance de la température"
        },
        "tailles": {
            "train": len(X_train),
            "test": len(X_test)
        },
        "droite_regression": {
            "x": x_range.tolist(),
            "y": y_range.tolist()
        },
        "nuage_test": {
            "x": X_test.flatten().tolist(),
            "y_reel": y_test.tolist(),
            "y_predit": y_pred.tolist()
        }
    }


# ─────────────────────────────────────────────
# ROUTE 4 : Régression linéaire multiple
# ─────────────────────────────────────────────
@router.get("/regression/multiple")
def get_regression_multiple():
    """
    Régression linéaire multiple : prédit la température à partir de
    plusieurs variables simultanément.
    Modèle : température = a1*humidite + a2*pression + a3*vent + b
    """
    df = charger_donnees()

    predicteurs = ["humidite", "pression", "vent"]
    df_clean = df[["temperature"] + predicteurs].dropna()

    X = df_clean[predicteurs].values
    y = df_clean["temperature"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    modele = LinearRegression()
    modele.fit(X_train, y_train)

    y_pred = modele.predict(X_test)

    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))

    # Coefficients par variable
    coefficients = {
        predicteurs[i]: round(float(modele.coef_[i]), 4)
        for i in range(len(predicteurs))
    }

    return {
        "modele": "Régression Linéaire Multiple",
        "variables_predicteurs": predicteurs,
        "variable_cible": "temperature",
        "equation": {
            "coefficients": coefficients,
            "ordonnee_b": round(float(modele.intercept_), 4)
        },
        "metriques": {
            "MAE": round(mae, 4),
            "MSE": round(mse, 4),
            "R2": round(r2, 4),
            "interpretation_R2": f"Le modèle explique {round(r2 * 100, 1)}% de la variance de la température"
        },
        "tailles": {
            "train": len(X_train),
            "test": len(X_test)
        },
        "comparaison_test": {
            "y_reel": y_test[:20].tolist(),
            "y_predit": [round(v, 2) for v in y_pred[:20].tolist()]
        }
    }
    
    
from pydantic import BaseModel, Field

# 1. Définir la structure des données reçues du formulaire Vue.js
class PredictionInput(BaseModel):
    humidite: float = Field(..., ge=0, le=100, description="Humidité en %")
    pression: float = Field(..., ge=900, le=1100, description="Pression en hPa")
    vent: float = Field(..., ge=0, le=150, description="Vitesse du vent en km/h")

# 2. Créer la route POST pour la prédiction
@router.post("/predire-temperature")
def predire_temperature(payload: PredictionInput):
    """
    Prend les variables climatiques en entrée, entraîne la régression multiple,
    et retourne la température prédite ainsi que l'équation pour le bouton explication.
    """
    df = charger_donnees()
    predicteurs = ["humidite", "pression", "vent"]
    df_clean = df[["temperature"] + predicteurs].dropna()

    X = df_clean[predicteurs].values
    y = df_clean["temperature"].values

    # Entraînement du modèle de régression multiple
    modele = LinearRegression()
    modele.fit(X, y)

    # Extraction des coefficients calculés par l'algorithme
    coef_h = float(modele.coef_[0])
    coef_p = float(modele.coef_[1])
    coef_v = float(modele.coef_[2])
    intercept_b = float(modele.intercept_)

    # Calcul de la prédiction avec les données de l'utilisateur
    temperature_predite = (coef_h * payload.humidite) + (coef_p * payload.pression) + (coef_v * payload.vent) + intercept_b

    return {
        "temperature_predite": round(temperature_predite, 2),
        "valeurs_saisies": {
            "humidite": payload.humidite,
            "pression": payload.pression,
            "vent": payload.vent
        },
        "details_modele": {
            "coef_humidite": round(coef_h, 4),
            "coef_pression": round(coef_p, 4),
            "coef_vent": round(coef_v, 4),
            "ordonnee_b": round(intercept_b, 4),
            "formule_complete": f"Température = ({round(coef_h, 4)} × Humidité) + ({round(coef_p, 4)} × Pression) + ({round(coef_v, 4)} × Vent) + {round(intercept_b, 4)}"
        }
    }

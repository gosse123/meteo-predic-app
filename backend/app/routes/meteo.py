from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
import numpy as np
import os

router = APIRouter(
    prefix="/meteo",
    tags=["Données Météo"]
)

# ─────────────────────────────────────────
# Chargement du dataset
# ─────────────────────────────────────────

def get_dataset() -> pd.DataFrame:
    """Charge le dataset CSV depuis le chemin défini."""
    dataset_path = os.getenv("DATASET_PATH", "../dataset/meteo_ouaga.csv")
    
    # Résolution du chemin relatif par rapport à ce fichier
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    full_path = os.path.join(base_dir, "dataset", "meteo_ouaga.csv")
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=404,
            detail=f"Dataset introuvable : {full_path}"
        )
    
    df = pd.read_csv(full_path, parse_dates=["date"])
    return df


# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────

@router.get("/", summary="Liste des données météo")
def get_meteo(
    limit: int = Query(default=30, ge=1, le=1460, description="Nombre de lignes"),
    annee: Optional[int] = Query(default=None, description="Filtrer par année"),
    mois: Optional[int] = Query(default=None, ge=1, le=12, description="Filtrer par mois"),
    saison: Optional[str] = Query(default=None, description="Saison sèche ou humide")
):
    """Retourne les données météo avec filtres optionnels."""
    df = get_dataset()

    # Filtres
    if annee:
        df = df[df["annee"] == annee]
    if mois:
        df = df[df["mois"] == mois]
    if saison:
        df = df[df["saison"].str.lower() == saison.lower()]

    df = df.head(limit)

    # Conversion en liste de dictionnaires
    records = df.copy()
    records["date"] = records["date"].dt.strftime("%Y-%m-%d")
    
    return {
        "total": len(records),
        "donnees": records.to_dict(orient="records")
    }


@router.get("/resume", summary="Résumé statistique du dataset")
def get_resume():
    """Retourne les statistiques générales du dataset."""
    df = get_dataset()

    return {
        "total_jours": len(df),
        "periode": {
            "debut": df["date"].min().strftime("%Y-%m-%d"),
            "fin": df["date"].max().strftime("%Y-%m-%d")
        },
        "annees_disponibles": sorted(df["annee"].unique().tolist()),
        "colonnes": list(df.columns)
    }


@router.get("/statistiques", summary="Statistiques descriptives")
def get_statistiques(
    annee: Optional[int] = Query(default=None, description="Filtrer par année")
):
    """
    Retourne les statistiques descriptives mathématiques :
    moyenne, médiane, variance, écart-type, min, max.
    """
    df = get_dataset()

    if annee:
        df = df[df["annee"] == annee]
        if df.empty:
            raise HTTPException(status_code=404, detail="Aucune donnée pour cette année")

    variables = ["temperature", "humidite", "pression", "vent", "precipitations"]
    stats = {}

    for var in variables:
        serie = df[var].dropna()
        stats[var] = {
            "moyenne":    round(float(serie.mean()), 2),
            "mediane":    round(float(serie.median()), 2),
            "variance":   round(float(serie.var()), 2),
            "ecart_type": round(float(serie.std()), 2),
            "minimum":    round(float(serie.min()), 2),
            "maximum":    round(float(serie.max()), 2),
            "count":      int(serie.count())
        }

    return {
        "annee": annee or "toutes",
        "statistiques": stats
    }


@router.get("/par-mois", summary="Moyennes mensuelles")
def get_par_mois(annee: Optional[int] = Query(default=None)):
    """Retourne les moyennes de chaque variable groupées par mois."""
    df = get_dataset()

    if annee:
        df = df[df["annee"] == annee]

    noms_mois = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
        5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
        9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }

    grouped = df.groupby("mois").agg(
        temperature=("temperature", "mean"),
        humidite=("humidite", "mean"),
        pression=("pression", "mean"),
        vent=("vent", "mean"),
        precipitations=("precipitations", "sum")
    ).round(2).reset_index()

    result = []
    for _, row in grouped.iterrows():
        result.append({
            "mois": int(row["mois"]),
            "nom_mois": noms_mois[int(row["mois"])],
            "temperature": row["temperature"],
            "humidite": row["humidite"],
            "pression": row["pression"],
            "vent": row["vent"],
            "precipitations_total": row["precipitations"]
        })

    return {"annee": annee or "toutes", "donnees": result}
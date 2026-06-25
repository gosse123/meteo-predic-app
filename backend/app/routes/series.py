from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression

router = APIRouter(prefix="/series", tags=["Séries temporelles"])


def charger_donnees():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    full_path = os.path.join(base_dir, "dataset", "meteo_ouaga.csv")

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"Dataset introuvable : {full_path}")

    df = pd.read_csv(full_path, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ─────────────────────────────────────────────
# ROUTE 1 : Évolution temporelle d'une variable
# ─────────────────────────────────────────────
@router.get("/evolution")
@router.get("/evolution")
def get_evolution(
    variable: str = Query(default="temperature", description="Variable à analyser"),
    annee: Optional[int] = Query(default=None, description="Filtrer par année"),
    fenetre_mobile: int = Query(default=7, ge=2, le=30, description="Fenêtre moyenne mobile en jours")
):
    variables_autorisees = ["temperature", "humidite", "pression", "vent", "precipitations"]

    if variable not in variables_autorisees:
        raise HTTPException(
            status_code=400,
            detail=f"Variables autorisées : {variables_autorisees}"
        )

    df = charger_donnees()

    if annee:
        df = df[df["annee"] == annee]
        if df.empty:
            raise HTTPException(status_code=404, detail="Aucune donnée pour cette année")

    df_clean = df[["date", variable]].dropna().copy()

    # Calculer la moyenne mobile sur la copie
    df_clean["moyenne_mobile"] = df_clean[variable].rolling(window=fenetre_mobile).mean()

    # Extraire les listes
    dates = df_clean["date"].dt.strftime("%Y-%m-%d").tolist()
    valeurs_brutes = df_clean[variable].round(2).tolist()
    valeurs_mobile = df_clean["moyenne_mobile"].round(2).tolist()

    # Remplacer NaN par None
    valeurs_brutes = [None if (isinstance(v, float) and np.isnan(v)) else v for v in valeurs_brutes]
    valeurs_mobile = [None if (isinstance(v, float) and np.isnan(v)) else v for v in valeurs_mobile]

    return {
        "variable": variable,
        "annee": annee or "toutes",
        "fenetre_mobile": fenetre_mobile,
        "n_observations": len(df_clean),
        "donnees": {
            "dates": dates,
            "valeurs": valeurs_brutes,
            "moyenne_mobile": valeurs_mobile
        }
    }

# ─────────────────────────────────────────────
# ROUTE 2 : Tendance générale sur toute la période
# ─────────────────────────────────────────────
@router.get("/tendance")
def get_tendance(
    variable: str = Query(default="temperature", description="Variable à analyser")
):
    """
    Calcule la tendance linéaire d'une variable sur toute la période.
    Un coefficient positif signifie que la variable augmente avec le temps.
    """
    variables_autorisees = ["temperature", "humidite", "pression", "vent", "precipitations"]

    if variable not in variables_autorisees:
        raise HTTPException(
            status_code=400,
            detail=f"Variables autorisées : {variables_autorisees}"
        )

    df = charger_donnees()
    df_clean = df[["date", variable]].dropna().copy()

    # Convertir la date en numéro de jour (entier)
    df_clean["jour_numero"] = (df_clean["date"] - df_clean["date"].min()).dt.days

    X = df_clean[["jour_numero"]].values
    y = df_clean[variable].values

    modele = LinearRegression()
    modele.fit(X, y)

    coefficient = float(modele.coef_[0])
    # Variation totale sur toute la période
    nb_jours = int(df_clean["jour_numero"].max())
    variation_totale = round(coefficient * nb_jours, 4)

    # Tendance par année
    variation_annuelle = round(coefficient * 365, 4)

    if abs(coefficient) < 0.0001:
        sens = "stable"
    elif coefficient > 0:
        sens = "hausse"
    else:
        sens = "baisse"

    # Droite de tendance pour le graphique
    x_range = np.array([0, nb_jours])
    y_range = modele.predict(x_range.reshape(-1, 1))

    dates_extremes = [
        df_clean["date"].min().strftime("%Y-%m-%d"),
        df_clean["date"].max().strftime("%Y-%m-%d")
    ]

    return {
        "variable": variable,
        "periode": {
            "debut": dates_extremes[0],
            "fin": dates_extremes[1],
            "nb_jours": nb_jours
        },
        "tendance": {
            "sens": sens,
            "coefficient_journalier": round(coefficient, 6),
            "variation_annuelle": variation_annuelle,
            "variation_totale_periode": variation_totale,
            "interpretation": f"La {variable} {'augmente' if sens == 'hausse' else 'diminue' if sens == 'baisse' else "reste stable"} d'environ {abs(variation_annuelle)} unités par an"
        },
        "droite_tendance": {
            "dates": dates_extremes,
            "valeurs": [round(float(v), 4) for v in y_range]
        }
    }


# ─────────────────────────────────────────────
# ROUTE 3 : Saisonnalité — pattern mensuel
# ─────────────────────────────────────────────
@router.get("/saisonnalite")
def get_saisonnalite(
    variable: str = Query(default="temperature", description="Variable à analyser")
):
    """
    Analyse le pattern saisonnier en calculant la moyenne de chaque mois
    sur toutes les années disponibles.
    """
    variables_autorisees = ["temperature", "humidite", "pression", "vent", "precipitations"]

    if variable not in variables_autorisees:
        raise HTTPException(
            status_code=400,
            detail=f"Variables autorisées : {variables_autorisees}"
        )

    df = charger_donnees()

    noms_mois = {
        1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr",
        5: "Mai", 6: "Juin", 7: "Juil", 8: "Août",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc"
    }

    groupé = df.groupby("mois")[variable].agg(["mean", "std", "min", "max"]).round(2)

    mois_list = []
    for mois_num, row in groupé.iterrows():
        mois_list.append({
            "mois": int(mois_num),
            "nom": noms_mois[int(mois_num)],
            "moyenne": round(float(row["mean"]), 2),
            "ecart_type": round(float(row["std"]), 2),
            "minimum": round(float(row["min"]), 2),
            "maximum": round(float(row["max"]), 2)
        })

    # Mois avec valeur max et min
    moyennes = [m["moyenne"] for m in mois_list]
    idx_max = int(np.argmax(moyennes))
    idx_min = int(np.argmin(moyennes))

    return {
        "variable": variable,
        "saisonnalite": mois_list,
        "observations": {
            "mois_max": mois_list[idx_max]["nom"],
            "valeur_max": mois_list[idx_max]["moyenne"],
            "mois_min": mois_list[idx_min]["nom"],
            "valeur_min": mois_list[idx_min]["moyenne"],
            "amplitude": round(mois_list[idx_max]["moyenne"] - mois_list[idx_min]["moyenne"], 2)
        }
    }


# ─────────────────────────────────────────────
# ROUTE 4 : Comparaison annuelle
# ─────────────────────────────────────────────
@router.get("/comparaison-annuelle")
def get_comparaison_annuelle(
    variable: str = Query(default="temperature", description="Variable à analyser")
):
    """
    Compare les moyennes annuelles d'une variable pour voir son évolution
    d'une année à l'autre.
    """
    variables_autorisees = ["temperature", "humidite", "pression", "vent", "precipitations"]

    if variable not in variables_autorisees:
        raise HTTPException(
            status_code=400,
            detail=f"Variables autorisées : {variables_autorisees}"
        )

    df = charger_donnees()

    groupé = df.groupby("annee")[variable].agg(["mean", "std", "min", "max"]).round(2)

    annees_list = []
    for annee, row in groupé.iterrows():
        annees_list.append({
            "annee": int(annee),
            "moyenne": round(float(row["mean"]), 2),
            "ecart_type": round(float(row["std"]), 2),
            "minimum": round(float(row["min"]), 2),
            "maximum": round(float(row["max"]), 2)
        })

    return {
        "variable": variable,
        "comparaison": annees_list,
        "annees_disponibles": [a["annee"] for a in annees_list]
    }
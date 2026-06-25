import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Reproductibilité
np.random.seed(42)

# Paramètres
START_DATE = datetime(2020, 1, 1)
N_DAYS = 365 * 7  # 4 ans de données

dates = [START_DATE + timedelta(days=i) for i in range(N_DAYS)]

temperatures = []
humidites = []
pressions = []
vents = []
precipitations = []

for date in dates:
    mois = date.month

    # --- Température (°C) ---
    # Ouaga : chaud toute l'année, pic en mars-avril, plus frais en décembre-janvier
    temp_base = 28 + 6 * np.sin((mois - 4) * np.pi / 6)
    temp = np.random.normal(loc=temp_base, scale=2.5)
    temperatures.append(round(temp, 1))

    # --- Humidité (%) ---
    # Saison sèche (nov-avril) : faible humidité
    # Saison humide (mai-oct)  : forte humidité
    if mois in [11, 12, 1, 2, 3]:
        hum_base = 25
    elif mois in [4, 10]:
        hum_base = 45
    elif mois in [5, 9]:
        hum_base = 60
    else:  # juin, juillet, août
        hum_base = 78
    humidite = np.clip(np.random.normal(loc=hum_base, scale=8), 10, 99)
    humidites.append(round(humidite, 1))

    # --- Pression atmosphérique (hPa) ---
    # Légèrement plus basse en saison chaude/humide
    pression_base = 1010 - 3 * np.sin((mois - 4) * np.pi / 6)
    pression = np.random.normal(loc=pression_base, scale=2)
    pressions.append(round(pression, 1))

    # --- Vitesse du vent (km/h) ---
    # Harmattan (saison sèche) : vent fort du nord-est
    if mois in [11, 12, 1, 2]:
        vent_base = 22
    elif mois in [3, 4]:
        vent_base = 18
    else:
        vent_base = 12
    vent = np.clip(np.random.normal(loc=vent_base, scale=5), 0, 60)
    vents.append(round(vent, 1))

    # --- Précipitations (mm) ---
    # Quasiment nulles en saison sèche, fortes en juillet-août
    if mois in [12, 1, 2, 3]:
        pluie = 0.0
    elif mois in [11, 4]:
        pluie = np.random.choice([0, 0, 0, np.random.uniform(1, 10)],
                                  p=[0.85, 0.05, 0.05, 0.05])
    elif mois in [5, 9, 10]:
        pluie = np.random.choice([0, np.random.uniform(1, 30)],
                                  p=[0.6, 0.4])
    else:  # juin, juillet, août
        pluie = np.random.choice([0, np.random.uniform(5, 60)],
                                  p=[0.35, 0.65])
    if isinstance(pluie, np.ndarray):
        pluie = float(pluie)
    precipitations.append(round(float(pluie), 1))

# Construction du DataFrame
df = pd.DataFrame({
    "date": [d.strftime("%Y-%m-%d") for d in dates],
    "temperature": temperatures,
    "humidite": humidites,
    "pression": pressions,
    "vent": vents,
    "precipitations": precipitations,
    "mois": [d.month for d in dates],
    "annee": [d.year for d in dates],
    "saison": [
        "Saison sèche" if d.month in [11, 12, 1, 2, 3, 4]
        else "Saison humide"
        for d in dates
    ]
})

# Sauvegarde
output_path = "meteo_ouaga.csv"
df.to_csv(output_path, index=False)

print(f"✅ Dataset généré : {output_path}")
print(f"📊 Nombre de lignes : {len(df)}")
print(f"\n--- Aperçu ---")
print(df.head(10).to_string())
print(f"\n--- Statistiques ---")
print(df.describe().round(2).to_string())
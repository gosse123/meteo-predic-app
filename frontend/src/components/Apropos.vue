<script setup>
// Liste contenant uniquement les Noms et Prénoms des auteurs
const auteurs = [
  "FAYCALE TRAORE",
  "NIKIEMA Judith",
  "BAMA Richard John Christian",
  "Tapsoba Abdoul -Faïd",
  "Tapsoba Aboulaye",
  "Ouzaïrou SINARE",
  "BIKIENGA Thimoté",
  "SAMANDOULGOU EUGÈNE CHEICK OUMAR",
  "KIMA Hindatou",
  "NAHOUNOU Gosse Amour Prince"
]
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto space-y-8 bg-gray-50 min-h-screen">
    
    <!-- En-tête -->
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
      <h1 class="text-3xl font-black text-gray-900 tracking-tight flex items-center gap-2">
        <span>ℹ️</span> À propos du Projet
      </h1>
      <p class="text-sm text-gray-500 mt-1">Application des Mathématiques Appliquées au climat de Ouagadougou</p>
    </div>

    <!-- Contenu en grilles -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- COLONNE GAUCHE : CONTEXTE, FONCTIONNEMENT DES ONGLETS & TECHS -->
      <div class="lg:col-span-2 space-y-6">
        
        <!-- 1. CONTEXTE -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 space-y-3">
          <h2 class="text-lg font-bold text-gray-800 flex items-center gap-2 border-b pb-2 border-gray-100">
            <span class="text-blue-500">🌍</span> Contexte du projet
          </h2>
          <p class="text-sm text-gray-600 leading-relaxed">
            Ce projet démontre l'utilisation concrète des <strong>Mathématiques Appliquées</strong> à travers une interface web. En exploitant un historique de données météorologiques de la ville de <strong>Ouagadougou</strong>, l'application utilise des concepts de statistiques et d'apprentissage automatique pour transformer des chiffres bruts en graphiques visuels et en outils de prédiction interactifs.
          </p>
        </div>

        <!-- 2. COMMENT LES MATHS INTERVIENNENT DANS CHAQUE ONGLET -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 space-y-4">
          <h2 class="text-lg font-bold text-gray-800 flex items-center gap-2 border-b pb-2 border-gray-100">
            <span class="text-indigo-500">📐</span> Fonctionnement Mathématique des Onglets
          </h2>
          
          <div class="space-y-4 text-sm text-gray-600">
            
            <!-- Séries Temporelles -->
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <strong class="text-indigo-900 block text-base mb-1">📈 Séries Temporelles (Lissage)</strong>
              <p class="mt-1">
                Le climat change d'un jour à l'autre de façon irrégulière (bruit aléatoire). L'application utilise la méthode de la <strong>Moyenne Mobile</strong>. En ajustant le curseur, l'interface calcule la moyenne des jours précédents pour effacer ces petites variations quotidiennes. Cela permet à l'utilisateur de voir clairement la courbe principale et l'évolution globale de la météo.
              </p>
            </div>

            <!-- Saisonnalité -->
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <strong class="text-indigo-900 block text-base mb-1">📊 Saisonnalité & Tendance</strong>
              <p class="mt-1">
                Cet onglet sépare les données en deux analyses. D'un côté, il calcule une <strong>ligne de tendance</strong> pour savoir si le climat se réchauffe ou se refroidit sur plusieurs années. De l'autre côté, il regroupe les données par mois pour calculer des <strong>moyennes mensuelles</strong>. C'est ce qui permet d'identifier visuellement le mois le plus chaud et le mois le plus frais de l'année.
              </p>
            </div>

            <!-- Régression -->
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <strong class="text-indigo-900 block text-base mb-1">📉 Régression Linéaire Simple</strong>
              <p class="mt-1">
                Cet onglet cherche à savoir si une variable (comme l'humidité) influence directement la température. L'ordinateur trace une <strong>droite de prédiction</strong> au milieu du nuage de points. Le score affiché (appelé R²) explique en pourcentage à quel point cette relation est fiable. Plus le pourcentage est élevé, plus le lien entre les deux variables est fort.
              </p>
            </div>

            <!-- Corrélations -->
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <strong class="text-indigo-900 block text-base mb-1">🧮 Corrélations (Heatmap)</strong>
              <p class="mt-1">
                Ici, les mathématiques mesurent la dépendance entre toutes les variables prises deux par deux. L'application calcule un score d'association. L'interface traduit ce score mathématique en couleur : si deux variables augmentent ensemble, la case devient <strong>rouge</strong>. Si l'une baisse quand l'autre monte, la case devient <strong>bleue</strong>.
              </p>
            </div>

            <!-- Prédictions IA -->
            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100">
              <strong class="text-indigo-900 block text-base mb-1">🔮 Prédictions IA (Modèle Multiple)</strong>
              <p class="mt-1">
                C'est la partie la plus avancée. Lorsque vous validez le formulaire, le modèle mathématique combine simultanément l'humidité, la pression et le vent. En appliquant des coefficients d'importance à chaque critère, il calcule instantanément la température estimée. Le bouton d'explication affiche ensuite la recette de calcul utilisée par l'algorithme.
              </p>
            </div>

          </div>
        </div>

        <!-- 3. TECHNOLOGIES -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 space-y-3">
          <h2 class="text-lg font-bold text-gray-800 flex items-center gap-2 border-b pb-2 border-gray-100">
            <span class="text-emerald-500">⚡</span> Technologies employées
          </h2>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs font-bold text-gray-700">
            <div class="p-3 bg-gray-50 border rounded-xl">Vue.js 3</div>
            <div class="p-3 bg-gray-50 border rounded-xl">FastAPI (Python)</div>
            <div class="p-3 bg-gray-50 border rounded-xl">Tailwind CSS</div>
            <div class="p-3 bg-gray-50 border rounded-xl">Chart.js</div>
            <div class="p-3 bg-gray-50 border rounded-xl">Scikit-Learn</div>
            <div class="p-3 bg-gray-50 border rounded-xl">Pandas & NumPy</div>
            <div class="p-3 bg-gray-50 border rounded-xl">Vite</div>
            <div class="p-3 bg-gray-50 border rounded-xl">Git / GitHub</div>
          </div>
        </div>

      </div>

      <!-- COLONNE DROITE : LES AUTEURS (UNIQUEMENT NOM ET PRÉNOM) -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 flex flex-col justify-between">
        <div>
          <h2 class="text-lg font-bold text-gray-800 flex items-center gap-2 border-b pb-3 border-gray-100">
            <span class="text-rose-500">👥</span> Équipe de développement
          </h2>
          <p class="text-xs text-gray-400 mt-2 mb-4">Auteurs ayant contribué au projet :</p>
          
          <ol class="space-y-2.5">
            <li 
              v-for="(auteur, index) in auteurs" 
              :key="index" 
              class="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-xl transition text-sm font-semibold text-gray-700"
            >
              <span class="flex items-center justify-center bg-rose-50 border border-rose-100 text-rose-600 rounded-lg w-6 h-6 text-xs font-bold">
                {{ index + 1 }}
              </span>
              <span class="uppercase tracking-wide text-xs">{{ auteur }}</span>
            </li>
          </ol>
        </div>
        
        <div class="pt-6 border-t border-gray-100 text-center text-[10px] text-gray-400 font-mono">
          Université Ouaga | Projet d'Études
        </div>
      </div>

    </div>
  </div>
</template>

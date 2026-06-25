<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

// Enregistrement des éléments pour le graphique à barres de la saisonnalité
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

// États de l'application
const variable = ref('temperature')
const donneesTendance = ref(null)
const donneesSaisonnalite = ref(null)
const chargement = ref(true)
const erreur = ref(null)

const API_BASE_URL = 'http://127.0.0.1:8000'

// Fonction pour charger simultanément les deux routes de FastAPI
const chargerDonneesAnalytiques = async () => {
  chargement.value = true
  erreur.value = null
  try {
    const [reponseTendance, reponseSaisonnalite] = await Promise.all([
      fetch(`${API_BASE_URL}/series/tendance?variable=${variable.value}`),
      fetch(`${API_BASE_URL}/series/saisonnalite?variable=${variable.value}`)
    ])

    if (!reponseTendance.ok || !reponseSaisonnalite.ok) {
      throw new Error("Erreur lors de la récupération des données de séries temporelles.")
    }

    donneesTendance.value = await reponseTendance.json()
    donneesSaisonnalite.value = await reponseSaisonnalite.json()
  } catch (err) {
    erreur.value = err.message
    console.error(err)
  } finally {
    chargement.value = false
  }
}

// Recharger dès que l'utilisateur sélectionne un autre indicateur météo
watch(variable, () => {
  chargerDonneesAnalytiques()
})

onMounted(() => {
  chargerDonneesAnalytiques()
})

// ─── CONFIGURATION DU GRAPHIQUE BARRE (SAISONNALITÉ) ───
const chartDataSaison = computed(() => {
  if (!donneesSaisonnalite.value) return { labels: [], datasets: [] }

  const listeMois = donneesSaisonnalite.value.saisonnalite
  
  return {
    labels: listeMois.map(m => m.nom), // ["Jan", "Fév", "Mar", ...]
    datasets: [
      {
        label: `Moyenne Mensuelle globale`,
        data: listeMois.map(m => m.moyenne),
        backgroundColor: 'rgba(79, 70, 229, 0.8)', // Indigo
        borderRadius: 8,
        hoverBackgroundColor: 'rgba(79, 70, 229, 1)'
      }
    ]
  }
})

const chartOptionsSaison = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: {
        title: {
          display: true,
          text: `Valeur Moyenne (${variable.value})`,
          font: { weight: 'bold' }
        }
      }
    }
  }
})
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto space-y-6 bg-gray-50 min-h-screen">
    
    <!-- En-tête de Sélection -->
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black text-gray-900 tracking-tight">Profils Saisonniers & Tendances</h1>
        <p class="text-sm text-gray-500 mt-1">Modèles de décomposition analytique pour Ouagadougou</p>
      </div>
      <div>
        <select v-model="variable" class="bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-xl p-2.5 font-semibold focus:ring-2 focus:ring-indigo-500">
          <option value="temperature">Température</option>
          <option value="humidite">Humidité</option>
          <option value="pression">Pression</option>
          <option value="vent">Vitesse du vent</option>
          <option value="precipitations">Précipitations</option>
        </select>
      </div>
    </div>

    <!-- Indicateurs graphiques d'attente / d'erreur -->
    <div v-if="chargement" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
    <div v-else-if="erreur" class="p-4 bg-red-100 text-red-700 rounded-xl border border-red-200">{{ erreur }}</div>

    <!-- Contenu Principal -->
    <div v-else class="space-y-6">
      
      <!-- 1. BLOC TENDANCE GÉNÉRALE (Texte explicite de FastAPI) -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
        <h2 class="text-sm font-bold text-gray-400 uppercase tracking-wider mb-2">Analyse Thermique et Temporelle globale</h2>
        
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <p class="text-lg font-bold text-gray-800 md:max-w-2xl">
            📈 Tendance : <span class="text-indigo-600 font-black">{{ donneesTendance.tendance.interpretation }}</span>
          </p>
          <div class="px-4 py-2 rounded-xl text-xs font-bold font-mono shadow-inner whitespace-nowrap"
               :class="donneesTendance.tendance.sens === 'hausse' ? 'bg-orange-50 text-orange-700' : 'bg-blue-50 text-blue-700'">
            Sens détecté : {{ donneesTendance.tendance.sens.toUpperCase() }}
          </div>
        </div>

        <!-- Chiffres clés de la Tendance -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
          <div class="p-4 bg-gray-50 border border-gray-100 rounded-xl">
            <span class="text-xs text-gray-400 font-medium block">Période d'analyse</span>
            <span class="text-sm font-bold text-gray-700 block mt-1">
              {{ donneesTendance.periode.debut }} au {{ donneesTendance.periode.fin }}
            </span>
          </div>
          <div class="p-4 bg-gray-50 border border-gray-100 rounded-xl">
            <span class="text-xs text-gray-400 font-medium block">Variation annuelle moyenne</span>
            <span class="text-lg font-black text-gray-800 block mt-1">
              {{ donneesTendance.tendance.variation_annuelle > 0 ? '+' : '' }}{{ donneesTendance.tendance.variation_annuelle }}
            </span>
          </div>
          <div class="p-4 bg-gray-50 border border-gray-100 rounded-xl">
            <span class="text-xs text-gray-400 font-medium block">Variation cumulée</span>
            <span class="text-lg font-black text-gray-800 block mt-1">
              {{ donneesTendance.tendance.variation_totale_periode > 0 ? '+' : '' }}{{ donneesTendance.tendance.variation_totale_periode }} (sur {{ donneesTendance.periode.nb_jours }}j)
            </span>
          </div>
        </div>
      </div>

      <!-- 2. BLOC SAISONNALITÉ (Graphique en barres et Résumé statistique) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Le Graphique à barres -->
        <div class="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
          <h3 class="text-lg font-bold text-gray-800 mb-4">Profil Mensuel Moyen (Sur l'ensemble des années)</h3>
          <div class="h-80">
            <Bar :data="chartDataSaison" :options="chartOptionsSaison" />
          </div>
        </div>

        <!-- Les Observations Extrêmes de FastAPI -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 flex flex-col justify-between space-y-4">
          <div>
            <h3 class="text-lg font-bold text-gray-800 border-b pb-3 border-gray-100">Points de Rupture</h3>
            <p class="text-xs text-gray-400 mt-1">Extrêmes saisonniers calculés automatiquement :</p>
          </div>

          <div class="space-y-3 flex-grow justify-center flex flex-col">
            <!-- Maximum cyclique -->
            <div class="p-4 bg-rose-50 rounded-xl border border-rose-100">
              <span class="text-xs font-bold text-rose-600 uppercase block tracking-wider">Mois le plus élevé</span>
              <div class="flex justify-between items-baseline mt-1">
                <span class="text-xl font-black text-rose-900">{{ donneesSaisonnalite.observations.mois_max }}</span>
                <span class="text-sm font-bold text-rose-700">{{ donneesSaisonnalite.observations.valeur_max }}</span>
              </div>
            </div>

            <!-- Minimum cyclique -->
            <div class="p-4 bg-sky-50 rounded-xl border border-sky-100">
              <span class="text-xs font-bold text-sky-600 uppercase block tracking-wider">Mois le plus bas</span>
              <div class="flex justify-between items-baseline mt-1">
                <span class="text-xl font-black text-sky-900">{{ donneesSaisonnalite.observations.mois_min }}</span>
                <span class="text-sm font-bold text-sky-700">{{ donneesSaisonnalite.observations.valeur_min }}</span>
              </div>
            </div>
          </div>

          <!-- Amplitude Saisonnante -->
          <div class="p-3 bg-purple-50 rounded-xl text-center border border-purple-100">
            <span class="text-xs font-semibold text-purple-700 block">Amplitude thermique / saisonnière</span>
            <span class="text-xl font-black text-purple-900 mt-1 block">
              {{ donneesSaisonnalite.observations.amplitude }} unités
            </span>
          </div>

        </div>

      </div>

    </div>
  </div>
</template>

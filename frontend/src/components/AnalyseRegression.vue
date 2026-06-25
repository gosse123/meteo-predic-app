<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Scatter } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  ScatterController
} from 'chart.js'

// Enregistrement des modules nécessaires pour Chart.js
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  ScatterController
)

const variableSelectionnee = ref('humidite')
const donneesRegression = ref(null)
const chargement = ref(true)
const erreur = ref(null)

const API_BASE_URL = 'http://127.0.0.1:8000'

const chargerAnalyseSimple = async () => {
  chargement.value = true
  erreur.value = null
  try {
    const reponse = await fetch(`${API_BASE_URL}/analyse/regression/simple?variable_x=${variableSelectionnee.value}`)
    if (!reponse.ok) throw new Error(`Erreur serveur : ${reponse.status}`)
    donneesRegression.value = await reponse.json()
  } catch (err) {
    erreur.value = "Impossible de récupérer les analyses mathématiques."
    console.error(err)
  } finally {
    chargement.value = false
  }
}

watch(variableSelectionnee, () => {
  chargerAnalyseSimple()
})

onMounted(() => {
  chargerAnalyseSimple()
})

// ─── CONFIGURATION DES DONNÉES DU GRAPHIQUE ───
const chartData = computed(() => {
  if (!donneesRegression.value) return { datasets: [] }

  const nuage = donneesRegression.value.nuage_test
  const droite = donneesRegression.value.droite_regression

  // Formatage des points réels (Scatter)
  const pointsReels = nuage.x.map((xVal, index) => ({
    x: xVal,
    y: nuage.y_reel[index]
  }))

  // Formatage des points de la droite de régression (Line)
  const pointsDroite = droite.x.map((xVal, index) => ({
    x: xVal,
    y: droite.y[index]
  }))

  return {
    datasets: [
      {
        type: 'line',
        label: 'Droite de régression (Prédiction)',
        data: pointsDroite,
        borderColor: '#4f46e5', // Indigo Tailwind
        borderWidth: 3,
        pointRadius: 0, // Pas de points visibles sur la ligne
        fill: false,
        tension: 0
      },
      {
        type: 'scatter',
        label: 'Données réelles (Test)',
        data: pointsReels,
        backgroundColor: 'rgba(245, 158, 11, 0.6)', // Amber Tailwind
        pointRadius: 5
      }
    ]
  }
})

// Options de configuration pour les axes du graphique
const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        title: {
          display: true,
          text: variableSelectionnee.value.toUpperCase(),
          font: { weight: 'bold' }
        }
      },
      y: {
        title: {
          display: true,
          text: 'Température (°C)',
          font: { weight: 'bold' }
        }
      }
    }
  }
})
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto space-y-6 bg-gray-50 min-h-screen">
    
    <!-- Menu d'en-tête (Inchangé) -->
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-black text-gray-900 tracking-tight">Visualisation Mathématique</h1>
        <p class="text-sm text-gray-500 mt-1">Régression linéaire sur le climat de Ouagadougou</p>
      </div>
      <div class="flex items-center gap-2">
        <label for="variable" class="text-sm font-semibold text-gray-700">Variable X :</label>
        <select id="variable" v-model="variableSelectionnee" class="bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-lg p-2.5 font-medium">
          <option value="humidite">Humidité</option>
          <option value="pression">Pression</option>
          <option value="vent">Vitesse du vent</option>
          <option value="precipitations">Précipitations</option>
        </select>
      </div>
    </div>

    <!-- Chargement & Erreur -->
    <div v-if="chargement" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
    <div v-else-if="erreur" class="p-4 bg-red-100 text-red-700 rounded-xl border border-red-200">{{ erreur }}</div>

    <!-- Tableau de bord principal -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Graphique Interactif Chart.js -->
      <div class="lg:col-span-2 bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
        <h3 class="text-lg font-bold text-gray-800 mb-4">Nuage de points & Modèle linéaire</h3>
        <div class="h-80">
          <Scatter :data="chartData" :options="chartOptions" />
        </div>
      </div>

      <!-- Métriques et Formule (Format compact) -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 flex flex-col justify-between space-y-4">
        <div>
          <h3 class="text-lg font-bold text-gray-800 border-b pb-2 border-gray-100">Analyse Algébrique</h3>
          <div class="my-4 p-3 bg-gray-900 text-green-400 font-mono text-xs text-center rounded-xl shadow-inner">
            {{ donneesRegression.equation.formule }}
          </div>
        </div>

        <div class="space-y-3">
          <div class="p-3 bg-indigo-50 rounded-xl">
            <div class="flex justify-between items-baseline">
              <span class="text-xs font-bold text-indigo-600 uppercase">R² (Score)</span>
              <span class="text-xl font-black text-indigo-900">{{ donneesRegression.metriques.R2 }}</span>
            </div>
            <p class="text-xs text-indigo-700 mt-1">{{ donneesRegression.metriques.interpretation_R2 }}</p>
          </div>

          <div class="p-3 bg-amber-50 rounded-xl">
            <span class="text-xs font-bold text-amber-700 uppercase block">Écart Moyen (MAE)</span>
            <span class="text-lg font-bold text-amber-900">{{ donneesRegression.metriques.MAE }} °C</span>
          </div>
        </div>

        <div class="text-[10px] text-gray-400 pt-2 border-t border-gray-100 flex justify-between">
          <span>Train size: {{ donneesRegression.tailles.train }}</span>
          <span>Test size: {{ donneesRegression.tailles.test }}</span>
        </div>
      </div>

    </div>
  </div>
</template>

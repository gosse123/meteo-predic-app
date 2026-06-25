<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
} from 'chart.js'

// Enregistrement des éléments Chart.js nécessaires
ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement)

// États pour les filtres (liés aux Query Parameters de FastAPI)
const variable = ref('temperature')
const annee = ref('') // Vide signifie "toutes les années"
const fenetreMobile = ref(7)

const donneesEvolution = ref(null)
const chargement = ref(true)
const erreur = ref(null)

const API_BASE_URL = 'http://127.0.0.1:8000'

// Génération dynamique de la liste des années de 2020 jusqu'à l'année courante (2026)
const listeAnnees = computed(() => {
  const anneeDebut = 2020
  const anneeFin = new Date().getFullYear() // Récupère dynamiquement 2026
  const annees = []
  for (let a = anneeDebut; a <= anneeFin; a++) {
    annees.push(a)
  }
  return annees
})

// Fonction pour appeler la route /series/evolution avec les paramètres d'URL
const chargerEvolution = async () => {
  chargement.value = true
  erreur.value = null
  try {
    let url = `${API_BASE_URL}/series/evolution?variable=${variable.value}&fenetre_mobile=${fenetreMobile.value}`
    if (annee.value) {
      url += `&annee=${annee.value}`
    }

    const reponse = await fetch(url)
    if (!reponse.ok) throw new Error(`Erreur serveur : ${reponse.status}`)
    
    donneesEvolution.value = await reponse.json()
  } catch (err) {
    erreur.value = "Impossible de récupérer les séries temporelles pour cette période."
    console.error(err)
  } finally {
    chargement.value = false
  }
}

// Recharger les données si un filtre change
watch([variable, annee, fenetreMobile], () => {
  chargerEvolution()
})

onMounted(() => {
  chargerEvolution()
})

// ─── CONFIGURATION DES DONNÉES DU GRAPHIQUE TEMPOREL ───
const chartData = computed(() => {
  if (!donneesEvolution.value) return { labels: [], datasets: [] }

  const dataObj = donneesEvolution.value.donnees

  return {
    labels: dataObj.dates, 
    datasets: [
      {
        label: `Moyenne Mobile (${fenetreMobile.value}j)`,
        data: dataObj.moyenne_mobile,
        borderColor: '#f59e0b', // Ambre Tailwind
        borderWidth: 3,
        pointRadius: 0, 
        tension: 0.2, 
        fill: false
      },
      {
        label: 'Valeurs Journalières Brutes',
        data: dataObj.valeurs,
        borderColor: 'rgba(99, 102, 241, 0.3)', 
        borderWidth: 1.5,
        pointRadius: 1, 
        tension: 0,
        fill: false
      }
    ]
  }
})

// Options de configuration responsives pour Chart.js
const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { maxTicksLimit: 12 } 
      },
      y: {
        title: {
          display: true,
          text: variable.value.toUpperCase(),
          font: { weight: 'bold' }
        }
      }
    }
  }
})
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto space-y-6 bg-gray-50 min-h-screen">
    
    <!-- Barre de Filtres Complète stylisée en Tailwind -->
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
      
      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Indicateur</label>
        <select v-model="variable" class="w-full bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-xl p-2.5 font-medium focus:ring-2 focus:ring-amber-500">
          <option value="temperature">Température</option>
          <option value="humidite">Humidité</option>
          <option value="pression">Pression</option>
          <option value="vent">Vitesse du vent</option>
          <option value="precipitations">Précipitations</option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Année de filtrage</label>
        <select v-model="annee" class="w-full bg-gray-100 border border-gray-300 text-gray-900 text-sm rounded-xl p-2.5 font-medium focus:ring-2 focus:ring-amber-500">
          <option value="">Toutes les années</option>
          <!-- Boucle dynamique sur les années générées (2020-2026) -->
          <option v-for="a in listeAnnees" :key="a" :value="a">
            {{ a }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Lissage : Moyenne Mobile ({{ fenetreMobile }}j)</label>
        <input 
          type="range" 
          v-model.number="fenetreMobile" 
          min="2" 
          max="30" 
          class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-amber-500 my-3"
        />
      </div>

      <div class="text-right">
        <span v-if="donneesEvolution" class="text-xs text-gray-400 block pb-1">
          Observations : <strong>{{ donneesEvolution.n_observations }}</strong> lignes
        </span>
        <button @click="chargerEvolution" class="w-full md:w-auto bg-amber-500 hover:bg-amber-600 text-white font-semibold text-sm px-5 py-2.5 rounded-xl transition">
          Actualiser
        </button>
      </div>

    </div>

    <!-- Gestion des États Graphiques -->
    <div v-if="chargement" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
    </div>
    
    <div v-else-if="erreur" class="p-4 bg-red-100 text-red-700 rounded-xl border border-red-200">
      {{ erreur }}
    </div>

    <!-- Zone d'affichage principale -->
    <div v-else class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-black text-gray-800 tracking-tight">Chronologie & Analyse Temporelle</h2>
        <span class="text-xs font-medium text-gray-400">Période : {{ annee || 'Historique Complet' }}</span>
      </div>
      
      <div class="h-96">
        <Line :data="chartData" :options="chartOptions" />
      </div>
    </div>

  </div>
</template>

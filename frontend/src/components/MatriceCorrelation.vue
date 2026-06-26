<script setup>
import { ref, onMounted } from 'vue'

const donnees = ref(null)
const chargement = ref(true)
const erreur = ref(null)

const API_BASE_URL = 'http://127.0.0.1:8000'

const chargerCorrelation = async () => {
  try {
    const reponse = await fetch(`${API_BASE_URL}/analyse/correlation`)
    if (!reponse.ok) throw new Error("Erreur lors de la récupération de la matrice")
    donnees.value = await reponse.json()
  } catch (err) {
    erreur.value = err.message
  } finally {
    chargement.value = false
  }
}

// Fonction utilitaire Tailwind pour colorer dynamiquement les cases (Heatmap)
const obtenirStyleCellule = (valeur) => {
  if (valeur === 1) return 'bg-gray-200 text-gray-800 font-bold'
  if (valeur > 0.5) return 'bg-red-500 text-white font-semibold'
  if (valeur > 0.2) return 'bg-red-200 text-red-900'
  if (valeur < -0.5) return 'bg-blue-500 text-white font-semibold'
  if (valeur < -0.2) return 'bg-blue-200 text-blue-900'
  return 'bg-gray-50 text-gray-600'
}

onMounted(() => {
  chargerCorrelation()
})
</script>

<template>
  <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 space-y-6">
    <div v-if="chargement" class="text-center py-10 text-indigo-500 animate-pulse">Chargement de la matrice...</div>
    <div v-else-if="erreur" class="text-red-500 p-4 bg-red-50 rounded-xl">Erreur : {{ erreur }}</div>
    
    <div v-else class="space-y-6">
      <div>
        <h3 class="text-lg font-bold text-gray-800">Matrice de Corrélation de Pearson</h3>
        <p class="text-sm text-gray-500">Analyse croisée des variables du climat de Ouagadougou</p>
      </div>

      <!-- Grille Graphique de type Heatmap -->
      <div class="overflow-x-auto">
        <table class="w-full table-fixed border-collapse text-sm text-center">
          <thead>
            <tr class="bg-gray-50/80">
              <th class="p-3 text-left font-bold text-gray-600 border-b">Variables</th>
              <th v-for="v in donnees.variables" :key="v" class="p-3 font-bold text-gray-600 border-b capitalize">
                {{ v }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="varLigne in donnees.variables" :key="varLigne" class="border-b border-gray-100">
              <td class="p-3 text-left font-bold text-gray-700 capitalize bg-gray-50/50">{{ varLigne }}</td>
              <td 
                v-for="varCol in donnees.variables" 
                :key="varCol" 
                :class="obtenirStyleCellule(donnees.matrice[varLigne][varCol])"
                class="p-4 border transition duration-150"
              >
                {{ donnees.matrice[varLigne][varCol] }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Interprétations textuelles automatisées de FastAPI -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-100">
        <div class="p-4 bg-indigo-50/50 border border-indigo-100 rounded-xl">
          <span class="text-xs font-bold text-indigo-600 uppercase tracking-wider block">Humidité & Précipitations</span>
          <p class="text-sm text-gray-700 font-semibold mt-1">{{ donnees.interpretation.humidite_precipitations.sens }}</p>
        </div>
        <div class="p-4 bg-amber-50/50 border border-amber-100 rounded-xl">
          <span class="text-xs font-bold text-amber-600 uppercase tracking-wider block">Pression & Température</span>
          <p class="text-sm text-gray-700 font-semibold mt-1">{{ donnees.interpretation.pression_temperature.sens }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

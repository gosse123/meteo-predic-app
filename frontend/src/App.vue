<script setup>
import { ref } from 'vue'
import EvolutionTemporelle from './components/EvolutionTemporelle.vue'
import SaisonnaliteEtTendance from './components/SaisonnaliteEtTendance.vue'
import AnalyseRegression from './components/AnalyseRegression.vue'
import MatriceCorrelation from './components/MatriceCorrelation.vue'

// Gestion de l'onglet actif
const ongletActif = ref('series')
</script>

<template>
  <div class="min-h-screen bg-gray-100 text-gray-800">
    <!-- Barre de navigation du Dashboard -->
    <header class="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div class="max-w-6xl mx-auto px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <span class="text-2xl">🌤️</span>
          <h1 class="text-xl font-black text-gray-900 tracking-tight">Météo Ouaga Analytics</h1>
        </div>
        
        <!-- Liste des Onglets -->
        <nav class="flex space-x-1 bg-gray-100 p-1 rounded-xl">
          <button 
            @click="ongletActif = 'series'"
            :class="ongletActif === 'series' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-900'"
            class="px-4 py-2 text-xs font-bold rounded-lg transition"
          >
            Séries Temporelles
          </button>
          <button 
            @click="ongletActif = 'saison'"
            :class="ongletActif === 'saison' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-900'"
            class="px-4 py-2 text-xs font-bold rounded-lg transition"
          >
            Saisonnalité
          </button>
          <button 
            @click="ongletActif = 'regression'"
            :class="ongletActif === 'regression' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-900'"
            class="px-4 py-2 text-xs font-bold rounded-lg transition"
          >
            Régression
          </button>
          <button 
            @click="ongletActif = 'correlation'"
            :class="ongletActif === 'correlation' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-900'"
            class="px-4 py-2 text-xs font-bold rounded-lg transition"
          >
            Corrélations
          </button>
        </nav>
      </div>
    </header>

    <!-- Zone de Rendu Dynamique du Contenu -->
    <main class="py-6">
      <KeepAlive>
        <component :is="
          ongletActif === 'series' ? EvolutionTemporelle :
          ongletActif === 'saison' ? SaisonnaliteEtTendance :
          ongletActif === 'regression' ? AnalyseRegression :
          MatriceCorrelation
        " />
      </KeepAlive>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

// Données du formulaire
const humidite = ref(null)
const pression = ref(null)
const vent = ref(null)

// États de la requête
const resultat = ref(null)
const chargement = ref(false)
const erreur = ref(null)
const afficherExplication = ref(false)

const API_BASE_URL = 'http://127.0.0.1:8000'

// Vérification stricte : tous les champs doivent être remplis et numériques
const formulaireEstValide = computed(() => {
  return humidite.value !== null && humidite.value !== '' &&
         pression.value !== null && pression.value !== '' &&
         vent.value !== null && vent.value !== ''
})

const soumettrePrediction = async () => {
  if (!formulaireEstValide.value) return

  chargement.value = true
  erreur.value = null
  resultat.value = null
  afficherExplication.value = false

  try {
    const reponse = await fetch(`${API_BASE_URL}/analyse/predire-temperature`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        humidite: Number(humidite.value),
        pression: Number(pression.value),
        vent: Number(vent.value)
      })
    })

    if (!reponse.ok) throw new Error("Le serveur a refusé la prédiction. Vérifiez vos valeurs.")
    resultat.value = await reponse.json()
  } catch (err) {
    erreur.value = err.message
  } finally {
    chargement.value = false
  }
}

// Données pour le Graphique de positionnement
const chartData = computed(() => {
  if (!resultat.value) return { labels: [], datasets: [] }
  return {
    labels: ['Température Prédite', 'Moyenne Historique de Ouaga'],
    datasets: [
      {
        label: 'Degrés Celsius (°C)',
        data: [resultat.value.temperature_predite, 28.5], // 28.5 est la moyenne générale théorique
        backgroundColor: ['#f43f5e', '#94a3b8'], // Rose pour la prédiction, Gris pour la moyenne
        borderRadius: 8
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: { y: { min: 15, max: 45 } }
}
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto space-y-6 bg-gray-50 min-h-screen">
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- 1. FORMULAIRE DE SAISIE -->
      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
        <h2 class="text-xl font-black text-gray-900 mb-4">Calculateur Prédictif</h2>
        <p class="text-xs text-gray-500 mb-6">Entrez les paramètres actuels pour estimer la température via Intelligence Artificielle.</p>
        
        <form @submit.prevent="soumettrePrediction" class="space-y-4">
          <div>
            <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Humidité (%)</label>
            <input v-model="humidite" type="number" min="0" max="100" step="0.1" placeholder="Ex: 45" class="w-full bg-gray-50 border p-2.5 rounded-xl text-sm focus:ring-2 focus:ring-rose-500" required />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Pression Atmosphérique (hPa)</label>
            <input v-model="pression" type="number" min="900" max="1100" step="0.1" placeholder="Ex: 1011" class="w-full bg-gray-50 border p-2.5 rounded-xl text-sm focus:ring-2 focus:ring-rose-500" required />
          </div>

          <div>
            <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Vitesse du vent (km/h)</label>
            <input v-model="vent" type="number" min="0" max="150" step="0.1" placeholder="Ex: 15" class="w-full bg-gray-50 border p-2.5 rounded-xl text-sm focus:ring-2 focus:ring-rose-500" required />
          </div>

          <button 
            type="submit" 
            :disabled="!formulaireEstValide || chargement"
            :class="formulaireEstValide ? 'bg-rose-500 hover:bg-rose-600 text-white' : 'bg-gray-200 text-gray-400 cursor-not-allowed'"
            class="w-full font-bold p-3 rounded-xl text-sm transition shadow-sm mt-2"
          >
            {{ chargement ? 'Calcul de l\'algorithme...' : 'Prédire la Température' }}
          </button>
        </form>
      </div>

      <!-- 2. ZONE D'AFFICHAGE DU RÉSULTAT & GRAPHIC -->
      <div class="lg:col-span-2 space-y-6">
        
        <!-- Si aucune donnée n'a encore été soumise -->
        <div v-if="!resultat && !chargement && !erreur" class="bg-white p-12 rounded-2xl shadow-sm border border-gray-200 text-center text-gray-400">
          <span class="text-4xl block mb-2">🤖</span>
          Veuillez remplir le formulaire et cliquer sur le bouton pour générer la prédiction mathématique.
        </div>

        <div v-if="erreur" class="p-4 bg-red-100 text-red-700 rounded-xl border border-red-200">{{ erreur }}</div>

        <!-- Si le résultat est disponible -->
        <div v-if="resultat" class="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          <!-- Carte Température -->
          <div class="bg-gradient-to-br from-rose-500 to-orange-500 p-6 rounded-2xl text-white shadow-md flex flex-col justify-between">
            <div>
              <span class="text-xs font-bold uppercase opacity-80">Résultat de la simulation</span>
              <h3 class="text-4xl font-black mt-2">{{ resultat.temperature_predite }} °C</h3>
            </div>
            
            <!-- LE BOUTON EXPLICATION (Uniquement visible si résultat présent) -->
            <button 
              @click="afficherExplication = !afficherExplication" 
              class="mt-6 bg-white/20 hover:bg-white/30 text-white font-bold text-xs py-2 px-4 rounded-xl transition text-center"
            >
              {{ afficherExplication ? 'Masquer l\'explication' : '💡 Comment ça fonctionne ?' }}
            </button>
          </div>

          <!-- Le Graphique à barres comparatif -->
          <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-200 h-56 md:h-auto">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
        </div>

        <!-- 3. ZONE EXPLICATION DYNAMIQUE (Dépliante) -->
        <div v-if="afficherExplication && resultat" class="bg-slate-900 text-slate-300 p-6 rounded-2xl shadow-inner space-y-3 font-mono text-xs border border-slate-800">
          <h4 class="text-green-400 font-bold text-sm border-b border-slate-800 pb-2">🧠 Rapport de l'Algorithme (Scikit-Learn)</h4>
          <p>Le backend a appliqué un modèle de <span class="text-white">Régression Linéaire Multiple</span> entraîné sur l'historique de Ouagadougou.</p>
          
          <div class="bg-slate-950 p-3 rounded-lg text-green-400 overflow-x-auto my-3 text-center text-sm">
            {{ resultat.details_modele.formule_complete }}
          </div>

          <h5 class="text-white font-bold mt-2">Détails des calculs appliqués :</h5>
          <ul class="list-disc pl-4 space-y-1">
            <li>L'humidité augmente l'indice de chaleur mais ici son poids d'ajustement est de : <span class="text-yellow-400">{{ resultat.details_modele.coef_humidite }}</span></li>
            <li>Le poids multiplicateur de la pression de l'air est de : <span class="text-yellow-400">{{ resultat.details_modele.coef_pression }}</span></li>
            <li>L'impact thermique de la vitesse du vent est de : <span class="text-yellow-400">{{ resultat.details_modele.coef_vent }}</span></li>
            <li>La constante de base (ordonnée à l'origine $b$) est fixée à : <span class="text-yellow-400">{{ resultat.details_modele.ordonnee_b }}</span></li>
          </ul>
        </div>

      </div>
    </div>
  </div>
</template>

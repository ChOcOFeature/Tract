# 🗳️ Tractage Electoral - Les Sables d'Olonne

## 📦 Projet complet

Ce projet contient tous les outils pour optimiser votre campagne de tractage électoral.

## 📂 Structure

```
Tract/
├── analyse_electeurs.py                    # Script 1: Analyse de base
├── analyse_tractage_avancee.py            # Script 2: Analyses avancées
├── preparer_donnees_web.py                # Script 3: Préparation web
├── tractage-app/                          # Application web Next.js
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
└── ListesElecteursActifs-com85194-...csv  # Données source
```

## 🚀 Guide d'utilisation complet

### Étape 1 : Analyser les données

```bash
# Analyse de base (foyers, natifs, âges)
python analyse_electeurs.py

# Analyses avancées (rues, segments, cartographie)
python analyse_tractage_avancee.py
```

**Fichiers générés :**
- `rapport_ciblage_tractage.csv`
- `foyers_par_adresse.csv`
- `segmentation_electeurs_detaillee.csv` ⭐
- `top_rues_prioritaires.csv`
- `cartographie_google_maps.csv`
- Et plus...

### Étape 2 : Préparer pour le web

```bash
# Copier les données dans l'application
python preparer_donnees_web.py
```

### Étape 3 : Lancer l'application web

```bash
# Aller dans le dossier de l'application
cd tractage-app

# Installer les dépendances (première fois seulement)
npm install

# Lancer en mode développement
npm run dev
```

Ouvrez [http://localhost:3000](http://localhost:3000)

### Étape 4 : Déployer sur Vercel

Voir le guide détaillé : `tractage-app/DEPLOIEMENT.md`

**En résumé :**
1. Créer un compte sur [vercel.com](https://vercel.com)
2. Connecter votre repository GitHub
3. Cliquer sur "Deploy"
4. ✨ Votre site est en ligne !

## 🎯 Fonctionnalités

### Scripts Python

- ✅ Analyse de 42,768 électeurs
- ✅ Identification de 26,101 foyers
- ✅ Segmentation en 7 profils
- ✅ Calcul de scores de priorité
- ✅ Export pour Google Maps/Earth

### Application Web

- 🗺️ **Carte interactive** avec tous les foyers
- 🔍 **Recherche** par adresse ou nom
- 🎯 **Filtrage** par segment démographique
- 💬 **Messages adaptés** pour chaque profil
- 📊 **Statistiques** en temps réel
- 📱 **Responsive** (desktop, tablette)

## 📊 Les 7 segments d'électeurs

| Segment | % | Âge | Message |
|---------|---|-----|---------|
| 🎓 Jeunes | 7.8% | 18-25 | Avenir, emploi, logement |
| 🏡 Jeunes actifs natifs | 4.3% | 26-35 | Développement local |
| 🤝 Jeunes actifs nouveaux | 4.4% | 26-35 | Accueil, intégration |
| 👨‍👩‍👧‍👦 Familles actives | 14% | 36-50 | École, sécurité |
| 🏛️ Seniors actifs natifs | 7.9% | 51-65 | Patrimoine, tradition |
| 🌊 Seniors actifs non natifs | 14.3% | 51-65 | Qualité de vie |
| 🏥 Retraités | 47.2% | 66+ | Santé, proximité |

## 🛠️ Technologies

- **Python 3** + pandas pour l'analyse
- **Next.js 14** pour l'application web
- **TypeScript** pour la robustesse
- **Leaflet** pour les cartes
- **Tailwind CSS** pour le design
- **Vercel** pour l'hébergement

## 📝 Prérequis

### Pour les scripts Python

```bash
pip install pandas
```

### Pour l'application web

- Node.js 18+ ([nodejs.org](https://nodejs.org))
- npm (inclus avec Node.js)

## 🆘 Support

### Problèmes communs

**Python : "ModuleNotFoundError: No module named 'pandas'"**
```bash
pip install pandas
```

**Node : "command not found"**
- Installez Node.js depuis [nodejs.org](https://nodejs.org)

**L'application ne démarre pas**
```bash
cd tractage-app
rm -rf node_modules .next
npm install
npm run dev
```

**La carte ne s'affiche pas**
- Vérifiez votre connexion internet (Leaflet utilise OpenStreetMap)
- Attendez quelques secondes le chargement

## 📱 Utilisation terrain

### Workflow recommandé

1. **Préparation :**
   - Exécutez les scripts Python
   - Déployez l'application sur Vercel
   - Partagez l'URL avec votre équipe

2. **Sur le terrain :**
   - Consultez l'application sur mobile/tablette
   - Filtrez par bureau ou segment
   - Copiez les messages adaptés
   - Marquez les adresses visitées

3. **Suivi :**
   - Analysez les zones couvertes
   - Ajustez la stratégie
   - Concentrez sur les priorités

## 🎯 Conseils tactiques

### Top 3 des bureaux prioritaires

1. **Bureau 22** - Salle Calixte-Aimé Plissonneau N°2
   - 57% foyers familles
   - Âge moyen 51 ans
   - Score 64/100

2. **Bureau 32** - Mairie Annexe Olonne N°2
   - 59% foyers familles
   - Âge moyen 54 ans
   - Score 64/100

3. **Bureau 31** - Le Stella
   - 55% foyers familles
   - 49% natifs Vendée
   - Score 63/100

### Messages les plus efficaces

- **Familles** : École, sécurité, activités enfants
- **Retraités** : Santé, services proximité
- **Jeunes** : Emploi, logement, avenir

## 📄 Licence & Mentions

- Données : Liste électorale Les Sables d'Olonne
- Application : Usage campagne électorale
- Open Source : Next.js, Leaflet, Tailwind CSS

## 🙏 Remerciements

Merci à tous les bénévoles qui utilisent ces outils pour améliorer notre démocratie locale !

---

**Bon tractage ! 🎯🗳️**

Pour toute question : consultez les README.md dans chaque dossier.

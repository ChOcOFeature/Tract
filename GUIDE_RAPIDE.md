# 🚀 GUIDE DE DÉMARRAGE RAPIDE

## ⚡ En 3 étapes

### 1️⃣ Analyser vos données (une seule fois)

```bash
python analyse_tractage_avancee.py
```

✅ Génère `segmentation_electeurs_detaillee.csv`

### 2️⃣ Lancer l'application

**Windows :**
Double-cliquez sur `DEMARRER_APP.bat`

**Ou en ligne de commande :**
```bash
cd tractage-app
npm install    # Première fois seulement
npm run dev
```

### 3️⃣ Utiliser l'application

1. Ouvrez http://localhost:3000
2. Cliquez sur "Charger les données CSV"
3. Sélectionnez `segmentation_electeurs_detaillee.csv`
4. Explorez la carte ! 🗺️

## 📱 Fonctionnalités

### 🗺️ Carte interactive
- Chaque point = un foyer
- Couleur = segment démographique
- Taille = nombre d'électeurs
- Clic = détails complets

### 🔍 Recherche intelligente
- Par adresse
- Par nom de famille
- Par segment

### 💬 Messages personnalisés
- 7 profils d'électeurs différents
- 3 longueurs (court/moyen/long)
- Copie en un clic

### 📊 Informations affichées
- Nombre d'électeurs par foyer
- Âge moyen
- Natif Vendée (🏠)
- Segment dominant
- Messages adaptés

## 🌐 Déployer sur Internet (Vercel)

### Pourquoi déployer ?
- ✅ Accessible depuis n'importe où
- ✅ Partager avec toute l'équipe
- ✅ Utiliser sur mobile/tablette
- ✅ Gratuit et rapide (3 minutes)

### Comment ?

1. **Créer un compte Vercel**
   - Aller sur https://vercel.com/signup
   - S'inscrire avec GitHub

2. **Pousser sur GitHub**
   ```bash
   git init
   git add .
   git commit -m "Application tractage"
   git remote add origin https://github.com/VOTRE-NOM/tractage.git
   git push -u origin main
   ```

3. **Connecter à Vercel**
   - Sur vercel.com, cliquer "New Project"
   - Importer depuis GitHub
   - Cliquer "Deploy"
   
4. **C'est prêt ! 🎉**
   - Vous obtenez une URL : `https://votre-projet.vercel.app`
   - Partagez-la avec votre équipe

## 🎯 Utilisation terrain

### Scénario 1 : Bureau ordinateur
1. Lancer l'application en local
2. Charger les données
3. Filtrer par bureau de vote
4. Imprimer les messages

### Scénario 2 : Mobile/Tablette
1. Déployer sur Vercel
2. Accéder à l'URL depuis n'importe où
3. Consulter en temps réel sur le terrain
4. Copier les messages adaptés

### Scénario 3 : Équipe distribuée
1. Déployer sur Vercel
2. Chaque bénévole accède à l'URL
3. Chacun voit les mêmes données
4. Coordination facilitée

## 💡 Astuces

### Filtrer efficacement
- Utilisez le filtre par segment pour cibler
- Cherchez par nom de rue
- Triez par priorité (automatique)

### Préparer vos messages
- Lisez le message "moyen" d'abord
- Adaptez selon la situation
- Personnalisez avec le prénom

### Optimiser vos tournées
- Groupez par quartier/rue
- Priorisez les foyers multi-personnes
- Visez les segments familles (36-50 ans)

## 🐛 Problèmes fréquents

### "npm not found"
➡️ Installez Node.js : https://nodejs.org

### "La carte ne s'affiche pas"
➡️ Attendez quelques secondes, vérifiez internet

### "Le CSV ne se charge pas"
➡️ Vérifiez que c'est bien `segmentation_electeurs_detaillee.csv`

### "Port 3000 already in use"
➡️ Fermez l'autre application ou utilisez : `npm run dev -- -p 3001`

## 📞 Support

Consultez les fichiers :
- `README.md` (racine) - Vue d'ensemble
- `tractage-app/README.md` - Documentation technique
- `tractage-app/DEPLOIEMENT.md` - Guide Vercel détaillé

---

**Bon tractage ! 🎯**

*Application créée pour optimiser la campagne électorale des Sables d'Olonne*

# 🗳️ Guide de déploiement Vercel

## Étape par étape

### 1. Créer un compte Vercel

Allez sur [vercel.com/signup](https://vercel.com/signup) et créez un compte avec :
- GitHub (recommandé)
- GitLab
- Bitbucket
- Email

### 2. Préparer le repository

Deux options :

#### Option A : Push vers GitHub (recommandé)

```bash
cd tractage-app

# Initialiser git si pas déjà fait
git init

# Ajouter tous les fichiers
git add .

# Commit
git commit -m "Initial commit - Application tractage electoral"

# Créer un repo sur GitHub puis :
git remote add origin https://github.com/VOTRE-USERNAME/tractage-electoral.git
git branch -M main
git push -u origin main
```

#### Option B : Déploiement direct sans GitHub

```bash
cd tractage-app
npm i -g vercel
vercel login
vercel
```

### 3. Déployer sur Vercel (via GitHub)

1. Connectez-vous sur [vercel.com](https://vercel.com)
2. Cliquez sur **"Add New..."** → **"Project"**
3. Sélectionnez votre repository GitHub
4. Vercel détecte automatiquement Next.js
5. Cliquez sur **"Deploy"**

⏱️ Le déploiement prend environ 2-3 minutes

### 4. Configuration (si nécessaire)

Vercel détecte automatiquement :
- ✅ Framework : Next.js
- ✅ Build Command : `npm run build`
- ✅ Output Directory : `.next`
- ✅ Install Command : `npm install`

### 5. Accéder à votre site

Après le déploiement, vous obtenez :
- 🌐 URL de production : `https://votre-projet.vercel.app`
- 🔄 URL de preview pour chaque PR
- 📊 Analytics automatiques

## 🚀 Déploiements automatiques

Chaque fois que vous pushez sur GitHub :
- `main` branch → Déploiement en production
- Autres branches → Déploiement de preview

## ⚙️ Configuration avancée

### Variables d'environnement

Dans Vercel Dashboard :
1. Allez dans **Settings** → **Environment Variables**
2. Ajoutez vos variables (si nécessaire)

### Custom Domain

1. **Settings** → **Domains**
2. Ajoutez votre domaine personnalisé
3. Suivez les instructions DNS

## 🔧 Commandes CLI utiles

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Déployer en preview
vercel

# Déployer en production
vercel --prod

# Voir les logs
vercel logs

# Lister les déploiements
vercel ls
```

## 📱 Tester avant le déploiement

```bash
# Build local
npm run build

# Tester le build
npm start

# Ouvrir http://localhost:3000
```

## 🐛 Troubleshooting

### Erreur de build

```bash
# Nettoyer et réinstaller
rm -rf node_modules .next
npm install
npm run build
```

### Problème de dépendances

Vérifiez `package.json` et assurez-vous que toutes les dépendances sont bien listées.

### Carte ne s'affiche pas

Vérifiez que `leaflet/dist/leaflet.css` est bien importé dans `globals.css`.

## 🎉 C'est prêt !

Votre application est maintenant en ligne et accessible depuis n'importe où.

Partagez l'URL avec votre équipe de campagne ! 🎯

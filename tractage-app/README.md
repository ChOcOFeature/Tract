# Tractage Electoral - Les Sables d'Olonne

Application web interactive pour optimiser le tractage électoral lors des élections municipales.

## 🎯 Fonctionnalités

- **📍 Carte interactive** : Visualisation géographique de tous les foyers avec code couleur par segment
- **🔍 Recherche avancée** : Filtrage par adresse, nom ou segment démographique
- **👥 Segmentation intelligente** : 7 profils d'électeurs avec messages personnalisés
- **💬 Messages adaptés** : 3 versions (court/moyen/long) pour chaque segment
- **📊 Statistiques en temps réel** : Nombre d'électeurs, âge moyen, priorités

## 🚀 Démarrage rapide

### Installation

```bash
cd tractage-app
npm install
```

### Développement local

```bash
npm run dev
```

Ouvrez [http://localhost:3000](http://localhost:3000) dans votre navigateur.

### Build de production

```bash
npm run build
npm start
```

## 📦 Déploiement sur Vercel

### Méthode 1 : Via l'interface Vercel (recommandé)

1. Créez un compte sur [vercel.com](https://vercel.com)
2. Cliquez sur "New Project"
3. Importez ce repository GitHub
4. Vercel détectera automatiquement Next.js
5. Cliquez sur "Deploy"

### Méthode 2 : Via CLI

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Déployer
vercel
```

### Méthode 3 : Via Git

Connectez simplement votre repository GitHub à Vercel. Chaque push sur `main` déclenchera un déploiement automatique.

## 📂 Structure du projet

```
tractage-app/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Layout principal
│   │   ├── page.tsx            # Page d'accueil avec logique
│   │   └── globals.css         # Styles globaux
│   ├── components/
│   │   └── Map.tsx             # Composant carte Leaflet
│   └── types/
│       └── index.ts            # Types TypeScript & segments
├── public/                     # Fichiers statiques
├── package.json
├── next.config.js
├── tailwind.config.js
└── README.md
```

## 📊 Utilisation

### 1. Charger les données

Cliquez sur "Charger les données CSV" et sélectionnez le fichier :
```
segmentation_electeurs_detaillee.csv
```

### 2. Explorer la carte

- **Points colorés** : Chaque foyer est représenté par un cercle coloré selon son segment
- **Taille** : Plus le cercle est grand, plus il y a d'électeurs
- **Clic** : Cliquez sur un point pour voir les détails

### 3. Rechercher et filtrer

- Utilisez la barre de recherche pour trouver une adresse ou un nom
- Filtrez par segment démographique
- La liste et la carte se synchronisent automatiquement

### 4. Voir les messages adaptés

- Sélectionnez un foyer
- Consultez les informations des électeurs
- Choisissez la longueur du message (court/moyen/long)
- Copiez le message dans votre presse-papier

## 🎨 Segments d'électeurs

| Segment | Emoji | Couleur | Thèmes |
|---------|-------|---------|--------|
| Jeunes (18-25) | 🎓 | Bleu | Avenir, Emploi, Logement |
| Jeunes actifs natifs | 🏡 | Vert clair | Développement local |
| Jeunes actifs nouveaux | 🤝 | Vert foncé | Accueil, Intégration |
| Familles actives | 👨‍👩‍👧‍👦 | Orange | École, Sécurité |
| Seniors actifs natifs | 🏛️ | Jaune | Patrimoine, Tradition |
| Seniors actifs non natifs | 🌊 | Violet | Qualité de vie |
| Retraités (66+) | 🏥 | Rouge | Santé, Proximité |

## 🛠️ Technologies utilisées

- **Next.js 14** : Framework React
- **TypeScript** : Typage statique
- **Tailwind CSS** : Styling moderne
- **Leaflet** : Cartes interactives
- **PapaParse** : Parsing CSV
- **Lucide React** : Icônes

## 🔧 Configuration avancée

### Variables d'environnement (optionnel)

Créez un fichier `.env.local` :

```env
NEXT_PUBLIC_MAP_CENTER_LAT=46.4959
NEXT_PUBLIC_MAP_CENTER_LON=-1.7842
```

### CSV chiffré + Vercel Blob

Le backend lit un fichier CSV chiffré stocké dans Vercel Blob, puis le déchiffre côté serveur.

1. Chiffrer localement le CSV

```bash
node scripts/encrypt-electeurs.mjs --in public/data/electeurs.csv --out public/data/electeurs.enc --passphrase "votre-passphrase"
```

2. Uploader le fichier chiffré dans Vercel Blob (via dashboard ou CLI) et récupérer l'URL du blob.

3. Configurer les variables d'environnement (ex: .env.local)

```env
ELECTEURS_BLOB_URL=https://.../electeurs.enc
BLOB_READ_WRITE_TOKEN=vercel_blob_token_...
ELECTEURS_PASSPHRASE=votre-passphrase
```

### Personnalisation des segments

Modifiez `src/types/index.ts` pour ajuster :
- Les messages par segment
- Les couleurs
- Les thèmes
- Les emojis

## 📱 Responsive

L'application est optimisée pour :
- 💻 Desktop (1920x1080+)
- 💻 Laptop (1366x768+)
- 📱 Tablette (768px+)

## 🆘 Support

Pour toute question ou problème :
1. Vérifiez que le CSV est bien formaté (séparateur `;`)
2. Vérifiez les colonnes requises : `Nom`, `Prénoms`, `Âge`, `Segment`, `Adresse Complète`
3. Consultez les logs dans la console du navigateur (F12)

## 📄 Licence

Ce projet est destiné à un usage spécifique pour la campagne électorale des Sables d'Olonne.

## 🎉 Conseils d'utilisation terrain

1. **Préparez vos données** : Exportez le CSV depuis l'analyse Python
2. **Planifiez vos tournées** : Filtrez par segment et bureau de vote
3. **Imprimez les messages** : Copiez-collez dans un document
4. **Synchronisez l'équipe** : Partagez le lien Vercel avec vos bénévoles
5. **Suivez l'avancement** : Marquez les adresses visitées

Bon tractage ! 🎯

# 📘 Feature FAQ - Documentation

## Vue d'ensemble

La feature FAQ a été mise en place pour permettre aux citoyens de trouver rapidement des réponses à leurs questions sur le programme politique.

## Structure

### Fichiers créés :

1. **`src/lib/faqData.ts`** - Base de données des questions/réponses
   - Contient toutes les FAQs avec leurs catégories
   - Structure: `FAQItem[]` avec id, categorie, question, reponse, segments

2. **`src/components/FAQ.tsx`** - Composants réutilisables
   - `<FAQ />` - Affiche une liste simple d'accoucher déplié/replié
   - `<FAQByCategory />` - Affiche les FAQs avec filtre par catégorie

3. **`src/app/api/faq/route.ts`** - Route API
   - Endpoint: `GET /api/faq`
   - Supporte les filtres: `categorie`, `segment`, `search`

4. **`src/app/faq/page.tsx`** - Page FAQ publique
   - URL: `https://yourapp.com/faq`
   - Page complète avec interface utilisateur

## Comment utiliser

### Afficher une FAQ simple
```tsx
import { FAQ } from '@/components/FAQ';
import { FAQ_DATA } from '@/lib/faqData';

export default function MyComponent() {
  return <FAQ items={FAQ_DATA} />;
}
```

### Afficher avec filtres par catégorie
```tsx
import { FAQByCategory } from '@/components/FAQ';
import { FAQ_DATA, CATEGORIES } from '@/lib/faqData';

export default function MyComponent() {
  return <FAQByCategory items={FAQ_DATA} categories={CATEGORIES} />;
}
```

### Utiliser l'API
```typescript
// Récupérer toutes les FAQs
const response = await fetch('/api/faq');
const data = await response.json();

// Filtrer par catégorie
const response = await fetch('/api/faq?categorie=Transports%20%26%20Mobilité');

// Filtrer par segment (ex: jeunes)
const response = await fetch('/api/faq?segment=jeunes');

// Recherche textuelle
const response = await fetch('/api/faq?search=logement');

// Combiner les filtres
const response = await fetch('/api/faq?categorie=Transports&segment=jeunes&search=gratuit');
```

## Comment ajouter de nouvelles FAQs

### 1. Ajouter dans `src/lib/faqData.ts`

```typescript
{
  id: 'mon-id-unique',
  categorie: 'Catégorie existante ou nouvelle',
  question: 'Ma question ?',
  reponse: 'Ma réponse basée sur le programme.',
  segments: ['jeunes', 'families'] // optionnel - si vide, c'est une FAQ générale
}
```

### Catégories disponibles :
- Transports & Mobilité
- Logement
- Enfance & Éducation
- Travail & Économie
- Santé
- Services Publics
- Environnement & Patrimoine
- Participation Citoyenne
- Vision Générale

### Segments disponibles :
- `jeunes` - Jeunes (18-25 ans)
- `jeunes-actifs-natifs` - Jeunes actifs natifs (26-35 ans)
- `jeunes-actifs-nouveaux` - Jeunes actifs nouveaux arrivants (26-35 ans)
- `familles` - Familles actives (36-50 ans)
- `seniors-actifs-natifs` - Seniors actifs natifs (51-65 ans)
- `seniors-actifs-non-natifs` - Seniors actifs non natifs (51-65 ans)
- `retraites` - Retraités (66+ ans)

### 2. Ajouter une nouvelle catégorie (si nécessaire)

```typescript
export const CATEGORIES = [
  'Transports & Mobilité',
  'Logement',
  // ... autres catégories
  'Ma Nouvelle Catégorie',
];
```

## Intégration dans d'autres pages

### Ajouter un bouton pour accéder à la FAQ
```tsx
<a href="/faq" className="...">
  📘 FAQ
</a>
```

Déjà intégré dans le header principal de l'app !

## Fonctionnalités

✅ Listes de questions/réponses dépliables
✅ Filtrage par catégorie
✅ Filtrage par segment (CitoyensSatisfied)
✅ Recherche textuelle via API
✅ Design responsive (mobile-friendly)
✅ API REST pour l'intégration externe

## SEO et Métadonnées

La page FAQ inclut des métadonnées pour le SEO :
```tsx
export const metadata = {
  title: 'Foire Aux Questions - Notre programme',
  description: 'Trouvez les réponses à vos questions sur notre programme politique pour Les Sables d\'Olonne',
};
```

## Exemples d'utilisation avancée

### Afficher FAQ pour un segment spécifique
```typescript
const userSegment = 'jeunes';
const userFAQs = FAQ_DATA.filter(item => 
  !item.segments || item.segments.length === 0 || item.segments.includes(userSegment)
);
```

### Exporter les FAQs en JSON
```typescript
// Via l'API
fetch('/api/faq').then(r => r.json()).then(data => {
  console.log(JSON.stringify(data, null, 2));
});
```

## Prochaines étapes (à considérer)

- [ ] Ajouter la recherche en temps réel côté client
- [ ] Analytics pour suivre les questions les plus visitées
- [ ] Système de feedback (utile/non utile)
- [ ] Intégration avec un formulaire de contact pour les questions sans réponse
- [ ] Versions PDF téléchargeables pour matériaux de campagne
- [ ] Versions dans d'autres langues

## Questions ?

Consultez la page FAQ à `/faq` pour voir la feature en action !

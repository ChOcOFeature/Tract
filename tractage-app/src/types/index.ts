export interface Electeur {
  nom: string;
  prenoms: string;
  age: number;
  sexe: 'M' | 'F';
  segment: string;
  natifVendee: boolean;
  adresse: string;
  rue: string;
  numeroVoie: string;
  codePostal: string;
  commune: string;
  codeBureau: string;
  libelleBureau: string;
  lat?: number;
  lon?: number;
}

export interface Foyer {
  adresse: string;
  adresseGoogleMaps: string;
  nbElecteurs: number;
  ageMoyen: number;
  segmentDominant: string;
  electeurs: Electeur[];
  scorePriorite: number;
  couleur: string;
  lat?: number;
  lon?: number;
}

export interface MessageTemplate {
  segment: string;
  titre: string;
  emoji: string;
  themes: string[];
  messages: {
    court: string;
    moyen: string;
    long: string;
  };
  couleur: string;
}

export const SEGMENTS: Record<string, MessageTemplate> = {
  'jeunes': {
    segment: '1. Jeunes (18-25 ans)',
    titre: 'Jeunes électeurs',
    emoji: '🎓',
    themes: ['Etudes', 'Mobilite', 'Logement', 'Culture'],
    couleur: '#3b82f6',
    messages: {
      court: "Transports gratuits, pistes cyclables protegees, logement plus accessible : votre voix peut changer le quotidien.",
      moyen: "Pour les 18-25 ans, on agit sur le concret : transports publics gratuits pour les residents, reseau cyclable plus sur et plus large, logements plus accessibles et vie culturelle renforcee. Votre place en ville compte.",
      long: "Etudiants, jeunes actifs, jeunes en insertion : notre programme met la mobilite et l'emancipation au centre. Transports gratuits toute l'annee pour les residents, pistes cyclables protegees, soutien au logement (bail reel solidaire, renovation des passoires thermiques), plus d'espaces culturels et associatifs. Et une democratie locale qui vous donne vraiment la parole."
    }
  },
  'jeunes-actifs-natifs': {
    segment: '2A. Jeunes actifs natifs (26-35 ans)',
    titre: 'Jeunes actifs locaux',
    emoji: '🏡',
    themes: ['Emploi local', 'Logement', 'Transports', 'Qualite de vie'],
    couleur: '#10b981',
    messages: {
      court: "Emplois locaux, mobilite gratuite, logements accessibles : on cree des conditions pour rester et s'installer durablement.",
      moyen: "Natifs d'ici, vous connaissez les besoins reels. Notre programme : soutien aux emplois locaux et aux filieres ecologiques, transports gratuits pour residents, stationnement mieux pense, logements accessibles et renovation energetique. Une ville qui facilite la vie des actifs.",
      long: "Pour les jeunes actifs locaux, on mise sur l'economie utile et l'equilibre vie pro/vie perso : aides aux filieres regeneratives, clauses sociales et environnementales dans les marches publics, transports gratuits, reseau cyclable securise, logements accessibles (bail reel solidaire) et lutte contre les locations touristiques abusives. On renforce aussi la participation citoyenne dans les projets d'amenagement."
    }
  },
  'jeunes-actifs-nouveaux': {
    segment: '2B. Jeunes actifs nouveaux arrivants (26-35 ans)',
    titre: 'Nouveaux arrivants actifs',
    emoji: '🤝',
    themes: ['Accueil', 'Services publics', 'Mobilite', 'Logement'],
    couleur: '#059669',
    messages: {
      court: "Bienvenue ! Services publics accessibles, mobilite gratuite et logement abordable pour bien s'installer.",
      moyen: "Vous arrivez aux Sables d'Olonne ? On facilite l'installation : services municipaux d'accueil, transports gratuits pour residents, pistes cyclables securisees, logement accessible et encadrement des locations touristiques. Vous etes chez vous ici.",
      long: "Nouveaux arrivants, notre programme rend la ville plus simple au quotidien : accueil municipal renforce, services publics de proximite, transports gratuits, reseau cyclable protege, logements accessibles et lutte contre les passoires thermiques. Nous associons aussi les habitants aux grands projets, pour une integration reelle et durable."
    }
  },
  'familles': {
    segment: '3. Familles actives (36-50 ans)',
    titre: 'Familles',
    emoji: '👨‍👩‍👧‍👦',
    themes: ['Ecoles', 'Petite enfance', 'Transports', 'Cadre de vie'],
    couleur: '#f59e0b',
    messages: {
      court: "Creches, ecoles, cantines equitables, transports gratuits : une ville qui soutient vraiment les familles.",
      moyen: "Pour les familles, on agit sur les besoins concrets : creches municipales, cantines et centres de loisirs adaptes aux revenus, renovation des ecoles, transports publics gratuits pour residents et pistes cyclables securisees. Un cadre de vie plus simple et plus sain.",
      long: "Familles actives, notre programme met l'enfance au coeur : creation de creches municipales, service d'assistantes maternelles, renovation des batiments scolaires, cantines plus bio et locales avec tarifs adaptes, activites sportives accessibles, mobilites douces et transports gratuits pour residents. On renforce aussi les espaces verts et la qualite environnementale."
    }
  },
  'seniors-actifs-natifs': {
    segment: '4A. Seniors actifs natifs (51-65 ans)',
    titre: 'Seniors actifs locaux',
    emoji: '🏛️',
    themes: ['Patrimoine', 'Services publics', 'Sante', 'Cadre de vie'],
    couleur: '#eab308',
    messages: {
      court: "Patrimoine protege, services publics renforces, sante de proximite : respectons ce que vous avez construit.",
      moyen: "Seniors actifs locaux, notre programme renforce les services publics de proximite, defend la presence des postes et du centre des impots, soutient une offre de sante municipale et protege le patrimoine. La qualite de vie reste notre boussole.",
      long: "Sablais de toujours, vous avez bati la ville. Nous voulons maintenir les services publics (poste, impots), renforcer la sante municipale, proteger le patrimoine maritime, et developper un urbanisme plus humain. La transition ecologique et la participation citoyenne sont au service de la qualite de vie."
    }
  },
  'seniors-actifs-non-natifs': {
    segment: '4B. Seniors actifs non natifs (51-65 ans)',
    titre: 'Seniors actifs installés',
    emoji: '🌊',
    themes: ['Qualite de vie', 'Sante', 'Mobilite', 'Culture'],
    couleur: '#8b5cf6',
    messages: {
      court: "Sante, culture, mobilite douce : on renforce la qualite de vie que vous avez choisie.",
      moyen: "Vous avez choisi Les Sables d'Olonne pour son cadre de vie. Nous renforcons la sante de proximite, les mobilites douces, la vie culturelle et la protection des espaces naturels. Une ville vivante toute l'annee.",
      long: "Seniors actifs installes, notre programme vise une qualite de vie durable : centres municipaux de sante, transports publics gratuits pour residents, pistes cyclables securisees, offre culturelle renforcee et protection du littoral et des marais. Plus de services, moins de contraintes au quotidien."
    }
  },
  'retraites': {
    segment: '5. Retraités (66+ ans)',
    titre: 'Retraités',
    emoji: '🏥',
    themes: ['Sante', 'Proximite', 'Solidarites', 'Services publics'],
    couleur: '#ef4444',
    messages: {
      court: "Centres municipaux de sante, services publics proches, solidarites renforcees : une retraite sereine.",
      moyen: "Nous voulons une ville qui prend soin de ses aines : deux centres municipaux de sante, renforcement du CCAS, services publics de proximite, accueil municipal pour l'accompagnement numerique. Une retraite paisible et active.",
      long: "Chers retraites, notre programme renforce la sante et la solidarite : deux centres municipaux de sante, cooperation avec l'hopital, unite de soins palliatifs, maintien des services publics, renforcement du CCAS, lieux d'accueil intergenerationnels et activites accessibles. La ville doit proteger celles et ceux qui l'ont faite."
    }
  }
};

export const getSegmentKey = (segment: string): string => {
  if (segment.includes('Jeunes (18-25')) return 'jeunes';
  if (segment.includes('Jeunes actifs natifs')) return 'jeunes-actifs-natifs';
  if (segment.includes('Jeunes actifs nouveaux')) return 'jeunes-actifs-nouveaux';
  if (segment.includes('Familles actives')) return 'familles';
  if (segment.includes('Seniors actifs natifs')) return 'seniors-actifs-natifs';
  if (segment.includes('Seniors actifs non natifs')) return 'seniors-actifs-non-natifs';
  if (segment.includes('Retraités')) return 'retraites';
  return 'familles';
};

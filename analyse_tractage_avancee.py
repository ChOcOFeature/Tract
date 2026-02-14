#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'analyse avancée pour tractage électoral - Les Sables d'Olonne
Objectif: Optimiser la stratégie de tractage et la cartographie
"""

import pandas as pd
from datetime import datetime
import os

# Configuration
CSV_FILE = "ListesElecteursActifs-com85194-13-02-2026-08h44.csv"
DATE_REFERENCE = datetime(2026, 2, 14)


def charger_donnees(fichier):
    """Charge le fichier CSV des électeurs"""
    print(f"Chargement du fichier: {fichier}")
    df = pd.read_csv(fichier, sep=';', encoding='utf-8')
    
    # Nettoyer et enrichir les données
    df['age'] = df['date de naissance'].apply(lambda x: calculer_age(x, DATE_REFERENCE))
    df['natif_vendee'] = df['code département de naissance'].astype(str).str.strip() == '85'
    df['adresse_complete'] = df.apply(nettoyer_adresse, axis=1)
    
    print(f"✓ {len(df)} électeurs chargés et préparés\n")
    return df


def nettoyer_adresse(row):
    """Construit une adresse complète unique"""
    elements = []
    if pd.notna(row['numéro de voie']):
        elements.append(str(row['numéro de voie']))
    if pd.notna(row['libellé de voie']):
        elements.append(row['libellé de voie'])
    if pd.notna(row['complément 1']):
        elements.append(row['complément 1'])
    if pd.notna(row['complément 2']):
        elements.append(row['complément 2'])
    if pd.notna(row['lieu-dit']):
        elements.append(row['lieu-dit'])
    if pd.notna(row['code postal']):
        elements.append(str(row['code postal']))
    return ' '.join(elements).strip().upper()


def nettoyer_rue(row):
    """Extrait uniquement le nom de la rue (sans numéro ni complément)"""
    elements = []
    if pd.notna(row['libellé de voie']):
        elements.append(row['libellé de voie'])
    if pd.notna(row['lieu-dit']):
        elements.append(f"[{row['lieu-dit']}]")
    if pd.notna(row['code postal']):
        elements.append(f"({row['code postal']})")
    return ' '.join(elements).strip().upper()


def calculer_age(date_naissance_str, date_ref):
    """Calcule l'âge à partir d'une date de naissance"""
    try:
        date_naissance = datetime.strptime(date_naissance_str, '%d/%m/%Y')
        age = date_ref.year - date_naissance.year
        if (date_ref.month, date_ref.day) < (date_naissance.month, date_naissance.day):
            age -= 1
        return age
    except:
        return None


def analyser_rues_prioritaires(df):
    """
    ANALYSE 1: Top des rues à tracter en priorité
    """
    print("="*80)
    print("ANALYSE 1: TOP DES RUES À TRACTER EN PRIORITÉ")
    print("="*80)
    
    # Créer une colonne pour identifier les rues
    df['rue_simple'] = df.apply(nettoyer_rue, axis=1)
    
    # Grouper par rue
    stats_rues = df.groupby(['rue_simple', 'code du bureau de vote', 
                             'libellé du bureau de vote']).agg({
        'age': ['count', 'mean'],
        'natif_vendee': 'sum',
        'sexe': lambda x: (x == 'M').sum() / len(x) * 100,  # % hommes
        'adresse_complete': 'nunique'  # nombre de foyers
    }).reset_index()
    
    stats_rues.columns = ['rue', 'code_bureau', 'libelle_bureau', 
                          'nb_electeurs', 'age_moyen', 'nb_natifs', 
                          'pct_hommes', 'nb_foyers']
    
    # Calculer des métriques de priorisation
    stats_rues['pct_natifs'] = (stats_rues['nb_natifs'] / stats_rues['nb_electeurs'] * 100)
    stats_rues['electeurs_par_foyer'] = stats_rues['nb_electeurs'] / stats_rues['nb_foyers']
    
    # Score de priorité (densité + familles + jeunes)
    stats_rues['score_densite'] = stats_rues['nb_electeurs'] / 10  # Max 10 points
    stats_rues['score_familles'] = (stats_rues['electeurs_par_foyer'] - 1) * 20  # Max 20 points
    stats_rues['score_age'] = 100 - abs(stats_rues['age_moyen'] - 45)  # Optimal 45 ans
    
    stats_rues['score_priorite'] = (
        stats_rues['score_densite'].clip(0, 10) * 0.4 +
        stats_rues['score_familles'].clip(0, 20) * 0.3 +
        stats_rues['score_age'].clip(0, 100) * 0.3
    )
    
    # Filtrer les rues avec au moins 10 électeurs
    stats_rues = stats_rues[stats_rues['nb_electeurs'] >= 10]
    stats_rues = stats_rues.sort_values('score_priorite', ascending=False)
    
    print(f"\n📊 STATISTIQUES GLOBALES:")
    print(f"   Nombre de rues analysées: {len(stats_rues)}")
    print(f"   Total électeurs: {stats_rues['nb_electeurs'].sum()}")
    
    print(f"\n🎯 TOP 30 DES RUES PRIORITAIRES:")
    print("-" * 80)
    
    for idx, row in stats_rues.head(30).iterrows():
        print(f"\n{list(stats_rues.head(30).index).index(idx) + 1}. {row['rue'][:60]}")
        print(f"   Bureau: {row['code_bureau']} - {row['libelle_bureau'][:45]}")
        print(f"   🎯 Score priorité: {row['score_priorite']:.1f}/100")
        print(f"   👥 {row['nb_electeurs']:.0f} électeurs | {row['nb_foyers']:.0f} foyers | {row['electeurs_par_foyer']:.1f} élec/foyer")
        print(f"   📅 Âge moyen: {row['age_moyen']:.1f} ans | Natifs: {row['pct_natifs']:.1f}%")
    
    # Export détaillé
    export_rues = stats_rues[[
        'rue', 'code_bureau', 'libelle_bureau', 'score_priorite',
        'nb_electeurs', 'nb_foyers', 'electeurs_par_foyer',
        'age_moyen', 'pct_natifs', 'pct_hommes'
    ]].copy()
    
    export_rues.columns = [
        'Rue', 'Code Bureau', 'Bureau de Vote', 'Score Priorité',
        'Nb Électeurs', 'Nb Foyers', 'Électeurs/Foyer',
        'Âge Moyen', '% Natifs Vendée', '% Hommes'
    ]
    
    export_rues.to_csv('top_rues_prioritaires.csv', index=False, 
                       encoding='utf-8-sig', sep=';')
    print(f"\n✓ Export détaillé: top_rues_prioritaires.csv ({len(export_rues)} rues)")
    
    return stats_rues


def segmentation_electeurs(df):
    """
    ANALYSE 2: Segmentation détaillée par profils d'électeurs
    """
    print("\n" + "="*80)
    print("ANALYSE 2: SEGMENTATION DÉTAILLÉE PAR PROFILS")
    print("="*80)
    
    # Définir les segments
    def definir_segment(row):
        age = row['age']
        if pd.isna(age):
            return 'Indéterminé'
        
        if 18 <= age <= 25:
            return '1. Jeunes (18-25 ans)'
        elif 26 <= age <= 35:
            if row['natif_vendee']:
                return '2A. Jeunes actifs natifs (26-35 ans)'
            else:
                return '2B. Jeunes actifs nouveaux arrivants (26-35 ans)'
        elif 36 <= age <= 50:
            return '3. Familles actives (36-50 ans)'
        elif 51 <= age <= 65:
            if row['natif_vendee']:
                return '4A. Seniors actifs natifs (51-65 ans)'
            else:
                return '4B. Seniors actifs non natifs (51-65 ans)'
        else:  # 66+
            return '5. Retraités (66+ ans)'
    
    df['segment'] = df.apply(definir_segment, axis=1)
    
    # Analyser les foyers par segment
    foyers_df = df.groupby('adresse_complete').agg({
        'segment': lambda x: x.value_counts().index[0],  # Segment dominant
        'age': 'mean',
        'sexe': lambda x: len(set(x)) > 1,  # Foyer mixte
        'nom de naissance': 'count'
    }).reset_index()
    foyers_df.columns = ['adresse', 'segment', 'age_moyen', 'foyer_mixte', 'nb_personnes']
    
    # Statistiques par segment
    print(f"\n📊 RÉPARTITION DES ÉLECTEURS PAR SEGMENT:")
    print("-" * 80)
    
    segments_stats = df.groupby('segment').agg({
        'age': ['count', 'mean'],
        'natif_vendee': lambda x: (x.sum() / len(x) * 100),
        'sexe': lambda x: (x == 'F').sum() / len(x) * 100,
        'code du bureau de vote': lambda x: x.value_counts().index[0]
    }).reset_index()
    
    segments_stats.columns = ['segment', 'nb_electeurs', 'age_moyen', 
                              'pct_natifs', 'pct_femmes', 'bureau_principal']
    segments_stats = segments_stats.sort_values('segment')
    
    total = segments_stats['nb_electeurs'].sum()
    
    for _, row in segments_stats.iterrows():
        pct = row['nb_electeurs'] / total * 100
        print(f"\n{row['segment']}")
        print(f"   Électeurs: {row['nb_electeurs']:.0f} ({pct:.1f}%)")
        print(f"   Âge moyen: {row['age_moyen']:.1f} ans")
        print(f"   Natifs Vendée: {row['pct_natifs']:.1f}%")
        print(f"   Femmes: {row['pct_femmes']:.1f}%")
    
    # Analyse par segment et bureau
    print(f"\n🗳️  SEGMENTS PAR BUREAU DE VOTE (Top 5 par segment):")
    print("-" * 80)
    
    segments_bureaux = df.groupby(['segment', 'code du bureau de vote', 
                                   'libellé du bureau de vote']).size().reset_index(name='nb_electeurs')
    
    messages_segments = {
        '1. Jeunes (18-25 ans)': 
            '🎓 Message: Avenir, emploi, logement, numérique',
        '2A. Jeunes actifs natifs (26-35 ans)': 
            '🏡 Message: Développement local, emploi qualifié, vie culturelle',
        '2B. Jeunes actifs nouveaux arrivants (26-35 ans)': 
            '🤝 Message: Accueil, intégration, services, découverte',
        '3. Familles actives (36-50 ans)': 
            '👨‍👩‍👧‍👦 Message: École, sécurité, activités enfants, cadre de vie',
        '4A. Seniors actifs natifs (51-65 ans)': 
            '🏛️ Message: Patrimoine, tradition, qualité de vie, santé',
        '4B. Seniors actifs non natifs (51-65 ans)': 
            '🌊 Message: Qualité de vie, services, culture, mobilité',
        '5. Retraités (66+ ans)': 
            '🏥 Message: Santé, services de proximité, sécurité, vie sociale'
    }
    
    for segment in sorted(df['segment'].unique()):
        if segment == 'Indéterminé':
            continue
        print(f"\n{messages_segments.get(segment, segment)}")
        top_bureaux = segments_bureaux[segments_bureaux['segment'] == segment].nlargest(5, 'nb_electeurs')
        for _, row in top_bureaux.iterrows():
            print(f"   • Bureau {row['code du bureau de vote']}: {row['nb_electeurs']} électeurs")
    
    # Export segments détaillés avec adresses
    df_export_segments = df[[
        'segment', 'nom de naissance', 'prénoms', 'age', 'sexe',
        'natif_vendee', 'adresse_complete', 
        'code du bureau de vote', 'libellé du bureau de vote'
    ]].copy()
    
    df_export_segments.columns = [
        'Segment', 'Nom', 'Prénoms', 'Âge', 'Sexe',
        'Natif Vendée', 'Adresse Complète',
        'Code Bureau', 'Bureau de Vote'
    ]
    
    df_export_segments = df_export_segments.sort_values(['Segment', 'Bureau de Vote', 'Adresse Complète'])
    df_export_segments.to_csv('segmentation_electeurs_detaillee.csv', 
                              index=False, encoding='utf-8-sig', sep=';')
    print(f"\n✓ Export détaillé: segmentation_electeurs_detaillee.csv")
    
    # Export résumé par segment et bureau
    segments_bureaux_pivot = segments_bureaux.pivot_table(
        index=['code du bureau de vote', 'libellé du bureau de vote'],
        columns='segment',
        values='nb_electeurs',
        fill_value=0
    ).reset_index()
    
    segments_bureaux_pivot.to_csv('segments_par_bureau.csv', 
                                  index=False, encoding='utf-8-sig', sep=';')
    print(f"✓ Export résumé: segments_par_bureau.csv")
    
    return df, segments_stats


def export_cartographie(df, stats_rues):
    """
    ANALYSE 3: Export pour cartographie (Google Maps / Excel)
    """
    print("\n" + "="*80)
    print("ANALYSE 3: EXPORT POUR CARTOGRAPHIE")
    print("="*80)
    
    # 1. Export par adresse complète pour Google Maps
    print(f"\n📍 Préparation des données géographiques...")
    
    adresses_carto = df.groupby('adresse_complete').agg({
        'nom de naissance': lambda x: ', '.join(list(x)[:3]) + ('...' if len(x) > 3 else ''),
        'age': ['count', 'mean'],
        'segment': lambda x: x.value_counts().index[0],
        'natif_vendee': 'sum',
        'code du bureau de vote': 'first',
        'libellé du bureau de vote': 'first',
        'numéro de voie': 'first',
        'libellé de voie': 'first',
        'code postal': 'first',
        'commune': 'first'
    }).reset_index()
    
    adresses_carto.columns = [
        'Adresse Complète', 'Noms (aperçu)', 'Nb Électeurs', 'Âge Moyen',
        'Segment Dominant', 'Nb Natifs Vendée', 'Code Bureau', 'Bureau de Vote',
        'Numéro', 'Rue', 'Code Postal', 'Commune'
    ]
    
    # Construire l'adresse formatée pour Google Maps
    adresses_carto['Adresse Google Maps'] = (
        adresses_carto['Numéro'].fillna('').astype(str) + ' ' +
        adresses_carto['Rue'].fillna('') + ', ' +
        adresses_carto['Code Postal'].fillna('').astype(str) + ' ' +
        adresses_carto['Commune'].fillna('')
    ).str.strip()
    
    # Couleur par segment (pour visualisation)
    couleurs_segments = {
        '1. Jeunes (18-25 ans)': 'Bleu',
        '2A. Jeunes actifs natifs (26-35 ans)': 'Vert clair',
        '2B. Jeunes actifs nouveaux arrivants (26-35 ans)': 'Vert foncé',
        '3. Familles actives (36-50 ans)': 'Orange',
        '4A. Seniors actifs natifs (51-65 ans)': 'Jaune',
        '4B. Seniors actifs non natifs (51-65 ans)': 'Violet',
        '5. Retraités (66+ ans)': 'Rouge',
        'Indéterminé': 'Gris'
    }
    
    adresses_carto['Couleur Suggérée'] = adresses_carto['Segment Dominant'].map(couleurs_segments)
    
    # Taille du marqueur (proportionnelle au nombre d'électeurs)
    adresses_carto['Taille Marqueur'] = adresses_carto['Nb Électeurs'].apply(
        lambda x: 'Petit' if x == 1 else 'Moyen' if x <= 3 else 'Grand'
    )
    
    # Score de priorité pour tri
    adresses_carto['Score Priorité'] = (
        adresses_carto['Nb Électeurs'] * 20 +  # Plus d'électeurs = plus prioritaire
        (50 - abs(adresses_carto['Âge Moyen'] - 45)) * 2  # Âge familles optimal
    )
    
    adresses_carto = adresses_carto.sort_values('Score Priorité', ascending=False)
    
    # Export données cartographiques
    export_carto = adresses_carto[[
        'Adresse Google Maps', 'Adresse Complète', 'Nb Électeurs', 
        'Âge Moyen', 'Segment Dominant', 'Couleur Suggérée', 'Taille Marqueur',
        'Score Priorité', 'Bureau de Vote', 'Code Bureau', 'Noms (aperçu)'
    ]].copy()
    
    export_carto['Âge Moyen'] = export_carto['Âge Moyen'].round(1)
    export_carto['Score Priorité'] = export_carto['Score Priorité'].round(0)
    
    export_carto.to_csv('cartographie_google_maps.csv', 
                       index=False, encoding='utf-8-sig', sep=';')
    
    print(f"✓ Export cartographie: cartographie_google_maps.csv ({len(export_carto)} adresses)")
    
    # 2. Export simplifié par rue pour planning de tractage
    rues_tractage = stats_rues.head(100)[['rue', 'code_bureau', 'libelle_bureau', 
                                          'nb_electeurs', 'nb_foyers', 'score_priorite']].copy()
    
    # Estimer le temps de tractage (1 minute par foyer)
    rues_tractage['Temps Estimé (min)'] = rues_tractage['nb_foyers']
    rues_tractage['Temps Estimé (texte)'] = rues_tractage['Temps Estimé (min)'].apply(
        lambda x: f"{int(x)} min" if x < 60 else f"{int(x/60)}h{int(x%60):02d}"
    )
    
    rues_tractage.columns = [
        'Rue', 'Code Bureau', 'Bureau de Vote', 'Nb Électeurs', 'Nb Foyers',
        'Score Priorité', 'Temps Estimé (min)', 'Temps Estimé'
    ]
    
    rues_tractage['Équipe Suggérée'] = rues_tractage['Temps Estimé (min)'].apply(
        lambda x: '1 personne' if x <= 30 else '2 personnes' if x <= 90 else '3+ personnes'
    )
    
    rues_tractage.to_csv('planning_tractage_par_rue.csv', 
                        index=False, encoding='utf-8-sig', sep=';')
    
    print(f"✓ Planning tractage: planning_tractage_par_rue.csv (Top 100 rues)")
    
    # 3. Export KML pour Google Earth (format simple)
    print(f"\n🗺️  Génération du fichier KML pour Google Earth...")
    
    kml_content = generate_kml(export_carto.head(500))  # Limiter à 500 points
    
    with open('cartographie_tractage.kml', 'w', encoding='utf-8') as f:
        f.write(kml_content)
    
    print(f"✓ Fichier KML: cartographie_tractage.kml (Top 500 adresses)")
    
    # 4. Statistiques de cartographie
    print(f"\n📊 STATISTIQUES CARTOGRAPHIE:")
    print("-" * 80)
    print(f"   Total adresses: {len(adresses_carto)}")
    print(f"   Adresses 1 personne: {len(adresses_carto[adresses_carto['Nb Électeurs'] == 1])}")
    print(f"   Adresses 2+ personnes (familles): {len(adresses_carto[adresses_carto['Nb Électeurs'] >= 2])}")
    print(f"   Temps total estimé: {rues_tractage['Temps Estimé (min)'].sum():.0f} min ({rues_tractage['Temps Estimé (min)'].sum()/60:.1f}h)")
    
    print(f"\n💡 INSTRUCTIONS D'UTILISATION:")
    print("-" * 80)
    print("   1. Google Maps:")
    print("      - Ouvrir Google My Maps (https://www.google.com/mymaps)")
    print("      - Créer une nouvelle carte")
    print("      - Importer 'cartographie_google_maps.csv'")
    print("      - Utiliser 'Adresse Google Maps' comme adresse")
    print("      - Styliser par 'Segment Dominant' ou 'Couleur Suggérée'")
    print("")
    print("   2. Google Earth:")
    print("      - Ouvrir Google Earth")
    print("      - Fichier > Ouvrir > Sélectionner 'cartographie_tractage.kml'")
    print("")
    print("   3. Excel:")
    print("      - Ouvrir les fichiers CSV avec Excel")
    print("      - Utiliser les filtres et tris pour planifier")
    
    return export_carto


def generate_kml(adresses_df):
    """Génère un fichier KML pour Google Earth"""
    kml_header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.org/kml/2.2">
  <Document>
    <name>Tractage Électoral - Les Sables d'Olonne</name>
    <description>Carte des adresses prioritaires pour le tractage</description>
    
    <!-- Styles -->
    <Style id="famille">
      <IconStyle>
        <color>ff0000ff</color>
        <scale>1.2</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/red-circle.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="standard">
      <IconStyle>
        <color>ff00ff00</color>
        <scale>0.8</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href>
        </Icon>
      </IconStyle>
    </Style>
"""
    
    kml_footer = """  </Document>
</kml>"""
    
    placemarks = []
    for _, row in adresses_df.iterrows():
        style = 'famille' if row['Nb Électeurs'] >= 2 else 'standard'
        placemark = f"""    <Placemark>
      <name>{row['Nb Électeurs']} électeur(s)</name>
      <description>
        Adresse: {row['Adresse Complète']}
        Segment: {row['Segment Dominant']}
        Âge moyen: {row['Âge Moyen']:.0f} ans
        Bureau: {row['Bureau de Vote']}
        Noms: {row['Noms (aperçu)']}
      </description>
      <styleUrl>#{style}</styleUrl>
      <address>{row['Adresse Google Maps']}</address>
    </Placemark>
"""
        placemarks.append(placemark)
    
    return kml_header + '\n'.join(placemarks) + kml_footer


def main():
    """Fonction principale"""
    print("\n" + "="*80)
    print("ANALYSE AVANCÉE POUR TRACTAGE ÉLECTORAL")
    print("Les Sables d'Olonne - Élections Municipales")
    print("="*80)
    
    if not os.path.exists(CSV_FILE):
        print(f"❌ Erreur: Le fichier '{CSV_FILE}' n'existe pas")
        return
    
    # Charger les données
    df = charger_donnees(CSV_FILE)
    
    # Exécuter les 3 analyses
    stats_rues = analyser_rues_prioritaires(df)
    df_enrichi, segments_stats = segmentation_electeurs(df)
    export_carto = export_cartographie(df_enrichi, stats_rues)
    
    print("\n" + "="*80)
    print("✅ ANALYSE TERMINÉE")
    print("="*80)
    print("\n📁 FICHIERS GÉNÉRÉS:")
    print("   1. top_rues_prioritaires.csv - Top des rues à tracter")
    print("   2. segmentation_electeurs_detaillee.csv - Détail par segment")
    print("   3. segments_par_bureau.csv - Résumé segments/bureaux")
    print("   4. cartographie_google_maps.csv - Import Google Maps")
    print("   5. planning_tractage_par_rue.csv - Planning avec temps estimés")
    print("   6. cartographie_tractage.kml - Import Google Earth")
    print("\n")


if __name__ == "__main__":
    main()

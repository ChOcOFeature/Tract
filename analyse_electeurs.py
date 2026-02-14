#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'analyse des listes électorales - Les Sables d'Olonne
Objectif: Cibler les tractages vers les familles et quartiers pertinents
"""

import pandas as pd
from datetime import datetime
import os

# Configuration
CSV_FILE = "ListesElecteursActifs-com85194-13-02-2026-08h44.csv"
DATE_REFERENCE = datetime(2026, 2, 14)  # Date actuelle


def charger_donnees(fichier):
    """Charge le fichier CSV des électeurs"""
    print(f"Chargement du fichier: {fichier}")
    df = pd.read_csv(fichier, sep=';', encoding='utf-8')
    print(f"✓ {len(df)} électeurs chargés\n")
    return df


def nettoyer_adresse(row):
    """Construit une adresse complète unique pour identifier les foyers"""
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


def analyser_foyers(df):
    """
    USE CASE 1: Nombre de foyers par bureau de vote
    Regroupe les électeurs par adresse (foyers/familles)
    """
    print("="*70)
    print("USE CASE 1: ANALYSE DES FOYERS")
    print("="*70)
    
    # Créer une colonne adresse complète
    df['adresse_complete'] = df.apply(nettoyer_adresse, axis=1)
    
    # Grouper par adresse et bureau de vote
    foyers = df.groupby(['adresse_complete', 'code du bureau de vote', 
                         'libellé du bureau de vote']).agg({
        'nom de naissance': list,
        'prénoms': list,
        'sexe': list
    }).reset_index()
    
    # Calculer le nombre de personnes par foyer
    foyers['nb_personnes'] = foyers['nom de naissance'].apply(len)
    
    # Statistiques globales
    print(f"\n📊 STATISTIQUES GLOBALES:")
    print(f"   Nombre total d'électeurs: {len(df)}")
    print(f"   Nombre total de foyers: {len(foyers)}")
    print(f"   Moyenne de personnes par foyer: {foyers['nb_personnes'].mean():.2f}")
    
    # Distribution des foyers
    print(f"\n📈 DISTRIBUTION DES FOYERS:")
    distrib = foyers['nb_personnes'].value_counts().sort_index()
    for nb_pers, count in distrib.items():
        pct = (count / len(foyers)) * 100
        print(f"   {nb_pers} personne(s): {count} foyers ({pct:.1f}%)")
    
    # Foyers avec 2+ personnes (familles/couples)
    foyers_familles = foyers[foyers['nb_personnes'] >= 2]
    print(f"\n👨‍👩‍👧‍👦 FOYERS MULTI-PERSONNES (2+):")
    print(f"   Nombre: {len(foyers_familles)}")
    print(f"   Pourcentage: {(len(foyers_familles)/len(foyers)*100):.1f}%")
    
    # Statistiques par bureau de vote
    print(f"\n🗳️  RÉPARTITION PAR BUREAU DE VOTE:")
    print("-" * 70)
    
    stats_bureaux = foyers.groupby(['code du bureau de vote', 
                                    'libellé du bureau de vote']).agg({
        'adresse_complete': 'count',
        'nb_personnes': 'sum'
    }).reset_index()
    
    stats_bureaux.columns = ['code', 'libelle', 'nb_foyers', 'nb_electeurs']
    stats_bureaux = stats_bureaux.sort_values('nb_foyers', ascending=False)
    
    for _, row in stats_bureaux.iterrows():
        print(f"\n   Bureau {row['code']} - {row['libelle']}")
        print(f"      Foyers: {row['nb_foyers']}")
        print(f"      Électeurs: {row['nb_electeurs']}")
        print(f"      Moyenne: {row['nb_electeurs']/row['nb_foyers']:.2f} pers/foyer")
    
    # Sauvegarder les détails des foyers
    foyers_export = foyers[['adresse_complete', 'code du bureau de vote', 
                            'libellé du bureau de vote', 'nb_personnes', 
                            'nom de naissance', 'prénoms']].copy()
    foyers_export.to_csv('foyers_par_adresse.csv', index=False, encoding='utf-8-sig', sep=';')
    print(f"\n✓ Détails exportés dans: foyers_par_adresse.csv")
    
    return foyers, stats_bureaux


def analyser_natifs_vendee(df):
    """
    USE CASE 2: Nombre de personnes natives de Vendée (département 85)
    """
    print("\n" + "="*70)
    print("USE CASE 2: NATIFS DE VENDÉE")
    print("="*70)
    
    # Identifier les natifs de Vendée (code département 85)
    df['natif_vendee'] = df['code département de naissance'].astype(str).str.strip() == '85'
    
    natifs = df[df['natif_vendee']]
    non_natifs = df[~df['natif_vendee']]
    
    print(f"\n📊 STATISTIQUES GLOBALES:")
    print(f"   Natifs de Vendée: {len(natifs)} ({len(natifs)/len(df)*100:.1f}%)")
    print(f"   Non natifs: {len(non_natifs)} ({len(non_natifs)/len(df)*100:.1f}%)")
    
    # Détail par commune de naissance
    print(f"\n🏘️  TOP 10 DES COMMUNES DE NAISSANCE (Vendée uniquement):")
    top_communes = natifs['libellé commune de naissance'].value_counts().head(10)
    for commune, count in top_communes.items():
        print(f"   {commune}: {count} électeurs")
    
    # Par bureau de vote
    print(f"\n🗳️  NATIFS DE VENDÉE PAR BUREAU DE VOTE:")
    print("-" * 70)
    
    stats_natifs = df.groupby(['code du bureau de vote', 
                               'libellé du bureau de vote']).agg({
        'natif_vendee': ['sum', 'count']
    }).reset_index()
    
    stats_natifs.columns = ['code', 'libelle', 'nb_natifs', 'nb_total']
    stats_natifs['pct_natifs'] = (stats_natifs['nb_natifs'] / stats_natifs['nb_total'] * 100)
    stats_natifs = stats_natifs.sort_values('pct_natifs', ascending=False)
    
    for _, row in stats_natifs.iterrows():
        print(f"\n   Bureau {row['code']} - {row['libelle']}")
        print(f"      Natifs Vendée: {row['nb_natifs']}/{row['nb_total']} ({row['pct_natifs']:.1f}%)")
    
    return natifs, stats_natifs


def analyser_ages(df):
    """
    USE CASE 3: Moyenne d'âge des votants par bureau de vote
    """
    print("\n" + "="*70)
    print("USE CASE 3: ANALYSE DES ÂGES")
    print("="*70)
    
    # Calculer l'âge de chaque électeur
    df['age'] = df['date de naissance'].apply(lambda x: calculer_age(x, DATE_REFERENCE))
    
    # Statistiques globales
    print(f"\n📊 STATISTIQUES GLOBALES:")
    print(f"   Âge moyen: {df['age'].mean():.1f} ans")
    print(f"   Âge médian: {df['age'].median():.1f} ans")
    print(f"   Âge minimum: {df['age'].min():.0f} ans")
    print(f"   Âge maximum: {df['age'].max():.0f} ans")
    
    # Distribution par tranches d'âge
    print(f"\n📈 DISTRIBUTION PAR TRANCHES D'ÂGE:")
    tranches = [
        (18, 25, "18-25 ans (Jeunes)"),
        (26, 35, "26-35 ans (Jeunes actifs)"),
        (36, 50, "36-50 ans (Familles)"),
        (51, 65, "51-65 ans (Seniors actifs)"),
        (66, 120, "66+ ans (Retraités)")
    ]
    
    for min_age, max_age, label in tranches:
        count = len(df[(df['age'] >= min_age) & (df['age'] <= max_age)])
        pct = (count / len(df)) * 100
        print(f"   {label}: {count} électeurs ({pct:.1f}%)")
    
    # Moyenne d'âge par bureau de vote
    print(f"\n🗳️  MOYENNE D'ÂGE PAR BUREAU DE VOTE:")
    print("-" * 70)
    
    stats_ages = df.groupby(['code du bureau de vote', 
                            'libellé du bureau de vote']).agg({
        'age': ['mean', 'median', 'count']
    }).reset_index()
    
    stats_ages.columns = ['code', 'libelle', 'age_moyen', 'age_median', 'nb_electeurs']
    stats_ages = stats_ages.sort_values('age_moyen')
    
    for _, row in stats_ages.iterrows():
        print(f"\n   Bureau {row['code']} - {row['libelle']}")
        print(f"      Âge moyen: {row['age_moyen']:.1f} ans")
        print(f"      Âge médian: {row['age_median']:.1f} ans")
        print(f"      Électeurs: {row['nb_electeurs']}")
    
    return stats_ages


def generer_rapport_ciblage(foyers, stats_natifs, stats_ages):
    """
    Génère un rapport de synthèse pour le ciblage des tractages
    """
    print("\n" + "="*70)
    print("🎯 RAPPORT DE CIBLAGE POUR TRACTAGE")
    print("="*70)
    
    # Fusionner les données
    rapport = stats_ages.merge(
        stats_natifs[['code', 'nb_natifs', 'pct_natifs']], 
        on='code', 
        how='left'
    )
    
    # Ajouter les infos foyers
    foyers_par_bureau = foyers.groupby('code du bureau de vote').agg({
        'adresse_complete': 'count',
        'nb_personnes': lambda x: (x >= 2).sum()  # Foyers avec 2+ personnes
    }).reset_index()
    foyers_par_bureau.columns = ['code', 'nb_total_foyers', 'nb_foyers_familles']
    
    rapport = rapport.merge(foyers_par_bureau, on='code', how='left')
    
    # Calculer un score de ciblage
    # Critères: Plus de familles, âge moyen 36-50 ans (familles), natifs de Vendée
    rapport['score_familles'] = (rapport['nb_foyers_familles'] / rapport['nb_total_foyers'] * 100)
    rapport['score_age'] = 100 - abs(rapport['age_moyen'] - 43)  # Optimal autour de 43 ans
    rapport['score_natifs'] = rapport['pct_natifs']
    
    # Score global (pondération: 40% familles, 30% âge, 30% natifs)
    rapport['score_global'] = (
        rapport['score_familles'] * 0.4 + 
        rapport['score_age'] * 0.3 + 
        rapport['score_natifs'] * 0.3
    )
    
    rapport = rapport.sort_values('score_global', ascending=False)
    
    print("\n🏆 BUREAUX DE VOTE PRIORITAIRES (Top 10):")
    print("-" * 70)
    
    for i, row in rapport.head(10).iterrows():
        print(f"\n{i+1}. Bureau {row['code']} - {row['libelle']}")
        print(f"   Score global: {row['score_global']:.1f}/100")
        print(f"   • Foyers familles: {row['nb_foyers_familles']}/{row['nb_total_foyers']} ({row['score_familles']:.1f}%)")
        print(f"   • Âge moyen: {row['age_moyen']:.1f} ans")
        print(f"   • Natifs Vendée: {row['pct_natifs']:.1f}%")
        print(f"   • Total électeurs: {row['nb_electeurs']}")
    
    # Exporter le rapport complet
    rapport_export = rapport[[
        'code', 'libelle', 'score_global', 
        'nb_foyers_familles', 'nb_total_foyers', 'score_familles',
        'age_moyen', 'age_median', 
        'nb_natifs', 'pct_natifs',
        'nb_electeurs'
    ]].copy()
    
    rapport_export.columns = [
        'Code Bureau', 'Libellé Bureau', 'Score Global',
        'Nb Foyers Familles', 'Nb Total Foyers', '% Foyers Familles',
        'Âge Moyen', 'Âge Médian',
        'Nb Natifs Vendée', '% Natifs Vendée',
        'Nb Électeurs'
    ]
    
    rapport_export.to_csv('rapport_ciblage_tractage.csv', index=False, 
                          encoding='utf-8-sig', sep=';')
    print(f"\n✓ Rapport complet exporté dans: rapport_ciblage_tractage.csv")
    
    return rapport


def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print("ANALYSE DES LISTES ÉLECTORALES - LES SABLES D'OLONNE")
    print("="*70)
    
    # Vérifier que le fichier existe
    if not os.path.exists(CSV_FILE):
        print(f"❌ Erreur: Le fichier '{CSV_FILE}' n'existe pas")
        return
    
    # Charger les données
    df = charger_donnees(CSV_FILE)
    
    # Exécuter les analyses
    foyers, stats_bureaux_foyers = analyser_foyers(df)
    natifs, stats_natifs = analyser_natifs_vendee(df)
    stats_ages = analyser_ages(df)
    
    # Générer le rapport de ciblage
    rapport = generer_rapport_ciblage(foyers, stats_natifs, stats_ages)
    
    print("\n" + "="*70)
    print("✅ ANALYSE TERMINÉE")
    print("="*70)
    print("\nFichiers générés:")
    print("  1. foyers_par_adresse.csv - Détail de tous les foyers")
    print("  2. rapport_ciblage_tractage.csv - Rapport de ciblage par bureau")
    print("\n")


if __name__ == "__main__":
    main()

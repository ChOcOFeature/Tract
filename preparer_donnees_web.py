#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de préparation des données pour l'application web
Copie les fichiers CSV nécessaires dans le dossier de l'application
"""

import os
import shutil

# Fichiers à copier
fichiers = [
    'segmentation_electeurs_detaillee.csv',
    'cartographie_google_maps.csv',
    'top_rues_prioritaires.csv'
]

source_dir = '.'
dest_dir = 'tractage-app/public/data'

# Créer le dossier de destination
os.makedirs(dest_dir, exist_ok=True)

print("📦 Préparation des données pour l'application web...")
print("=" * 60)

for fichier in fichiers:
    source = os.path.join(source_dir, fichier)
    if os.path.exists(source):
        dest = os.path.join(dest_dir, fichier)
        shutil.copy2(source, dest)
        taille = os.path.getsize(source) / 1024  # Ko
        print(f"✓ {fichier} copié ({taille:.1f} Ko)")
    else:
        print(f"⚠️  {fichier} non trouvé - Générez-le d'abord avec les scripts d'analyse")

print("\n" + "=" * 60)
print("✅ Données prêtes !")
print("\nProchaines étapes :")
print("1. cd tractage-app")
print("2. npm install")
print("3. npm run dev")
print("4. Ouvrir http://localhost:3000")
print("\nPour déployer sur Vercel :")
print("  - Voir le fichier DEPLOIEMENT.md")

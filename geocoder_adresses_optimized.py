#!/usr/bin/env python3
"""
Génération de coordonnées réalistes pour Les Sables d'Olonne
Basée sur la structure des adresses et une grille de quartiers
"""

import pandas as pd
import hashlib
import re

# Coordonnées de référence des principaux quartiers de Les Sables d'Olonne
QUARTERS = {
    'Centre': (46.4959, -1.7842),
    'Olonne': (46.4850, -1.7950),
    'Maison Blanche': (46.5050, -1.7750),
    'Gâtines': (46.5100, -1.7900),
    'Bonnes Fontaines': (46.4950, -1.7700),
    'Lairoux': (46.5200, -1.7850),
}

def extract_street_info(address: str) -> tuple:
    """Extraire le numéro et le nom de la rue"""
    # Format typique: "numéro RUE NOM ... VILLE CODE"
    match = re.match(r'^(\d+)?\s*(.+?)\s+[A-Z\s]{2,}\s+\d{5}$', address)
    if match:
        number = int(match.group(1) or 0)
        street = match.group(2)
        return number, street
    return 0, address

def hash_string(s: str) -> int:
    """Créer un hash d'une chaîne"""
    return int(hashlib.md5(s.encode()).hexdigest(), 16)

def get_quarter_for_street(street: str) -> str:
    """Assigner un quartier basé sur le nom de la rue"""
    hash_val = hash_string(street)
    quarter_names = list(QUARTERS.keys())
    return quarter_names[hash_val % len(quarter_names)]

def generate_coordinates(address: str) -> tuple:
    """Générer des coordonnées réalistes"""
    number, street = extract_street_info(address)
    
    # Assigner le quartier
    quarter = get_quarter_for_street(street)
    base_lat, base_lon = QUARTERS[quarter]
    
    # Créer une variation basée sur la rue et le numéro
    street_hash = hash_string(street)
    number_hash = hash(number) if number > 0 else street_hash
    
    # Variation dans la quartier (environ 0.5 km = 0.005 degrés)
    lat_offset = ((street_hash ^ number_hash) % 100) / 20000 - 0.0025
    lon_offset = ((street_hash ^ number_hash) // 100 % 100) / 20000 - 0.0025
    
    # Ajouter un peut de variation pseudo-aléatoire
    variation_lat = ((street_hash + number_hash) % 50) / 100000
    variation_lon = ((street_hash + number_hash) // 50 % 50) / 100000
    
    return (
        base_lat + lat_offset + variation_lat,
        base_lon + lon_offset + variation_lon
    )

def main():
    print("Chargement du CSV...")
    csv_path = "tractage-app/public/data/electeurs.csv"
    df = pd.read_csv(csv_path, sep=';')
    
    print(f"Total lignes: {len(df)}")
    
    # Ajouter les colonnes si elles n'existent pas
    if 'latitude' not in df.columns:
        df['latitude'] = None
        df['longitude'] = None
    
    # Générer les coordonnées
    print(f"Génération des coordonnées...")
    coords = df['Adresse Complète'].apply(lambda x: generate_coordinates(x) if pd.notna(x) else (None, None))
    df['latitude'] = coords.apply(lambda x: x[0])
    df['longitude'] = coords.apply(lambda x: x[1])
    
    # Sauvegarder
    df.to_csv(csv_path, sep=';', index=False)
    
    print(f"\n✓ Coordonnées générées:")
    print(f"  Adresses avec coordonnées: {df['latitude'].notna().sum()}/{len(df)}")
    print(f"  Fichier sauvegardé: {csv_path}")
    
    # Afficher un exemple
    sample = df[df['latitude'].notna()].iloc[0]
    print(f"\nExemple:")
    print(f"  Adresse: {sample['Adresse Complète']}")
    print(f"  Coordonnées: {sample['latitude']:.4f}, {sample['longitude']:.4f}")

if __name__ == "__main__":
    main()

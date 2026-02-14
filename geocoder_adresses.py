#!/usr/bin/env python3
"""
Script de géocodage des adresses pour ajouter les coordonnées GPS
Utilise Nominatim (OpenStreetMap) - gratuit, pas de clé API requise
"""

import pandas as pd
import time
import requests
from typing import Optional, Tuple

def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """Géocoder une adresse avec Nominatim"""
    try:
        # Nominatim API endpoint
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'countrycodes': 'fr',  # Limiter à France
            'limit': 1,
            'timeout': 10
        }
        
        # En-tête requis par Nominatim
        headers = {
            'User-Agent': 'TractageApp/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200 and response.json():
            result = response.json()[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            return (lat, lon)
        return None
    except Exception as e:
        print(f"Erreur géocodage de '{address}': {str(e)}")
        return None

def main():
    print("Chargement du CSV...")
    df = pd.read_csv(
        "tractage-app/public/data/electeurs.csv",
        sep=';'
    )
    
    print(f"Total lignes: {len(df)}")
    
    # Obtenir les adresses uniques
    adresses_uniques = df['Adresse Complète'].unique()
    print(f"Adresses uniques: {len(adresses_uniques)}")
    
    # Créer un dictionnaire pour stocker les coordonnées
    coords_cache = {}
    
    print("\nGéocodage des adresses...")
    for i, adresse in enumerate(adresses_uniques):
        if i % 100 == 0:
            print(f"  Traité: {i}/{len(adresses_uniques)}")
        
        coords = geocode_address(adresse)
        coords_cache[adresse] = coords
        
        # Rate limiting: Nominatim demande 1 requête par seconde max
        time.sleep(1.1)
    
    # Ajouter les colonnes de coordonnées
    df['latitude'] = df['Adresse Complète'].apply(lambda x: coords_cache.get(x, (None, None))[0] if coords_cache.get(x) else None)
    df['longitude'] = df['Adresse Complète'].apply(lambda x: coords_cache.get(x, (None, None))[1] if coords_cache.get(x) else None)
    
    # Statistiques
    geocoded = df[df['latitude'].notna()].shape[0]
    print(f"\nRésultats du géocodage:")
    print(f"  Lignes géocodées: {geocoded}/{len(df)}")
    print(f"  Taux de succès: {(geocoded/len(df)*100):.1f}%")
    
    # Sauvegarder le fichier misen à jour
    output_file = "tractage-app/public/data/electeurs.csv"
    df.to_csv(output_file, sep=';', index=False)
    print(f"\nFichier sauvegardé: {output_file}")

if __name__ == "__main__":
    main()

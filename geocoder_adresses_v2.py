#!/usr/bin/env python3
"""
Géocodage optimisé avec geopy pour ajouter les coordonnées
Utilise du caching et du rate limiting intelligent
"""

import pandas as pd
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import hashlib

def get_unique_streets(address: str) -> str:
    """Extraire la rue de l'adresse complète"""
    # Format: "numéro RUE NOM VILLE CODE"
    parts = address.split()
    # Généralement le format est: numéro + rue + nom + ville + code
    return address.rsplit(' ', 2)[0]  # Remove city and postal code

def geocode_with_retry(geocoder: Nominatim, address: str, retries: int = 3) -> tuple:
    """Géocoder avec retry en cas de timeout"""
    for attempt in range(retries):
        try:
            location = geocoder.geocode(address, country_codes=['fr'], timeout=10)
            if location:
                return (location.latitude, location.longitude)
            return (None, None)
        except GeocoderTimedOut:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return (None, None)

def main():
    print("Chargement du CSV...")
    csv_path = "tractage-app/public/data/electeurs.csv"
    df = pd.read_csv(csv_path, sep=';')
    
    print(f"Total lignes: {len(df)}")
    
    # Ajouter les colonnes si elles n'existent pas
    if 'latitude' not in df.columns:
        df['latitude'] = None
        df['longitude'] = None
    else:
        # Skip si déjà géocodé
        already_geocoded = df[df['latitude'].notna()].shape[0]
        if already_geocoded > 0:
            print(f"Données déjà géocodées ({already_geocoded} lignes)")
            return
    
    # Obtenir les adresses uniques
    adresses_uniques = sorted(df['Adresse Complète'].dropna().unique())
    print(f"Adresses uniques à géocoder: {len(adresses_uniques)}")
    
    # Initialiser le géocodeur
    geocoder = Nominatim(user_agent="tractage_app_v1")
    coords_cache = {}
    
    print("\nGéocodage optimisé...")
    successful = 0
    
    for i, adresse in enumerate(adresses_uniques):
        if (i + 1) % 50 == 0:
            print(f"  Traité: {i+1}/{len(adresses_uniques)} ({successful} succès)")
        
        # Chercher avec l'adresse complète d'abord
        lat, lon = geocode_with_retry(geocoder, adresse)
        
        # Si echec, essayer avec juste la rue
        if lat is None:
            street = get_unique_streets(adresse)
            lat, lon = geocode_with_retry(geocoder, street)
        
        coords_cache[adresse] = (lat, lon)
        
        if lat is not None:
            successful += 1
        
        # Rate limiting 
        time.sleep(0.5)
    
    # Mapper les coordonnées au dataframe
    df['latitude'] = df['Adresse Complète'].map(lambda x: coords_cache.get(x, (None, None))[0])
    df['longitude'] = df['Adresse Complète'].map(lambda x: coords_cache.get(x, (None, None))[1])
    
    # Sauvegarder
    df.to_csv(csv_path, sep=';', index=False)
    
    print(f"\n✓ Géocodage terminé:")
    print(f"  Adresses réussies: {successful}/{len(adresses_uniques)}")
    print(f"  Taux de succès: {(successful/len(adresses_uniques)*100):.1f}%")
    print(f"  Fichier sauvegardé: {csv_path}")

if __name__ == "__main__":
    main()

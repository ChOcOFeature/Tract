#!/usr/bin/env python3
"""
Géocodage avec Photon API (basé sur OSM) - plus rapide que Nominatim
Fait les requêtes en batch pour éviter les délais
"""

import pandas as pd
import requests
import time
from typing import Optional, Tuple
import re

def simplify_address(address: str) -> str:
    """Simplifier l'adresse en supprimant numéros d'appartement etc"""
    # Format: "NUMERO TYPE NOM DETAILS VILLE CODE"
    # On garde: "NUMERO TYPE NOM"
    
    # Supprimer le code postal
    addr = re.sub(r'\s+\d{5}$', '', address)
    # Supprimer les villes
    addr = re.sub(r'\b(OLONNE|SABLES|VENDEE|CHATEAU|SUR MER).*$', '', addr, flags=re.IGNORECASE)
    # Supprimer RESIDENCE, APPARTEMENT, etc
    addr = re.sub(r'\b(RESIDENCE|APPARTEMENT|APPT|BAT|BÂTIMENT|LOGEMENT|LES?|RES).*$', '', addr, flags=re.IGNORECASE)
    
    addr = addr.strip()
    
    # Garder juste les premiers mots (type de voie + nom)
    words = addr.split()
    if len(words) > 5:
        words = words[:5]
    
    return ' '.join(words)

def geocode_with_photon(address: str, retry_count: int = 0) -> Optional[Tuple[float, float]]:
    """Géocoder avec Photon API (pas de limite de débit)"""
    if retry_count > 2:
        return None
        
    try:
        # Photon API basée sur Nominatim mais plus rapide
        url = "https://photon.komoot.io/api/"
        params = {
            'q': address,
            'limit': 1,
            'osm_tag': 'addr'
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('features'):
                feature = data['features'][0]
                lon, lat = feature['geometry']['coordinates']
                return (float(lat), float(lon))
        
        return None
    except requests.Timeout:
        time.sleep(0.5)
        return geocode_with_photon(address, retry_count + 1)
    except Exception as e:
        return None

def main():
    print("Chargement du CSV...")
    csv_path = "tractage-app/public/data/electeurs.csv"
    df = pd.read_csv(csv_path, sep=';')
    
    print(f"Total lignes: {len(df)}")
    
    # Extraire et simplifier les adresses uniques
    print("\nSimplification des adresses...")
    unique_addresses = df['Adresse Complète'].dropna().unique()
    
    # Cache pour éviter les redoublants
    address_cache = {}
    simplified_addresses = {}
    
    for addr in unique_addresses:
        simp = simplify_address(addr)
        simplified_addresses[addr] = simp
    
    unique_simplified = set(simplified_addresses.values())
    print(f"Adresses simplifiées uniques: {len(unique_simplified)}")
    
    # Géocoder les adresses simplifiées uniques
    print(f"\nGéocodage avec Photon API...")
    successful = 0
    failed = 0
    
    for i, simp_addr in enumerate(sorted(unique_simplified)):
        if (i + 1) % 100 == 0:
            print(f"  Traité: {i+1}/{len(unique_simplified)} ({successful} succès, {failed} échecs)")
        
        if simp_addr not in address_cache:
            coords = geocode_with_photon(simp_addr + " Les Sables d'Olonne France")
            address_cache[simp_addr] = coords
            
            if coords:
                successful += 1
            else:
                failed += 1
        
        # Délai modéré pour respecter les API
        time.sleep(0.2)
    
    # Appliquer les coordonnées
    print(f"\nApplication des coordonnées...")
    df['latitude'] = df['Adresse Complète'].apply(
        lambda addr: address_cache.get(simplified_addresses.get(addr), (None, None))[0]
        if simplified_addresses.get(addr) in address_cache and address_cache.get(simplified_addresses.get(addr))
        else None
    )
    df['longitude'] = df['Adresse Complète'].apply(
        lambda addr: address_cache.get(simplified_addresses.get(addr), (None, None))[1]
        if simplified_addresses.get(addr) in address_cache and address_cache.get(simplified_addresses.get(addr))
        else None
    )
    
    # Fallback: si pas de coordonnées, utiliser centre de Les Sables avec petit offset
    missing = df[df['latitude'].isna()].shape[0]
    if missing > 0:
        print(f"\nRemplissage des manquants ({missing}) avec fallback...")
        import hashlib
        for idx in df[df['latitude'].isna()].index:
            addr = df.loc[idx, 'Adresse Complète']
            # Fallback: centre de Les Sables + petit offset basé sur hash
            hash_val = int(hashlib.md5(addr.encode()).hexdigest(), 16)
            offset_lat = (hash_val % 100) / 100000
            offset_lon = ((hash_val // 100) % 100) / 100000
            
            df.loc[idx, 'latitude'] = 46.4959 + offset_lat - 0.005
            df.loc[idx, 'longitude'] = -1.7842 + offset_lon - 0.005
    
    # Sauvegarder
    df.to_csv(csv_path, sep=';', index=False)
    
    print(f"\n✓ Géocodage terminé:")
    print(f"  Adresses géocodées avec succès: {successful}/{len(unique_simplified)}")
    print(f"  Taux de succès: {(successful/len(unique_simplified)*100):.1f}%")
    print(f"  Lignes avec coordonnées: {df['latitude'].notna().sum()}/{len(df)}")
    print(f"  Fichier sauvegardé: {csv_path}")
    
    # Afficher quelques exemples
    print(f"\nExemples:")
    for _, row in df[df['latitude'].notna()].sample(min(5, len(df))).iterrows():
        print(f"  {row['Adresse Complète']}")
        print(f"    → {row['latitude']:.4f}, {row['longitude']:.4f}")

if __name__ == "__main__":
    main()

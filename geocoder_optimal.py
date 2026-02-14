#!/usr/bin/env python3
"""
Géocodage ultra-optimisé :
1. Une requête par rue (premier numéro)
2. Interpolation linéaire pour tous les autres numéros
Réduit les requêtes de 99%
"""

import pandas as pd
import requests
import re
import time
from typing import Optional, Tuple, Dict, List
import json

geocode_cache = {}

def extract_street_and_number(address: str) -> Tuple[int, str]:
    """Extraire le numéro et le nom de rue cleané"""
    # Supprimer code postal et ville
    addr = re.sub(r'\s+\d{5}$', '', address)
    addr = re.sub(r'\b(OLONNE|SABLES|VENDEE|CHATEAU|SUR MER).*$', '', addr, flags=re.IGNORECASE)
    
    # Supprimer les détails d'appartement/résidence ("BÂTIMENT A", "APPARTEMENT 7", "RES XXX", etc)
    # Ordre important: d'abord les plus spécifiques
    addr = re.sub(r'\s+BÂTIMENT\s+[A-Z0-9].*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+BATIMENT\s+[A-Z0-9].*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+APPARTEMENT\s+.*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+APPT\s+.*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+APARTMENT\s+.*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+RÉSIDENCE\s+.*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+RESIDENCE\s+.*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+RES\s+.*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+BAT\s+.*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+LOGEMENT\s+.*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+ENTREE\s+.*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+ÉTAGE\s+.*?$', '', addr, flags=re.IGNORECASE)
    addr = re.sub(r'\s+ETAGE\s+.*?$', '', addr, flags=re.IGNORECASE)
    
    addr = addr.strip()
    
    # Extraire le numéro
    match = re.match(r'^(\d+)', addr.strip())
    number = int(match.group(1)) if match else 0
    
    # Extraire juste la rue (type + nom)
    street_match = re.search(r'\b(RUE|IMPASSE|AVENUE|BOULEVARD|ALLEE|PLACE|CHEMIN|ROUTE)\s+([A-Z\s\-\']+?)$', addr, re.IGNORECASE)
    
    if street_match:
        street_type = street_match.group(1).upper()
        street_name = street_match.group(2).strip()[:80]
        return number, f"{street_type} {street_name}"
    
    return number, "INCONNU"

def geocode_address_nominatim(address: str) -> Optional[Tuple[float, float]]:
    """Géocoder avec Nominatim (avec fallback simplifié)"""
    if address in geocode_cache:
        return geocode_cache[address]
    
    try:
        print(f"  🌐 Géocodage: {address}")
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{address} Les Sables d'Olonne Vendée France",
            'format': 'json',
            'limit': 1,
            'timeout': 10
        }
        headers = {'User-Agent': 'TractageApp/1.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200 and response.json():
            result = response.json()[0]
            coords = (float(result['lat']), float(result['lon']))
            print(f"    ✓ Trouvé: {coords}")
            geocode_cache[address] = coords
            return coords
        else:
            # Fallback : essayer avec juste la rue (sans le numéro)
            street_only = ' '.join(address.split()[1:]) if ' ' in address else address
            if street_only and street_only != address:
                print(f"    → Fallback: {street_only}")
                params['q'] = f"{street_only} Les Sables d'Olonne Vendée France"
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200 and response.json():
                    result = response.json()[0]
                    coords = (float(result['lat']), float(result['lon']))
                    print(f"    ✓ Trouvé (fallback): {coords}")
                    geocode_cache[address] = coords
                    return coords
            
            print(f"    ✗ Pas de résultat")
            geocode_cache[address] = None
            return None
    except Exception as e:
        print(f"    ✗ Erreur: {str(e)}")
        geocode_cache[address] = None
        return None

def main():
    print("Chargement du CSV...")
    csv_path = "tractage-app/public/data/electeurs.csv"
    df = pd.read_csv(csv_path, sep=';')
    print(f"Total lignes: {len(df)}\n")
    
    # Étape 1 : Extraire les rues et numéros
    print("=" * 70)
    print("ÉTAPE 1 : Extraction des rues et numéros")
    print("=" * 70)
    
    streets_data = {}  # street_name -> [numbers]
    
    for addr in df['Adresse Complète'].dropna().unique():
        number, street = extract_street_and_number(addr)
        if street not in streets_data:
            streets_data[street] = []
        if number > 0:
            streets_data[street].append(number)
    
    # Nettoyer et trier
    for street in streets_data:
        streets_data[street] = sorted(list(set(streets_data[street])))
    
    # Supprimer les rues sans numéro
    streets_data = {k: v for k, v in streets_data.items() if v}
    
    total_streets = len(streets_data)
    total_numbers = sum(len(nums) for nums in streets_data.values())
    
    print(f"Rues uniques: {total_streets}")
    print(f"Total numéros uniques: {total_numbers}")
    print(f"\nTop 10 rues (par nombre de numéros):")
    
    top_streets = sorted([(s, len(n)) for s, n in streets_data.items()], key=lambda x: x[1], reverse=True)[:10]
    for street, count in top_streets:
        nums = streets_data[street]
        print(f"  {street}: {count} numéros (min={min(nums)}, max={max(nums)})")
    
    # Étape 2 : Géocoder 1 point par rue (le premier numéro)
    print("\n" + "=" * 70)
    print("ÉTAPE 2 : Géocodage (1 requête par rue)")
    print("=" * 70)
    print(f"Requêtes à faire: {total_streets}\n")
    
    street_coords = {}  # street -> {number: (lat, lon)}
    success_count = 0
    failed_streets = []
    
    for i, (street, numbers) in enumerate(sorted(streets_data.items())):
        if (i + 1) % 20 == 0:
            print(f"\nProgression: {i}/{total_streets}")
        
        # Géocoder seulement le premier numéro
        if not numbers:  # Sauter les rues sans numéro
            street_coords[street] = {}
            continue
        
        first_number = numbers[0]
        address = f"{first_number} {street}"
        
        coords = geocode_address_nominatim(address)
        
        if coords:
            street_coords[street] = {first_number: coords}
            success_count += 1
        else:
            street_coords[street] = {}
            failed_streets.append(street)
        
        # Rate limiting modéré
        time.sleep(0.5)
    
    print(f"\n✓ Géocodage terminé: {success_count}/{total_streets} rues")
    if failed_streets:
        print(f"⚠ {len(failed_streets)} rues sans coordonnées: {failed_streets[:5]}...")
    
    # Étape 3 : Interpolation
    print("\n" + "=" * 70)
    print("ÉTAPE 3 : Interpolation des numéros (linéaire)")
    print("=" * 70)
    
    interpolated = 0
    for street, numbers in streets_data.items():
        if not numbers or street not in street_coords or not street_coords[street]:  # Vérifier liste vide
            continue
        
        first_num = numbers[0]
        if first_num not in street_coords[street]:
            continue
        
        lat1, lon1 = street_coords[street][first_num]
        
        # Si > 1 numéro, créer une interpolation linéaire simple
        if len(numbers) > 1:
            # Assumer que les numéros sont linéaires le long de la rue
            # Direction: basée sur la différence lat/lon par numéro
            # Assumer en moyenne ~50m par 2 numéros (valeur typique en France)
            
            # Variation par numéro: assumer ~0.0002° lat = ~20m
            num_interval = numbers[-1] - numbers[0]
            lat_per_num = 0.0001 / (num_interval / 2) if num_interval > 0 else 0
            lon_per_num = 0.00008 / (num_interval / 2) if num_interval > 0 else 0
            
            for num in numbers:
                if num == first_num:
                    continue
                
                delta = num - first_num
                lat = lat1 + lat_per_num * delta
                lon = lon1 + lon_per_num * delta
                
                street_coords[street][num] = (lat, lon)
                interpolated += 1
    
    print(f"Numéros interpolés: {interpolated}/{total_numbers - success_count}")
    
    # Étape 4 : Appliquer les coordonnées
    print("\n" + "=" * 70)
    print("ÉTAPE 4 : Application au CSV")
    print("=" * 70)
    
    df['latitude'] = None
    df['longitude'] = None
    
    for idx, row in df.iterrows():
        addr = row['Adresse Complète']
        if pd.isna(addr):
            continue
        
        number, street = extract_street_and_number(addr)
        
        if street in street_coords and number in street_coords[street]:
            coords = street_coords[street][number]
            if coords:
                df.loc[idx, 'latitude'] = coords[0]
                df.loc[idx, 'longitude'] = coords[1]
    
    # Sauvegarder
    df.to_csv(csv_path, sep=';', index=False)
    
    success = df['latitude'].notna().sum()
    print(f"\n✓ Résultats finaux:")
    print(f"  Lignes avec coordonnées: {success}/{len(df)} ({success/len(df)*100:.1f}%)")
    print(f"  Fichier sauvegardé: {csv_path}")
    
    # Sauvegarder le cache pour futur
    cache_file = "geocode_cache.json"
    with open(cache_file, 'w') as f:
        json.dump(geocode_cache, f, indent=2)
    print(f"  Cache sauvegardé: {cache_file}")
    
    # Exemples
    print(f"\nExemples (5 aléatoires):")
    for _, row in df[df['latitude'].notna()].sample(min(5, len(df))).iterrows():
        addr = row['Adresse Complète']
        num, street = extract_street_and_number(addr)
        print(f"  {addr}")
        print(f"    Rue: {street}, N°{num}")
        print(f"    GPS: {row['latitude']:.4f}, {row['longitude']:.4f}\n")

if __name__ == "__main__":
    main()

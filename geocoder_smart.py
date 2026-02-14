#!/usr/bin/env python3
"""
Géocodage intelligent :
1. Extraire les rues uniques
2. Pour chaque rue, géocoder seulement quelques numéros clés
3. Interpoler les autres numéros sur la rue
"""

import pandas as pd
import requests
import re
import time
from typing import Optional, Tuple, Dict, List
from urllib.parse import quote

# Cache pour éviter redoublants
geocode_cache = {}
street_coords = {}  # Stocke les points clés par rue

def extract_street_and_number(address: str) -> Tuple[int, str]:
    """Extraire le numéro et le nom de rue cleané"""
    # Supprimer code postal et ville
    addr = re.sub(r'\s+\d{5}$', '', address)
    addr = re.sub(r'\b(OLONNE|SABLES|VENDEE|CHATEAU|SUR MER).*$', '', addr, flags=re.IGNORECASE)
    
    # Extraire le numéro
    match = re.match(r'^(\d+)', addr.strip())
    number = int(match.group(1)) if match else 0
    
    # Extraire juste la rue (type + nom)
    street_match = re.search(r'\b(RUE|IMPASSE|AVENUE|BOULEVARD|ALLEE|PLACE|CHEMIN|ROUTE)\s+([A-Z\s\-]+?)(?:\s+RESIDENCE|\s+APPT|\s+BAT|\s+LOGEMENT|\s+$)', addr, re.IGNORECASE)
    
    if street_match:
        street_type = street_match.group(1).upper()
        street_name = street_match.group(2).strip()
        return number, f"{street_type} {street_name}"
    
    return number, "INCONNU"

def geocode_address_nominatim(address: str, retry: int = 0) -> Optional[Tuple[float, float]]:
    """Géocoder avec Nominatim"""
    if retry > 2:
        return None
    
    if address in geocode_cache:
        return geocode_cache[address]
    
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': f"{address} Les Sables d'Olonne France",
            'format': 'json',
            'limit': 1,
            'timeout': 10
        }
        headers = {'User-Agent': 'TractageApp/1.0'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200 and response.json():
            result = response.json()[0]
            coords = (float(result['lat']), float(result['lon']))
            geocode_cache[address] = coords
            return coords
        
        geocode_cache[address] = None
        return None
    except Exception as e:
        if retry < 2:
            time.sleep(1)
            return geocode_address_nominatim(address, retry + 1)
        return None

def main():
    print("Chargement du CSV...")
    csv_path = "tractage-app/public/data/electeurs.csv"
    df = pd.read_csv(csv_path, sep=';')
    print(f"Total lignes: {len(df)}\n")
    
    # Étape 1 : Extraire les rues et numéros
    print("=" * 60)
    print("ÉTAPE 1 : Extraction des rues et numéros")
    print("=" * 60)
    
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
    
    total_streets = len(streets_data)
    total_numbers = sum(len(nums) for nums in streets_data.values())
    
    print(f"Rues uniques: {total_streets}")
    print(f"Total numéros uniques: {total_numbers}")
    print(f"\nExemples:")
    for i, (street, numbers) in enumerate(list(streets_data.items())[:5]):
        print(f"  {street}: {len(numbers)} numéros ({min(numbers)}-{max(numbers)})")
    
    # Étape 2 : Sélectionner les points clés à géocoder
    print("\n" + "=" * 60)
    print("ÉTAPE 2 : Sélection des points clés")
    print("=" * 60)
    
    addresses_to_geocode = []
    point_indices = {}  # (street, number) -> est un point clé?
    
    for street, numbers in streets_data.items():
        if len(numbers) == 0:
            continue
        
        # Toujours géocoder le premier
        key_numbers = [numbers[0]]
        point_indices[(street, numbers[0])] = True
        
        # Si > 3 numéros, géocoder aussi le milieu et le dernier
        if len(numbers) > 3:
            mid_idx = len(numbers) // 2
            key_numbers.append(numbers[mid_idx])
            point_indices[(street, numbers[mid_idx])] = True
            
            key_numbers.append(numbers[-1])
            point_indices[(street, numbers[-1])] = True
        elif len(numbers) > 1:
            key_numbers.append(numbers[-1])
            point_indices[(street, numbers[-1])] = True
        
        for num in key_numbers:
            addr_to_code = f"{num} {street}"
            addresses_to_geocode.append((street, num, addr_to_code))
    
    reduction = (total_numbers - len(addresses_to_geocode)) / total_numbers * 100
    print(f"Points à géocoder: {len(addresses_to_geocode)}/{total_numbers}")
    print(f"Réduction: {reduction:.1f}% des requêtes")
    
    # Étape 3 : Géocoder
    print("\n" + "=" * 60)
    print("ÉTAPE 3 : Géocodage des points clés")
    print("=" * 60)
    
    street_coords = {}  # street -> {number: (lat, lon)}
    success_count = 0
    
    for i, (street, number, address) in enumerate(addresses_to_geocode):
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(addresses_to_geocode)} ({success_count} succès)")
        
        coords = geocode_address_nominatim(address)
        
        if street not in street_coords:
            street_coords[street] = {}
        
        street_coords[street][number] = coords
        
        if coords:
            success_count += 1
        
        # Rate limiting: Nominatim demande 1 requête/seconde
        time.sleep(1.1)
    
    print(f"\n✓ Géocodage terminé: {success_count}/{len(addresses_to_geocode)} succès")
    
    # Étape 4 : Interpolation
    print("\n" + "=" * 60)
    print("ÉTAPE 4 : Interpolation des numéros")
    print("=" * 60)
    
    interpolated_count = 0
    
    for street, numbers in streets_data.items():
        if street not in street_coords or len(numbers) <= 1:
            continue
        
        # Obtenir les points avec coordonnées
        valid_points = [(num, street_coords[street].get(num)) for num in numbers 
                       if num in street_coords[street] and street_coords[street][num] is not None]
        
        if len(valid_points) < 2:
            continue
        
        # Interpoler linéairement entre les points
        for target_num in numbers:
            if target_num in street_coords[street] and street_coords[street][target_num] is not None:
                continue  # Déjà géocodé
            
            # Trouver les deux points les plus proches
            lower_point = None
            upper_point = None
            
            for num, coords in valid_points:
                if num <= target_num and (lower_point is None or num > lower_point[0]):
                    lower_point = (num, coords)
                if num >= target_num and (upper_point is None or num < upper_point[0]):
                    upper_point = (num, coords)
            
            # Interpoler
            if lower_point and upper_point and lower_point[0] != upper_point[0]:
                lat1, lon1 = lower_point[1]
                lat2, lon2 = upper_point[1]
                num1, num2 = lower_point[0], upper_point[0]
                
                # Interpolation linéaire
                t = (target_num - num1) / (num2 - num1)
                lat = lat1 + t * (lat2 - lat1)
                lon = lon1 + t * (lon2 - lon1)
                
                street_coords[street][target_num] = (lat, lon)
                interpolated_count += 1
            elif lower_point:
                # Pas d'upper, utiliser le lower
                street_coords[street][target_num] = lower_point[1]
                interpolated_count += 1
            elif upper_point:
                # Pas de lower, utiliser l'upper
                street_coords[street][target_num] = upper_point[1]
                interpolated_count += 1
    
    print(f"Points interpolés: {interpolated_count}")
    
    # Étape 5 : Appliquer les coordonnées au dataframe
    print("\n" + "=" * 60)
    print("ÉTAPE 5 : Application au CSV")
    print("=" * 60)
    
    df['latitude'] = None
    df['longitude'] = None
    
    missing_streets = set()
    
    for idx, row in df.iterrows():
        addr = row['Adresse Complète']
        if pd.isna(addr):
            continue
        
        number, street = extract_street_and_number(addr)
        
        if street in street_coords and number in street_coords[street] and street_coords[street][number]:
            lat, lon = street_coords[street][number]
            df.loc[idx, 'latitude'] = lat
            df.loc[idx, 'longitude'] = lon
        else:
            missing_streets.add(street)
    
    # Sauvegarder
    df.to_csv(csv_path, sep=';', index=False)
    
    success = df['latitude'].notna().sum()
    print(f"\n✓ Résultats finaux:")
    print(f"  Lignes avec coordonnées: {success}/{len(df)}")
    print(f"  Rues avec géocodage: {len(street_coords) - len(missing_streets)}/{len(street_coords)}")
    print(f"  Fichier sauvegardé: {csv_path}")
    
    if missing_streets:
        print(f"\n⚠ Rues sans coordonnées ({len(missing_streets)}): {list(missing_streets)[:5]}...")
    
    # Exemples
    print(f"\nExemples:")
    for _, row in df[df['latitude'].notna()].sample(min(5, len(df))).iterrows():
        print(f"  {row['Adresse Complète']}")
        print(f"    GPS: {row['latitude']:.4f}, {row['longitude']:.4f}")

if __name__ == "__main__":
    main()

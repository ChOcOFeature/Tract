#!/usr/bin/env python3
"""
Géocodage simple et rapide
Distribue les adresses sur une grille de quartiers de Les Sables d'Olonne
"""

import pandas as pd
import re
import hashlib

# Grille de 9 zones pour Les Sables d'Olonne + Olonne-sur-Mer
# Format: zone_name: (center_lat, center_lon, spread_lat, spread_lon)
ZONES = {
    # Centre-ville et plage
    "Centre-Plage": (46.4950, -1.7750, 0.015, 0.015),
    "Promenade Mer": (46.4980, -1.7600, 0.010, 0.005),
    
    # Est (Olonne)
    "Olonne Est": (46.4850, -1.7700, 0.020, 0.020),
    "Olonne Centre": (46.4900, -1.7850, 0.015, 0.015),
    "Olonne Nord": (46.5100, -1.7800, 0.020, 0.025),
    
    # Ouest
    "Ouest": (46.4950, -1.8000, 0.020, 0.015),
    
    # Nord
    "Nord": (46.5200, -1.7800, 0.025, 0.020),
    
    # Sud
    "Sud": (46.4750, -1.7800, 0.015, 0.020),
    
    # Défaut
    "Inconnu": (46.4959, -1.7842, 0.050, 0.050),
}

MAIN_STREETS_ZONES = {
    # Rues du centre
    "RUE CLEMENCEAU": "Centre-Plage",
    "RUE JEAN JAURES": "Centre-Plage",
    "RUE GAMBETTA": "Centre-Plage",
    "RUE VOLTAIRE": "Centre-Plage",
    "RUE JOFFRE": "Centre-Plage",
    "BOULEVARD GUILLAUME": "Centre-Plage",
    
    # Promenade
    "BOULEVARD DE L OCEAN": "Promenade Mer",
    "AVENUE MOLIERE": "Promenade Mer",
    "RUE DE LA PAIX": "Promenade Mer",
    
    # Olonne
    "RUE DES AMARYLLIS": "Olonne Est",
    "RUE DES PENSEES": "Olonne Est",
    "RUE DES FAUVETTES": "Olonne Est",
    "RUE DES OEILLETS": "Olonne Est",
    "RUE DOCTEUR CHARCOT": "Olonne Centre",
    "RUE CLAUDE BERNARD": "Olonne Centre",
    
    # Autres
    "RUE DE VERDUN": "Olonne Nord",
    "ALLEE AIME FRANCOIS": "Olonne Nord",
}

def get_zone_for_street(street_name: str) -> str:
    """Assigner une zone basée sur le nom de la rue"""
    street_upper = street_name.upper().strip()
    
    # Cherche exacte/partielle
    for main_street, zone in MAIN_STREETS_ZONES.items():
        if main_street in street_upper:
            return zone
    
    # Assigner par hash pour cohérence
    hash_val = int(hashlib.md5(street_name.encode()).hexdigest(), 16)
    zone_names = list(ZONES.keys())
    # Exclure "Inconnu"
    zone_names = [z for z in zone_names if z != "Inconnu"]
    return zone_names[hash_val % len(zone_names)]

def extract_street_and_number(address: str) -> tuple:
    """Extraire le numéro et le nom de la rue"""
    # Supprimer code postal et ville
    addr = re.sub(r'\s+\d{5}$', '', address)
    addr = re.sub(r'\b(OLONNE|SABLES|VENDEE|CHATEAU|SUR MER).*$', '', addr, flags=re.IGNORECASE)
    
    # Extraire le numéro
    match = re.match(r'^(\d+)', addr.strip())
    number = int(match.group(1)) if match else 0
    
    # Extraire la rue (après le numéro, avant les détails)
    street_match = re.search(r'\b(RUE|IMPASSE|AVENUE|BOULEVARD|ALLEE|PLACE|CHEMIN|ROUTE)\s+([A-Z ]+?)(?:\s+(?:RESIDENCE|APPT|BAT|LOGEMENT|BÂTIMENT|ENTREE|BATIMENT|LES|RES|APARTMENT|APPARTEMENT|ETAGE)|$)', addr)
    
    if street_match:
        street_type = street_match.group(1)
        street_name = street_match.group(2).strip()[:50]
        return number, f"{street_type} {street_name}"
    
    return number, addr.strip()[:50]

def generate_coordinates(address: str, address_hash: int) -> tuple:
    """Générer les coordonnées de manière déterministe"""
    number, street = extract_street_and_number(address)
    
    # Assigner une zone
    zone = get_zone_for_street(street)
    center_lat, center_lon, spread_lat, spread_lon = ZONES[zone]
    
    # Variation basée sur le hash de l'adresse
    lat_var = ((address_hash % 100) / 100 - 0.5) * spread_lat
    lon_var = (((address_hash // 100) % 100) / 100 - 0.5) * spread_lon
    
    # Variation supplémentaire basée sur le numéro
    num_var_lat = (number % 10) / 100 * spread_lat / 10
    num_var_lon = ((number // 10) % 10) / 100 * spread_lon / 10
    
    return (
        center_lat + lat_var + num_var_lat,
        center_lon + lon_var + num_var_lon
    )

def main():
    print("Chargement du CSV...")
    csv_path = "tractage-app/public/data/electeurs.csv"
    df = pd.read_csv(csv_path, sep=';')
    
    print(f"Total lignes: {len(df)}")
    
    # Générer les coordonnées
    print("Génération des coordonnées...")
    coords = []
    for idx, addr in enumerate(df['Adresse Complète']):
        if pd.isna(addr):
            coords.append((None, None))
        else:
            # Hash déterministe de l'adresse
            addr_hash = int(hashlib.md5(addr.encode()).hexdigest(), 16)
            lat, lon = generate_coordinates(addr, addr_hash)
            coords.append((lat, lon))
        
        if (idx + 1) % 10000 == 0:
            print(f"  Traité: {idx+1}/{len(df)}")
    
    # Ajouter les colonnes
    df['latitude'] = [c[0] for c in coords]
    df['longitude'] = [c[1] for c in coords]
    
    # Sauvegarder
    df.to_csv(csv_path, sep=';', index=False)
    
    # Statistiques
    success = df['latitude'].notna().sum()
    
    print(f"\n✓ Géocodage terminé:")
    print(f"  Adresses avec coordonnées: {success}/{len(df)}")
    print(f"  Fichier sauvegardé: {csv_path}")
    
    # Exemples
    print(f"\nExemples:")
    for _, row in df[df['latitude'].notna()].sample(min(5, len(df))).iterrows():
        addr = row['Adresse Complète']
        num, street = extract_street_and_number(addr)
        zone = get_zone_for_street(street)
        print(f"  {addr}")
        print(f"    Rue: {street} | Zone: {zone}")
        print(f"    GPS: {row['latitude']:.4f}, {row['longitude']:.4f}\n")

if __name__ == "__main__":
    main()

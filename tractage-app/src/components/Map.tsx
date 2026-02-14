'use client';

import { useEffect, useRef, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { Foyer } from '@/types';
import 'leaflet/dist/leaflet.css';

interface MapComponentProps {
  foyers: Foyer[];
  selectedFoyer: Foyer | null;
  onSelectFoyer: (foyer: Foyer) => void;
}

// Composant pour centrer la carte sur le foyer sélectionné
function MapController({ selectedFoyer }: { selectedFoyer: Foyer | null }) {
  const map = useMap();
  
  useEffect(() => {
    if (selectedFoyer && selectedFoyer.lat && selectedFoyer.lon) {
      map.setView([selectedFoyer.lat, selectedFoyer.lon], 16);
    }
  }, [selectedFoyer, map]);
  
  return null;
}

export default function MapComponent({ foyers, selectedFoyer, onSelectFoyer }: MapComponentProps) {
  // Centre sur Les Sables d'Olonne
  const defaultCenter: [number, number] = [46.4959, -1.7842];
  const defaultZoom = 13;

  // Utiliser les coordonnées du CSV ou les valeurs par défaut
  const foyersWithCoords = useMemo(() => 
    foyers.map((foyer) => {
      // Les coordonnées sont déjà dans le foyer depuis le CSV
      return foyer;
    }),
    [foyers]
  );

  return (
    <MapContainer
      key={`map-${foyers.length}`}
      center={defaultCenter}
      zoom={defaultZoom}
      className="h-full w-full"
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      <MapController selectedFoyer={selectedFoyer} />
      
      {foyersWithCoords.map((foyer, index) => {
        if (!foyer.lat || !foyer.lon) return null;
        
        const isSelected = selectedFoyer?.adresse === foyer.adresse;
        const radius = isSelected ? 10 : Math.min(5 + foyer.nbElecteurs, 15);
        
        return (
          <CircleMarker
            key={`${foyer.adresse}-${index}`}
            center={[foyer.lat, foyer.lon]}
            radius={radius}
            pathOptions={{
              fillColor: foyer.couleur,
              fillOpacity: isSelected ? 0.9 : 0.6,
              color: isSelected ? '#1e40af' : '#fff',
              weight: isSelected ? 3 : 1,
            }}
            eventHandlers={{
              click: () => onSelectFoyer(foyer),
            }}
          >
            <Popup>
              <div className="p-2">
                <p className="font-semibold text-sm mb-1">{foyer.adresse}</p>
                <p className="text-xs text-gray-600">
                  {foyer.nbElecteurs} électeur{foyer.nbElecteurs > 1 ? 's' : ''}
                </p>
                <p className="text-xs text-gray-600">
                  Âge moyen: {Math.round(foyer.ageMoyen)} ans
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {foyer.segmentDominant}
                </p>
                <button
                  onClick={() => onSelectFoyer(foyer)}
                  className="mt-2 w-full px-2 py-1 bg-primary-600 text-white text-xs rounded hover:bg-primary-700"
                >
                  Voir détails
                </button>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}

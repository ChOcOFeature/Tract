'use client';

import { useState, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Search, Users, MapPin } from 'lucide-react';
import Papa from 'papaparse';
import { Foyer, Electeur, getSegmentKey, SEGMENTS } from '@/types';

const MapComponent = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => <div className="h-full w-full bg-gray-200 animate-pulse flex items-center justify-center">Chargement de la carte...</div>
});

export default function TractageApp() {
  const [foyers, setFoyers] = useState<Foyer[]>([]);
  const [selectedFoyer, setSelectedFoyer] = useState<Foyer | null>(null);
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [filterSegment, setFilterSegment] = useState<string>('all');
  const [visibleCount, setVisibleCount] = useState(200);

  // Charger les données au montage
  useEffect(() => {
    loadCSVData();
  }, []);

  // Debounce de la recherche pour limiter les recalculs
  useEffect(() => {
    const handle = setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
    }, 500);

    return () => clearTimeout(handle);
  }, [searchInput]);

  useEffect(() => {
    setVisibleCount(200);
  }, [debouncedSearch, filterSegment]);

  const loadCSVData = async () => {
    try {
      const response = await fetch('/data/electeurs.csv');
      const csvText = await response.text();
      
      Papa.parse(csvText, {
        header: true,
        delimiter: ';',
        complete: (results) => {
          processData(results.data as any[]);
        },
        error: (error: any) => {
          console.error('Erreur de parsing:', error);
          setLoading(false);
        }
      });
    } catch (error) {
      console.error('Erreur lors du chargement du fichier:', error);
      setLoading(false);
    }
  };

  const processData = (data: any[]) => {
    const foyersMap = new Map<string, Foyer>();

    data.forEach((row) => {
      if (!row['Adresse Complète']) return;

      const adresse = row['Adresse Complète'];
      const electeur: Electeur = {
        nom: row['Nom'] || '',
        prenoms: row['Prénoms'] || '',
        age: parseInt(row['Âge']) || 0,
        sexe: row['Sexe'] as 'M' | 'F',
        segment: row['Segment'] || '',
        natifVendee: row['Natif Vendée'] === 'True' || row['Natif Vendée'] === 'TRUE',
        adresse: adresse,
        rue: row['Adresse Complète'] || '',
        numeroVoie: '',
        codePostal: '',
        commune: '',
        codeBureau: row['Code Bureau'] || '',
        libelleBureau: row['Bureau de Vote'] || '',
      };

      if (!foyersMap.has(adresse)) {
        const segmentKey = getSegmentKey(electeur.segment);
        foyersMap.set(adresse, {
          adresse,
          adresseGoogleMaps: adresse,
          nbElecteurs: 0,
          ageMoyen: 0,
          segmentDominant: electeur.segment,
          electeurs: [],
          scorePriorite: 0,
          couleur: SEGMENTS[segmentKey]?.couleur || '#6b7280',
          lat: parseFloat(row['latitude']) || undefined,
          lon: parseFloat(row['longitude']) || undefined,
        });
      }

      const foyer = foyersMap.get(adresse)!;
      foyer.electeurs.push(electeur);
      foyer.nbElecteurs++;
    });

    // Calculer les moyennes
    const foyersList = Array.from(foyersMap.values()).map(foyer => {
      foyer.ageMoyen = foyer.electeurs.reduce((sum, e) => sum + e.age, 0) / foyer.nbElecteurs;
      foyer.scorePriorite = foyer.nbElecteurs * 20 + (50 - Math.abs(foyer.ageMoyen - 45)) * 2;
      
      // Trouver le segment dominant
      const segmentCounts = new Map<string, number>();
      foyer.electeurs.forEach(e => {
        segmentCounts.set(e.segment, (segmentCounts.get(e.segment) || 0) + 1);
      });
      const dominantSegment = Array.from(segmentCounts.entries())
        .sort((a, b) => b[1] - a[1])[0]?.[0] || '';
      foyer.segmentDominant = dominantSegment;
      
      const segmentKey = getSegmentKey(dominantSegment);
      foyer.couleur = SEGMENTS[segmentKey]?.couleur || '#6b7280';
      
      return foyer;
    });

    setFoyers(foyersList.sort((a, b) => b.scorePriorite - a.scorePriorite));
    setLoading(false);
  };

  const foyersSearchIndex = useMemo(() => {
    return foyers.map((foyer) => {
      const electeursText = foyer.electeurs
        .map((e) => `${e.nom} ${e.prenoms}`)
        .join(' ');

      return {
        foyer,
        searchText: `${foyer.adresse} ${electeursText}`.toLowerCase(),
      };
    });
  }, [foyers]);

  const filteredFoyers = useMemo(() => {
    const searchLower = debouncedSearch.toLowerCase();

    return foyersSearchIndex
      .filter(({ foyer, searchText }) => {
        const matchesSearch = searchLower === '' || searchText.includes(searchLower);
        const matchesSegment = filterSegment === 'all' || foyer.segmentDominant === filterSegment;
        return matchesSearch && matchesSegment;
      })
      .map(({ foyer }) => foyer);
  }, [foyersSearchIndex, debouncedSearch, filterSegment]);

  const visibleFoyers = useMemo(() => {
    return filteredFoyers.slice(0, visibleCount);
  }, [filteredFoyers, visibleCount]);

  const uniqueSegments = Array.from(new Set(foyers.map(f => f.segmentDominant))).filter(Boolean);

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="bg-primary-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <MapPin className="w-8 h-8" />
            Tractage Electoral - Les Sables d'Olonne
          </h1>
          <p className="text-primary-100 text-sm mt-1">
            Outil interactif de gestion de campagne électorale
          </p>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <aside className="w-96 bg-white border-r border-gray-200 flex flex-col overflow-hidden">
          {/* Status Section */}
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            {loading ? (
              <div className="text-center">
                <div className="animate-spin inline-block w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full"></div>
                <p className="text-sm text-gray-600 mt-2">Chargement des données...</p>
              </div>
            ) : foyers.length > 0 ? (
              <p className="text-sm text-gray-600 text-center font-medium">
                ✓ {foyers.length} foyers • {foyers.reduce((sum, f) => sum + f.nbElecteurs, 0)} électeurs
              </p>
            ) : (
              <p className="text-sm text-red-600 text-center">Erreur lors du chargement</p>
            )}
          </div>

          {foyers.length > 0 && (
            <>
              {/* Search & Filters */}
              <div className="p-4 space-y-3 border-b border-gray-200">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Rechercher une adresse ou un nom..."
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                
                <select
                  value={filterSegment}
                  onChange={(e) => setFilterSegment(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="all">Tous les segments</option>
                  {uniqueSegments.map(segment => (
                    <option key={segment} value={segment}>{segment}</option>
                  ))}
                </select>
              </div>

              {/* Foyers List */}
              <div className="flex-1 overflow-y-auto">
                {filteredFoyers.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    Aucun résultat
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {visibleFoyers.map((foyer, index) => (
                      <button
                        key={index}
                        onClick={() => setSelectedFoyer(foyer)}
                        className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                          selectedFoyer?.adresse === foyer.adresse ? 'bg-primary-50 border-l-4 border-primary-600' : ''
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0"
                            style={{ backgroundColor: foyer.couleur }}
                          >
                            {foyer.nbElecteurs}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 truncate">{foyer.adresse}</p>
                            <p className="text-sm text-gray-600 mt-1">
                              {foyer.nbElecteurs} électeur{foyer.nbElecteurs > 1 ? 's' : ''} • 
                              Âge moyen: {Math.round(foyer.ageMoyen)} ans
                            </p>
                            <p className="text-xs text-gray-500 mt-1 truncate">
                              {foyer.segmentDominant}
                            </p>
                          </div>
                        </div>
                      </button>
                    ))}
                    {visibleFoyers.length < filteredFoyers.length && (
                      <div className="p-4">
                        <button
                          onClick={() => setVisibleCount((count) => count + 200)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                        >
                          Afficher plus ({Math.min(200, filteredFoyers.length - visibleFoyers.length)})
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </>
          )}

          {foyers.length === 0 && !loading && (
            <div className="flex-1 flex items-center justify-center p-8 text-center">
              <div>
                <Users className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Erreur lors du chargement
                </h3>
                <p className="text-sm text-gray-500">
                  Les données n'ont pas pu être chargées.
                </p>
              </div>
            </div>
          )}
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Map */}
          <div className="flex-1">
            <MapComponent 
              foyers={selectedFoyer ? [selectedFoyer] : []}
              selectedFoyer={selectedFoyer}
              onSelectFoyer={setSelectedFoyer}
            />
          </div>

          {/* Details Panel */}
          {selectedFoyer && (
            <div className="h-80 border-t border-gray-200 bg-white overflow-y-auto">
              <DetailPanel foyer={selectedFoyer} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

function DetailPanel({ foyer }: { foyer: Foyer }) {
  const segmentKey = getSegmentKey(foyer.segmentDominant);
  const segmentInfo = SEGMENTS[segmentKey];
  const [messageType, setMessageType] = useState<'court' | 'moyen' | 'long'>('moyen');

  if (!segmentInfo) return null;

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div
            className="w-12 h-12 rounded-full flex items-center justify-center text-white text-xl font-bold"
            style={{ backgroundColor: foyer.couleur }}
          >
            {segmentInfo.emoji}
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">{foyer.adresse}</h2>
            <p className="text-sm text-gray-600">
              {foyer.nbElecteurs} électeur{foyer.nbElecteurs > 1 ? 's' : ''} • 
              Âge moyen: {Math.round(foyer.ageMoyen)} ans
            </p>
          </div>
        </div>

        {/* Electeurs list */}
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <h3 className="font-semibold text-gray-900 mb-2">Électeurs du foyer:</h3>
          <div className="space-y-2">
            {foyer.electeurs.map((electeur, idx) => (
              <div key={idx} className="flex items-center justify-between text-sm">
                <span className="font-medium">
                  {electeur.prenoms} {electeur.nom}
                </span>
                <span className="text-gray-600">
                  {electeur.age} ans • {electeur.sexe} {electeur.natifVendee && '🏠'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Segment Info */}
      <div className="border-t pt-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900">
            {segmentInfo.emoji} {segmentInfo.titre}
          </h3>
          <div className="flex gap-2">
            <button
              onClick={() => setMessageType('court')}
              className={`px-3 py-1 rounded text-sm font-medium ${
                messageType === 'court' 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Court
            </button>
            <button
              onClick={() => setMessageType('moyen')}
              className={`px-3 py-1 rounded text-sm font-medium ${
                messageType === 'moyen' 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Moyen
            </button>
            <button
              onClick={() => setMessageType('long')}
              className={`px-3 py-1 rounded text-sm font-medium ${
                messageType === 'long' 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Long
            </button>
          </div>
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4">
          <p className="text-gray-800 leading-relaxed">
            {segmentInfo.messages[messageType]}
          </p>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          {segmentInfo.themes.map((theme) => (
            <span
              key={theme}
              className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium"
            >
              {theme}
            </span>
          ))}
        </div>

        <button
          onClick={() => {
            navigator.clipboard.writeText(segmentInfo.messages[messageType]);
            alert('Message copié dans le presse-papier !');
          }}
          className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
        >
          📋 Copier le message
        </button>
      </div>
    </div>
  );
}

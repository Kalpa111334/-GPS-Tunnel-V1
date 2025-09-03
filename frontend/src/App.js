import React, { useState, useEffect, useCallback, useRef } from 'react';
import './App.css';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card } from './components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { MapPin, Navigation, Play, Pause, Volume2, VolumeX, Map } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const GOOGLE_MAPS_API_KEY = 'AIzaSyARSoKujCNX2odk8wachQyz0DIjBCqJNd4';

// Language configurations
const LANGUAGES = {
  en: { name: 'English', flag: '🇬🇧' },
  nl: { name: 'Nederlands', flag: '🇳🇱' },
  si: { name: 'සිංහල', flag: '🇱🇰' },
  ta: { name: 'தமிழ்', flag: '🇱🇰' },
  ja: { name: '日本語', flag: '🇯🇵' },
  zh: { name: '中文', flag: '🇨🇳' }
};

function App() {
  // State management
  const [currentLocation, setCurrentLocation] = useState(null);
  const [tourRoutes, setTourRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [tourSession, setTourSession] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentContent, setCurrentContent] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [map, setMap] = useState(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  
  // Refs
  const mapRef = useRef(null);
  const speechUtteranceRef = useRef(null);
  const watchIdRef = useRef(null);
  const markersRef = useRef([]);
  const routePolylineRef = useRef(null);

  // Load Google Maps
  useEffect(() => {
    if (!window.google) {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=geometry`;
      script.async = true;
      script.onload = () => setMapLoaded(true);
      document.head.appendChild(script);
    } else {
      setMapLoaded(true);
    }
  }, []);

  // Initialize map when loaded
  useEffect(() => {
    if (mapLoaded && mapRef.current && !map) {
      const mapInstance = new window.google.maps.Map(mapRef.current, {
        center: { lat: 52.3791, lng: 4.9003 }, // Amsterdam Central Station
        zoom: 14,
        mapTypeId: 'roadmap',
        styles: [
          {
            featureType: 'water',
            elementType: 'geometry.fill',
            stylers: [{ color: '#006994' }]
          },
          {
            featureType: 'landscape',
            elementType: 'geometry.fill',
            stylers: [{ color: '#f5f5f5' }]
          }
        ]
      });
      setMap(mapInstance);
    }
  }, [mapLoaded, map]);

  // Fetch tour routes
  useEffect(() => {
    const fetchTourRoutes = async () => {
      try {
        const response = await axios.get(`${API}/tour-routes`);
        setTourRoutes(response.data);
        if (response.data.length > 0) {
          setSelectedRoute(response.data[0]);
        }
      } catch (error) {
        console.error('Error fetching tour routes:', error);
      }
    };

    fetchTourRoutes();
  }, []);

  // Start geolocation tracking
  const startLocationTracking = useCallback(() => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by this browser.');
      return;
    }

    const options = {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 0
    };

    watchIdRef.current = navigator.geolocation.watchPosition(
      (position) => {
        const newLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: new Date().toISOString()
        };
        
        setCurrentLocation(newLocation);
        
        // Update tour session location if active
        if (tourSession) {
          updateSessionLocation(newLocation);
        }

        // Center map on current location
        if (map) {
          map.setCenter({ 
            lat: newLocation.latitude, 
            lng: newLocation.longitude 
          });
        }
      },
      (error) => {
        console.error('Error getting location:', error);
        alert('Unable to retrieve your location. Please enable location services.');
      },
      options
    );
  }, [map, tourSession]);

  // Update session location
  const updateSessionLocation = async (location) => {
    if (!tourSession) return;

    try {
      await axios.put(`${API}/tour-sessions/${tourSession.id}/location`, location);
      await fetchCurrentContent();
    } catch (error) {
      console.error('Error updating location:', error);
    }
  };

  // Fetch current tour content
  const fetchCurrentContent = async () => {
    if (!tourSession) return;

    try {
      const response = await axios.get(
        `${API}/tour-sessions/${tourSession.id}/current-content?language=${selectedLanguage}`
      );
      setCurrentContent(response.data);
      
      // Auto-play narration if playing
      if (isPlaying && response.data.audio_content && !isMuted) {
        speakText(response.data.audio_content);
      }
    } catch (error) {
      console.error('Error fetching current content:', error);
    }
  };

  // Text-to-speech functionality
  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      // Stop any current speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = selectedLanguage === 'zh' ? 'zh-CN' : selectedLanguage;
      utterance.rate = 0.9;
      utterance.pitch = 1;
      
      speechUtteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    }
  };

  // Stop speech
  const stopSpeech = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  };

  // Start tour
  const startTour = async () => {
    if (!selectedRoute || !currentLocation) {
      alert('Please select a route and enable location services first.');
      return;
    }

    setIsLoading(true);
    try {
      const sessionData = {
        route_id: selectedRoute.id,
        user_id: `user_${Date.now()}`,
        current_language: selectedLanguage
      };

      const response = await axios.post(`${API}/tour-sessions`, sessionData);
      setTourSession(response.data);
      setIsPlaying(true);
      
      // Load route points on map
      await loadRouteOnMap(selectedRoute.id);
      
      // Start location tracking
      startLocationTracking();
      
      // Fetch initial content
      setTimeout(() => fetchCurrentContent(), 1000);
      
    } catch (error) {
      console.error('Error starting tour:', error);
      alert('Error starting tour. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Load route on map
  const loadRouteOnMap = async (routeId) => {
    if (!map) return;

    try {
      const response = await axios.get(`${API}/tour-routes/${routeId}/points`);
      const points = response.data;

      // Clear existing markers
      markersRef.current.forEach(marker => marker.setMap(null));
      markersRef.current = [];

      // Add markers for each tour point
      points.forEach((point, index) => {
        const marker = new window.google.maps.Marker({
          position: { lat: point.latitude, lng: point.longitude },
          map: map,
          title: point.name,
          label: (index + 1).toString(),
          icon: {
            path: window.google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: '#2563eb',
            fillOpacity: 1,
            strokeColor: '#ffffff',
            strokeWeight: 2
          }
        });

        markersRef.current.push(marker);
      });

      // Create route polyline
      if (routePolylineRef.current) {
        routePolylineRef.current.setMap(null);
      }

      const routePath = points.map(point => ({
        lat: point.latitude,
        lng: point.longitude
      }));

      routePolylineRef.current = new window.google.maps.Polyline({
        path: routePath,
        geodesic: true,
        strokeColor: '#2563eb',
        strokeOpacity: 1.0,
        strokeWeight: 4
      });

      routePolylineRef.current.setMap(map);

      // Adjust map bounds to show all points
      const bounds = new window.google.maps.LatLngBounds();
      points.forEach(point => {
        bounds.extend({ lat: point.latitude, lng: point.longitude });
      });
      map.fitBounds(bounds);

    } catch (error) {
      console.error('Error loading route on map:', error);
    }
  };

  // Toggle play/pause
  const togglePlayPause = () => {
    if (isPlaying) {
      setIsPlaying(false);
      stopSpeech();
    } else {
      setIsPlaying(true);
      if (currentContent && currentContent.audio_content && !isMuted) {
        speakText(currentContent.audio_content);
      }
    }
  };

  // Toggle mute
  const toggleMute = () => {
    setIsMuted(!isMuted);
    if (!isMuted) {
      stopSpeech();
    } else if (isPlaying && currentContent && currentContent.audio_content) {
      speakText(currentContent.audio_content);
    }
  };

  // Get current location
  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date().toISOString()
          };
          setCurrentLocation(location);
          
          if (map) {
            map.setCenter({ 
              lat: location.latitude, 
              lng: location.longitude 
            });
            map.setZoom(16);
          }
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('Unable to get your current location. Please enable location services.');
        }
      );
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (watchIdRef.current) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
      stopSpeech();
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-lg border-b border-blue-100">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl flex items-center justify-center">
                <Navigation className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">GPS TUNNEL</h1>
                <p className="text-sm text-blue-600">Dining Boat Tour Navigation</p>
              </div>
            </div>
            
            {/* Language Selector */}
            <div className="flex items-center space-x-4">
              <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(LANGUAGES).map(([code, lang]) => (
                    <SelectItem key={code} value={code}>
                      <span className="flex items-center space-x-2">
                        <span>{lang.flag}</span>
                        <span>{lang.name}</span>
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Control Panel */}
          <div className="lg:col-span-1 space-y-6">
            {/* Tour Status */}
            <Card className="p-6 bg-white/70 backdrop-blur-sm border border-blue-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <MapPin className="w-5 h-5 mr-2 text-blue-600" />
                Tour Status
              </h3>
              
              {tourSession ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      Tour Active
                    </Badge>
                    {currentContent && (
                      <span className="text-sm text-gray-600">
                        {currentContent.progress} / {currentContent.total_points}
                      </span>
                    )}
                  </div>
                  
                  {currentContent && currentContent.point && (
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900">
                        {currentContent.point.name}
                      </h4>
                      <p className="text-sm text-blue-700 mt-1">
                        {currentContent.description}
                      </p>
                    </div>
                  )}
                  
                  {/* Controls */}
                  <div className="flex items-center space-x-2">
                    <Button
                      onClick={togglePlayPause}
                      variant={isPlaying ? "secondary" : "default"}
                      size="sm"
                    >
                      {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </Button>
                    
                    <Button
                      onClick={toggleMute}
                      variant={isMuted ? "destructive" : "outline"}
                      size="sm"
                    >
                      {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center space-y-4">
                  <p className="text-gray-600">Ready to start your dining boat tour adventure?</p>
                  
                  {/* Location Status */}
                  {currentLocation ? (
                    <div className="p-3 bg-green-50 rounded-lg">
                      <p className="text-sm text-green-800">
                        📍 Location detected
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="p-3 bg-amber-50 rounded-lg">
                        <p className="text-sm text-amber-800">
                          📍 Location needed for tour
                        </p>
                      </div>
                      <Button
                        onClick={getCurrentLocation}
                        variant="outline"
                        size="sm"
                        className="w-full"
                      >
                        <MapPin className="w-4 h-4 mr-2" />
                        Get My Location
                      </Button>
                    </div>
                  )}

                  <Button
                    onClick={startTour}
                    disabled={!currentLocation || isLoading}
                    className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
                  >
                    {isLoading ? 'Starting Tour...' : 'Start Tour'}
                  </Button>
                </div>
              )}
            </Card>

            {/* Route Information */}
            {selectedRoute && (
              <Card className="p-6 bg-white/70 backdrop-blur-sm border border-blue-100">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Map className="w-5 h-5 mr-2 text-blue-600" />
                  Tour Route
                </h3>
                <div>
                  <h4 className="font-medium text-gray-900">
                    {selectedRoute.name}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {selectedRoute.description[selectedLanguage] || selectedRoute.description.en}
                  </p>
                </div>
              </Card>
            )}
          </div>

          {/* Map */}
          <div className="lg:col-span-2">
            <Card className="p-2 bg-white/70 backdrop-blur-sm border border-blue-100">
              <div
                ref={mapRef}
                className="w-full h-[600px] rounded-lg"
                style={{ minHeight: '600px' }}
              />
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
import React, { useState, useEffect, useCallback, useRef } from 'react';
import './App.css';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card } from './components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Badge } from './components/ui/badge';
import { Input } from './components/ui/input';
import { Separator } from './components/ui/separator';
import { MapPin, Navigation, Play, Pause, Volume2, VolumeX, Map, Search, Target, Route, Compass } from 'lucide-react';

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
  zh: { name: '中文', flag: '🇨🇳' },
  es: { name: 'Español', flag: '🇪🇸' },
  fr: { name: 'Français', flag: '🇫🇷' },
  de: { name: 'Deutsch', flag: '🇩🇪' },
  it: { name: 'Italiano', flag: '🇮🇹' },
  pt: { name: 'Português', flag: '🇵🇹' },
  ru: { name: 'Русский', flag: '🇷🇺' }
};

function App() {
  // State management
  const [currentLocation, setCurrentLocation] = useState(null);
  const [destinationQuery, setDestinationQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState(null);
  const [currentRoute, setCurrentRoute] = useState(null);
  const [tourRoutes, setTourRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [tourSession, setTourSession] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentContent, setCurrentContent] = useState(null);
  const [currentInstructionIndex, setCurrentInstructionIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [map, setMap] = useState(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [isNavigating, setIsNavigating] = useState(false);
  
  // Refs
  const mapRef = useRef(null);
  const speechUtteranceRef = useRef(null);
  const watchIdRef = useRef(null);
  const markersRef = useRef([]);
  const routePolylineRef = useRef(null);
  const currentLocationMarkerRef = useRef(null);
  const destinationMarkerRef = useRef(null);

  // Load Google Maps
  useEffect(() => {
    if (!window.google) {
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=geometry,places`;
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
        
        // Update current location marker
        updateCurrentLocationMarker(newLocation);
        
        // Update tour session location if active
        if (tourSession) {
          updateSessionLocation(newLocation);
        }
      },
      (error) => {
        console.error('Error getting location:', error);
        alert('Unable to retrieve your location. Please enable location services.');
      },
      options
    );
  }, [map, tourSession]);

  // Update current location marker with animation
  const updateCurrentLocationMarker = (location) => {
    if (!map) return;

    const position = { lat: location.latitude, lng: location.longitude };

    if (currentLocationMarkerRef.current) {
      // Animate existing marker to new position
      currentLocationMarkerRef.current.setPosition(position);
    } else {
      // Create new animated current location marker
      currentLocationMarkerRef.current = new window.google.maps.Marker({
        position: position,
        map: map,
        title: 'Your Current Location',
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 12,
          fillColor: '#4285F4',
          fillOpacity: 1,
          strokeColor: '#ffffff',
          strokeWeight: 3,
          strokeOpacity: 1
        },
        animation: window.google.maps.Animation.BOUNCE
      });

      // Add pulsing circle around current location
      const accuracyCircle = new window.google.maps.Circle({
        strokeColor: '#4285F4',
        strokeOpacity: 0.3,
        strokeWeight: 2,
        fillColor: '#4285F4',
        fillOpacity: 0.1,
        map: map,
        center: position,
        radius: location.accuracy || 50
      });

      // Stop bouncing after 3 seconds
      setTimeout(() => {
        if (currentLocationMarkerRef.current) {
          currentLocationMarkerRef.current.setAnimation(null);
        }
      }, 3000);
    }

    // Center map on current location if not navigating
    if (!isNavigating) {
      map.setCenter(position);
    }
  };

  // Search for destinations
  const searchDestinations = async () => {
    if (!destinationQuery.trim()) return;

    setIsSearching(true);
    try {
      const searchParams = {
        query: destinationQuery,
        language: selectedLanguage
      };

      if (currentLocation) {
        searchParams.latitude = currentLocation.latitude;
        searchParams.longitude = currentLocation.longitude;
        searchParams.radius = 10000; // 10km radius
      }

      const response = await axios.post(`${API}/search/places`, searchParams);
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Error searching destinations:', error);
      alert('Failed to search destinations. Please try again.');
    } finally {
      setIsSearching(false);
    }
  };

  // Select destination from search results
  const selectDestination = (destination) => {
    setSelectedDestination(destination);
    setSearchResults([]);
    setDestinationQuery(destination.name);

    // Add destination marker to map
    if (map) {
      // Remove existing destination marker
      if (destinationMarkerRef.current) {
        destinationMarkerRef.current.setMap(null);
      }

      // Create new destination marker
      destinationMarkerRef.current = new window.google.maps.Marker({
        position: { lat: destination.latitude, lng: destination.longitude },
        map: map,
        title: destination.name,
        icon: {
          path: window.google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
          scale: 10,
          fillColor: '#EA4335',
          fillOpacity: 1,
          strokeColor: '#ffffff',
          strokeWeight: 2
        }
      });

      // Center map to show both current location and destination
      if (currentLocation) {
        const bounds = new window.google.maps.LatLngBounds();
        bounds.extend({ lat: currentLocation.latitude, lng: currentLocation.longitude });
        bounds.extend({ lat: destination.latitude, lng: destination.longitude });
        map.fitBounds(bounds, { padding: 50 });
      } else {
        map.setCenter({ lat: destination.latitude, lng: destination.longitude });
        map.setZoom(15);
      }
    }
  };

  // Calculate route to destination
  const calculateRoute = async () => {
    if (!currentLocation || !selectedDestination) {
      alert('Please select a destination and enable location services.');
      return;
    }

    setIsLoading(true);
    try {
      const routeRequest = {
        origin_lat: currentLocation.latitude,
        origin_lng: currentLocation.longitude,
        destination_lat: selectedDestination.latitude,
        destination_lng: selectedDestination.longitude,
        travel_mode: 'driving',
        language: selectedLanguage
      };

      const response = await axios.post(`${API}/directions/calculate`, routeRequest);
      setCurrentRoute(response.data);
      setIsNavigating(true);
      
      // Display route on map
      displayRouteOnMap(response.data);
      
      // Start navigation
      setCurrentInstructionIndex(0);
      setIsPlaying(true);
      
      // Start location tracking
      startLocationTracking();
      
      // Speak first instruction
      if (response.data.steps.length > 0 && !isMuted) {
        speakInstruction(response.data.steps[0].instruction);
      }
      
    } catch (error) {
      console.error('Error calculating route:', error);
      alert('Failed to calculate route. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Display route on map
  const displayRouteOnMap = (route) => {
    if (!map) return;

    // Clear existing route
    if (routePolylineRef.current) {
      routePolylineRef.current.setMap(null);
    }

    // Create route polyline
    const routePath = route.steps.map(step => [
      { lat: step.start_lat, lng: step.start_lng },
      { lat: step.end_lat, lng: step.end_lng }
    ]).flat();

    routePolylineRef.current = new window.google.maps.Polyline({
      path: routePath,
      geodesic: true,
      strokeColor: '#4285F4',
      strokeOpacity: 1.0,
      strokeWeight: 5
    });

    routePolylineRef.current.setMap(map);

    // Adjust map bounds to show entire route
    const bounds = new window.google.maps.LatLngBounds();
    bounds.extend({ lat: route.bounds.northeast.lat, lng: route.bounds.northeast.lng });
    bounds.extend({ lat: route.bounds.southwest.lat, lng: route.bounds.southwest.lng });
    map.fitBounds(bounds, { padding: 50 });

    // Add step markers
    route.steps.forEach((step, index) => {
      const stepMarker = new window.google.maps.Marker({
        position: { lat: step.start_lat, lng: step.start_lng },
        map: map,
        title: `Step ${index + 1}`,
        label: (index + 1).toString(),
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          scale: 6,
          fillColor: '#34A853',
          fillOpacity: 1,
          strokeColor: '#ffffff',
          strokeWeight: 1
        }
      });

      markersRef.current.push(stepMarker);
    });
  };

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

  // Speak navigation instruction
  const speakInstruction = (instruction) => {
    if (!isMuted) {
      // Clean HTML tags from instruction
      const cleanInstruction = instruction.replace(/<[^>]*>/g, '');
      speakText(cleanInstruction);
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
      if (currentRoute && currentRoute.steps.length > currentInstructionIndex && !isMuted) {
        speakInstruction(currentRoute.steps[currentInstructionIndex].instruction);
      } else if (currentContent && currentContent.audio_content && !isMuted) {
        speakText(currentContent.audio_content);
      }
    }
  };

  // Toggle mute
  const toggleMute = () => {
    setIsMuted(!isMuted);
    if (!isMuted) {
      stopSpeech();
    } else if (isPlaying) {
      if (currentRoute && currentRoute.steps.length > currentInstructionIndex) {
        speakInstruction(currentRoute.steps[currentInstructionIndex].instruction);
      } else if (currentContent && currentContent.audio_content) {
        speakText(currentContent.audio_content);
      }
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
          updateCurrentLocationMarker(location);
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('Unable to get your current location. Please enable location services.');
        }
      );
    }
  };

  // Handle Enter key in search
  const handleSearchKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchDestinations();
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
                <p className="text-sm text-blue-600">Turn-by-Turn Navigation & Dining Tours</p>
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
            {/* Destination Search */}
            <Card className="p-6 bg-white/70 backdrop-blur-sm border border-blue-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Search className="w-5 h-5 mr-2 text-blue-600" />
                Destination Search
              </h3>
              
              <div className="space-y-4">
                <div className="flex space-x-2">
                  <Input
                    placeholder="Search for restaurants, hotels, attractions..."
                    value={destinationQuery}
                    onChange={(e) => setDestinationQuery(e.target.value)}
                    onKeyPress={handleSearchKeyPress}
                    className="flex-1"
                  />
                  <Button 
                    onClick={searchDestinations}
                    disabled={isSearching || !destinationQuery.trim()}
                    size="sm"
                  >
                    {isSearching ? '...' : <Search className="w-4 h-4" />}
                  </Button>
                </div>

                {searchResults.length > 0 && (
                  <div className="max-h-64 overflow-y-auto space-y-2">
                    {searchResults.map((result, index) => (
                      <div
                        key={index}
                        onClick={() => selectDestination(result)}
                        className="p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-blue-50 transition-colors"
                      >
                        <div className="font-medium text-gray-900">{result.name}</div>
                        <div className="text-sm text-gray-600 truncate">{result.formatted_address}</div>
                        {result.rating && (
                          <div className="text-xs text-amber-600 mt-1">⭐ {result.rating}</div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {selectedDestination && (
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-blue-900">{selectedDestination.name}</h4>
                        <p className="text-sm text-blue-700 mt-1">{selectedDestination.formatted_address}</p>
                      </div>
                      <Target className="w-5 h-5 text-blue-600" />
                    </div>
                  </div>
                )}

                {currentLocation && selectedDestination && (
                  <Button
                    onClick={calculateRoute}
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800"
                  >
                    {isLoading ? 'Calculating Route...' : (
                      <>
                        <Route className="w-4 h-4 mr-2" />
                        Calculate Route
                      </>
                    )}
                  </Button>
                )}
              </div>
            </Card>

            {/* Navigation Status */}
            {currentRoute && (
              <Card className="p-6 bg-white/70 backdrop-blur-sm border border-blue-100">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Compass className="w-5 h-5 mr-2 text-green-600" />
                  Navigation Active
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      Navigating
                    </Badge>
                    <span className="text-sm text-gray-600">
                      {currentRoute.total_distance_text} • {currentRoute.total_duration_text}
                    </span>
                  </div>
                  
                  {currentRoute.steps[currentInstructionIndex] && (
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="font-medium text-green-900 mb-2">
                        Next: {currentRoute.steps[currentInstructionIndex].distance_text}
                      </div>
                      <div 
                        className="text-sm text-green-800"
                        dangerouslySetInnerHTML={{
                          __html: currentRoute.steps[currentInstructionIndex].instruction
                        }}
                      />
                    </div>
                  )}
                  
                  {/* Navigation Controls */}
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
              </Card>
            )}

            {/* Tour Status */}
            {!isNavigating && (
              <Card className="p-6 bg-white/70 backdrop-blur-sm border border-blue-100">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <MapPin className="w-5 h-5 mr-2 text-blue-600" />
                  Dining Tour
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
                      {isLoading ? 'Starting Tour...' : 'Start Dining Tour'}
                    </Button>
                  </div>
                )}
              </Card>
            )}

            {/* Route Information */}
            {selectedRoute && !isNavigating && (
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
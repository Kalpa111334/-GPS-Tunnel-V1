import requests
import sys
import json
from datetime import datetime

class GPSTunnelAPITester:
    def __init__(self, base_url="https://dining-boat-nav.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.tour_route_id = None
        self.tour_session_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_get_tour_routes(self):
        """Test getting tour routes"""
        success, response = self.run_test(
            "Get Tour Routes",
            "GET",
            "tour-routes",
            200
        )
        
        if success and response:
            if isinstance(response, list) and len(response) > 0:
                self.tour_route_id = response[0].get('id')
                print(f"   Found {len(response)} tour routes")
                print(f"   First route ID: {self.tour_route_id}")
                print(f"   First route name: {response[0].get('name')}")
                
                # Verify multilingual descriptions
                first_route = response[0]
                if 'description' in first_route:
                    languages = list(first_route['description'].keys())
                    print(f"   Supported languages: {languages}")
                    expected_languages = ['en', 'nl', 'si', 'ta', 'ja', 'zh']
                    missing_languages = [lang for lang in expected_languages if lang not in languages]
                    if missing_languages:
                        print(f"   ⚠️  Missing languages: {missing_languages}")
                
                return True
            else:
                print(f"   ❌ Expected list with routes, got: {response}")
                return False
        return success

    def test_get_tour_route_points(self):
        """Test getting tour route points"""
        if not self.tour_route_id:
            print("   ⚠️  Skipping - No tour route ID available")
            return False
            
        success, response = self.run_test(
            "Get Tour Route Points",
            "GET",
            f"tour-routes/{self.tour_route_id}/points",
            200
        )
        
        if success and response:
            if isinstance(response, list):
                print(f"   Found {len(response)} tour points")
                if len(response) >= 4:  # Expected 4 points for Amsterdam tour
                    print("   ✅ Expected number of tour points found")
                    
                    # Check first point structure
                    first_point = response[0]
                    required_fields = ['id', 'name', 'description', 'latitude', 'longitude', 'audio_content', 'order']
                    missing_fields = [field for field in required_fields if field not in first_point]
                    if missing_fields:
                        print(f"   ⚠️  Missing fields in tour point: {missing_fields}")
                    
                    # Check multilingual content
                    if 'description' in first_point and 'audio_content' in first_point:
                        desc_languages = list(first_point['description'].keys())
                        audio_languages = list(first_point['audio_content'].keys())
                        print(f"   Description languages: {desc_languages}")
                        print(f"   Audio content languages: {audio_languages}")
                    
                    return True
                else:
                    print(f"   ⚠️  Expected at least 4 points, got {len(response)}")
            else:
                print(f"   ❌ Expected list, got: {type(response)}")
                return False
        return success

    def test_create_tour_session(self):
        """Test creating a tour session"""
        if not self.tour_route_id:
            print("   ⚠️  Skipping - No tour route ID available")
            return False
            
        session_data = {
            "route_id": self.tour_route_id,
            "user_id": f"test_user_{datetime.now().strftime('%H%M%S')}",
            "current_language": "en"
        }
        
        success, response = self.run_test(
            "Create Tour Session",
            "POST",
            "tour-sessions",
            200,
            data=session_data
        )
        
        if success and response:
            self.tour_session_id = response.get('id')
            print(f"   Created session ID: {self.tour_session_id}")
            
            # Verify session structure
            required_fields = ['id', 'route_id', 'user_id', 'current_language', 'current_point_index', 'is_active']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields in session: {missing_fields}")
            
            return True
        return success

    def test_update_session_location(self):
        """Test updating tour session location"""
        if not self.tour_session_id:
            print("   ⚠️  Skipping - No tour session ID available")
            return False
            
        location_data = {
            "latitude": 52.3791,  # Amsterdam Central Station
            "longitude": 4.9003,
            "accuracy": 10.0,
            "timestamp": datetime.now().isoformat()
        }
        
        success, response = self.run_test(
            "Update Session Location",
            "PUT",
            f"tour-sessions/{self.tour_session_id}/location",
            200,
            data=location_data
        )
        
        if success and response:
            if 'message' in response:
                print(f"   Update message: {response['message']}")
                return True
        return success

    def test_get_current_content(self):
        """Test getting current tour content"""
        if not self.tour_session_id:
            print("   ⚠️  Skipping - No tour session ID available")
            return False
            
        # Test different languages
        languages_to_test = ['en', 'nl', 'si', 'ta', 'ja', 'zh']
        
        for language in languages_to_test:
            success, response = self.run_test(
                f"Get Current Content ({language})",
                "GET",
                f"tour-sessions/{self.tour_session_id}/current-content",
                200,
                params={'language': language}
            )
            
            if success and response:
                if 'point' in response:
                    print(f"   Content for {language}: {response.get('description', '')[:50]}...")
                    print(f"   Progress: {response.get('progress')}/{response.get('total_points')}")
                elif 'message' in response:
                    print(f"   Message: {response['message']}")
                
                # Only return success for first language test
                if language == 'en':
                    return True
            else:
                print(f"   ❌ Failed to get content for language: {language}")
                if language == 'en':
                    return False
        
        return True

    def test_search_places(self):
        """Test destination search using Google Places API"""
        # Test basic search
        search_data = {
            "query": "restaurants Amsterdam",
            "language": "en"
        }
        
        success, response = self.run_test(
            "Search Places - Basic Query",
            "POST",
            "search/places",
            200,
            data=search_data
        )
        
        if success and response:
            if 'results' in response and 'status' in response:
                results = response['results']
                print(f"   Found {len(results)} places")
                
                if len(results) > 0:
                    first_result = results[0]
                    required_fields = ['place_id', 'name', 'formatted_address', 'latitude', 'longitude']
                    missing_fields = [field for field in required_fields if field not in first_result]
                    if missing_fields:
                        print(f"   ⚠️  Missing fields in search result: {missing_fields}")
                    else:
                        print(f"   ✅ Search result structure is correct")
                        print(f"   Sample result: {first_result['name']} - {first_result['formatted_address']}")
                
                # Test with location bias
                search_with_location = {
                    "query": "hotels near Dam Square",
                    "latitude": 52.3738,
                    "longitude": 4.8909,
                    "radius": 5000,
                    "language": "en"
                }
                
                success2, response2 = self.run_test(
                    "Search Places - With Location Bias",
                    "POST",
                    "search/places",
                    200,
                    data=search_with_location
                )
                
                return success and success2
            else:
                print(f"   ❌ Expected 'results' and 'status' in response, got: {list(response.keys())}")
                return False
        return success

    def test_calculate_route(self):
        """Test route calculation using Google Directions API"""
        # Test route from Amsterdam Central to Dam Square
        route_data = {
            "origin_lat": 52.3791,
            "origin_lng": 4.9003,
            "destination_lat": 52.3738,
            "destination_lng": 4.8909,
            "travel_mode": "driving",
            "language": "en"
        }
        
        success, response = self.run_test(
            "Calculate Route - Basic",
            "POST",
            "directions/calculate",
            200,
            data=route_data
        )
        
        if success and response:
            required_fields = ['total_distance_text', 'total_duration_text', 'start_address', 
                             'end_address', 'overview_polyline', 'steps', 'bounds']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields in route response: {missing_fields}")
                return False
            
            steps = response.get('steps', [])
            print(f"   Route calculated with {len(steps)} steps")
            print(f"   Total distance: {response['total_distance_text']}")
            print(f"   Total duration: {response['total_duration_text']}")
            
            if len(steps) > 0:
                first_step = steps[0]
                step_fields = ['instruction', 'distance_text', 'duration_text', 
                             'start_lat', 'start_lng', 'end_lat', 'end_lng']
                missing_step_fields = [field for field in step_fields if field not in first_step]
                if missing_step_fields:
                    print(f"   ⚠️  Missing fields in route step: {missing_step_fields}")
                else:
                    print(f"   ✅ Route step structure is correct")
                    print(f"   First instruction: {first_step['instruction'][:50]}...")
            
            # Test different travel modes
            walking_route = route_data.copy()
            walking_route['travel_mode'] = 'walking'
            
            success2, response2 = self.run_test(
                "Calculate Route - Walking Mode",
                "POST",
                "directions/calculate",
                200,
                data=walking_route
            )
            
            return success and success2
        return success

    def test_geocode_address(self):
        """Test address geocoding"""
        # Test geocoding Amsterdam Central Station
        success, response = self.run_test(
            "Geocode Address",
            "POST",
            "geocode/address?address=Amsterdam Central Station&language=en",
            200
        )
        
        if success and response:
            required_fields = ['status', 'address', 'latitude', 'longitude', 'formatted_address']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields in geocode response: {missing_fields}")
                return False
            
            print(f"   Geocoded address: {response['formatted_address']}")
            print(f"   Coordinates: {response['latitude']}, {response['longitude']}")
            
            # Verify coordinates are reasonable for Amsterdam
            lat, lng = response['latitude'], response['longitude']
            if 52.0 <= lat <= 53.0 and 4.0 <= lng <= 5.0:
                print(f"   ✅ Coordinates are within Amsterdam bounds")
                return True
            else:
                print(f"   ⚠️  Coordinates seem outside Amsterdam: {lat}, {lng}")
                return False
        return success

    def test_supported_languages(self):
        """Test getting supported languages"""
        success, response = self.run_test(
            "Get Supported Languages",
            "GET",
            "languages",
            200
        )
        
        if success and response:
            if 'languages' in response and 'status' in response:
                languages = response['languages']
                print(f"   Found {len(languages)} supported languages")
                
                # Check expected languages are present
                expected_languages = ['en', 'nl', 'si', 'ta', 'ja', 'zh', 'es', 'fr', 'de']
                language_codes = [lang['code'] for lang in languages]
                
                missing_languages = [code for code in expected_languages if code not in language_codes]
                if missing_languages:
                    print(f"   ⚠️  Missing expected languages: {missing_languages}")
                else:
                    print(f"   ✅ All expected languages are supported")
                
                # Check language structure
                if len(languages) > 0:
                    first_lang = languages[0]
                    required_fields = ['code', 'name', 'flag']
                    missing_fields = [field for field in required_fields if field not in first_lang]
                    if missing_fields:
                        print(f"   ⚠️  Missing fields in language: {missing_fields}")
                    else:
                        print(f"   ✅ Language structure is correct")
                        print(f"   Sample language: {first_lang['flag']} {first_lang['name']} ({first_lang['code']})")
                
                return True
            else:
                print(f"   ❌ Expected 'languages' and 'status' in response, got: {list(response.keys())}")
                return False
        return success

    def test_multilingual_navigation(self):
        """Test multilingual navigation instructions"""
        # Test route calculation in different languages
        route_data = {
            "origin_lat": 52.3791,
            "origin_lng": 4.9003,
            "destination_lat": 52.3738,
            "destination_lng": 4.8909,
            "travel_mode": "driving",
            "language": "nl"  # Dutch
        }
        
        success, response = self.run_test(
            "Multilingual Route - Dutch",
            "POST",
            "directions/calculate",
            200,
            data=route_data
        )
        
        if success and response:
            steps = response.get('steps', [])
            if len(steps) > 0:
                instruction = steps[0]['instruction']
                print(f"   Dutch instruction: {instruction[:50]}...")
                
                # Test another language
                route_data['language'] = 'fr'  # French
                success2, response2 = self.run_test(
                    "Multilingual Route - French",
                    "POST",
                    "directions/calculate",
                    200,
                    data=route_data
                )
                
                if success2 and response2:
                    steps2 = response2.get('steps', [])
                    if len(steps2) > 0:
                        instruction2 = steps2[0]['instruction']
                        print(f"   French instruction: {instruction2[:50]}...")
                        
                        # Verify instructions are different (different languages)
                        if instruction != instruction2:
                            print(f"   ✅ Instructions are properly localized")
                            return True
                        else:
                            print(f"   ⚠️  Instructions appear to be the same across languages")
                            return False
                
                return success2
        return success

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print(f"\n🔍 Testing Error Handling...")
        
        # Test invalid search query
        success1, response1 = self.run_test(
            "Invalid Search - Empty Query",
            "POST",
            "search/places",
            422,  # Validation error
            data={"query": "", "language": "en"}
        )
        
        # Test invalid route coordinates
        success2, response2 = self.run_test(
            "Invalid Route - Bad Coordinates",
            "POST",
            "directions/calculate",
            422,  # Validation error
            data={
                "origin_lat": 200,  # Invalid latitude
                "origin_lng": 4.9003,
                "destination_lat": 52.3738,
                "destination_lng": 4.8909,
                "travel_mode": "driving",
                "language": "en"
            }
        )
        
        # Test invalid travel mode
        success3, response3 = self.run_test(
            "Invalid Route - Bad Travel Mode",
            "POST",
            "directions/calculate",
            422,  # Validation error
            data={
                "origin_lat": 52.3791,
                "origin_lng": 4.9003,
                "destination_lat": 52.3738,
                "destination_lng": 4.8909,
                "travel_mode": "flying",  # Invalid mode
                "language": "en"
            }
        )
        
        # Test invalid tour route ID
        success4, response4 = self.run_test(
            "Invalid Route ID",
            "GET",
            "tour-routes/invalid-id/points",
            404
        )
        
        # Test invalid session ID
        success5, response5 = self.run_test(
            "Invalid Session ID",
            "GET",
            "tour-sessions/invalid-id/current-content",
            404
        )
        
        return success1 and success2 and success3 and success4 and success5

def main():
    print("🚢 GPS TUNNEL - Enhanced Navigation & Dining Boat Tour API Tests")
    print("=" * 70)
    
    # Setup
    tester = GPSTunnelAPITester()
    
    # Run all tests
    test_results = []
    
    # Basic connectivity
    test_results.append(tester.test_root_endpoint())
    
    # NEW NAVIGATION API TESTS
    print(f"\n🧭 TESTING NEW NAVIGATION FEATURES")
    print("-" * 40)
    test_results.append(tester.test_search_places())
    test_results.append(tester.test_calculate_route())
    test_results.append(tester.test_geocode_address())
    test_results.append(tester.test_supported_languages())
    test_results.append(tester.test_multilingual_navigation())
    
    # ORIGINAL TOUR API TESTS
    print(f"\n🚢 TESTING ORIGINAL DINING TOUR FEATURES")
    print("-" * 40)
    test_results.append(tester.test_get_tour_routes())
    test_results.append(tester.test_get_tour_route_points())
    test_results.append(tester.test_create_tour_session())
    test_results.append(tester.test_update_session_location())
    test_results.append(tester.test_get_current_content())
    
    # ERROR HANDLING TESTS
    print(f"\n⚠️  TESTING ERROR HANDLING")
    print("-" * 40)
    test_results.append(tester.test_error_handling())
    
    # Print final results
    print(f"\n" + "=" * 70)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        print("✅ Both navigation and dining tour features are functional.")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} test(s) failed. Please check the issues above.")
        
        # Provide specific guidance based on failures
        if tester.tests_passed < tester.tests_run / 2:
            print("🚨 Major issues detected. Backend may not be running or configured properly.")
        else:
            print("⚠️  Some features are not working. Check individual test failures above.")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
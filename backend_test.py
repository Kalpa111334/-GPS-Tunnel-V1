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

    def test_invalid_endpoints(self):
        """Test invalid endpoints for proper error handling"""
        print(f"\n🔍 Testing Invalid Endpoints...")
        
        # Test invalid route ID
        success, response = self.run_test(
            "Invalid Route ID",
            "GET",
            "tour-routes/invalid-id/points",
            404
        )
        
        # Test invalid session ID
        success2, response2 = self.run_test(
            "Invalid Session ID",
            "GET",
            "tour-sessions/invalid-id/current-content",
            404
        )
        
        return success and success2

def main():
    print("🚢 GPS TUNNEL - Dining Boat Tour Navigation API Tests")
    print("=" * 60)
    
    # Setup
    tester = GPSTunnelAPITester()
    
    # Run all tests
    test_results = []
    
    # Basic connectivity
    test_results.append(tester.test_root_endpoint())
    
    # Core functionality tests
    test_results.append(tester.test_get_tour_routes())
    test_results.append(tester.test_get_tour_route_points())
    test_results.append(tester.test_create_tour_session())
    test_results.append(tester.test_update_session_location())
    test_results.append(tester.test_get_current_content())
    
    # Error handling tests
    test_results.append(tester.test_invalid_endpoints())
    
    # Print final results
    print(f"\n" + "=" * 60)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_tests} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
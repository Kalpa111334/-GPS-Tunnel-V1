from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models for GPS Tunnel App
class TourPoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Dict[str, str] = {}  # multilingual descriptions
    latitude: float
    longitude: float
    trigger_radius: float = 50.0  # meters
    audio_content: Dict[str, str] = {}  # multilingual audio content
    order: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TourPointCreate(BaseModel):
    name: str
    description: Dict[str, str] = {}
    latitude: float
    longitude: float
    trigger_radius: float = 50.0
    audio_content: Dict[str, str] = {}
    order: int

class TourRoute(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Dict[str, str] = {}
    tour_points: List[str] = []  # list of tour point IDs
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TourRouteCreate(BaseModel):
    name: str
    description: Dict[str, str] = {}
    tour_points: List[str] = []
    is_active: bool = True

class UserLocation(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TourSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    route_id: str
    user_id: str
    current_language: str = "en"
    current_point_index: int = 0
    is_active: bool = True
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_location: Optional[UserLocation] = None

class TourSessionCreate(BaseModel):
    route_id: str
    user_id: str
    current_language: str = "en"

# Initialize sample data
async def init_sample_data():
    # Check if sample data already exists
    existing_routes = await db.tour_routes.count_documents({})
    if existing_routes > 0:
        return
    
    # Sample Amsterdam canal tour route
    sample_points = [
        {
            "name": "Central Station Departure",
            "description": {
                "en": "Welcome aboard! We're starting our magical dining boat tour from Amsterdam Central Station.",
                "nl": "Welkom aan boord! We beginnen onze magische eetboot tour vanaf Amsterdam Centraal Station.",
                "si": "ස්වාගතම්! අපි ඇම්ස්ටර්ඩෑම් මධ්‍යම දුම්රිය ස්ථානයෙන් අපගේ ආහාර නෞකා චාරිකාව ආරම්භ කරමු.",
                "ta": "வரவேற்கிறோம்! ஆம்ஸ்டர்டாம் மத்திய நிலையத்திலிருந்து எங்கள் மந்திர உணவு படகு பயணத்தை தொடங்குகிறோம்.",
                "ja": "ようこそ！アムステルダム中央駅から魔法のダイニングボートツアーを始めます。",
                "zh": "欢迎登船！我们从阿姆斯特丹中央车站开始神奇的餐船之旅。"
            },
            "latitude": 52.3791,
            "longitude": 4.9003,
            "trigger_radius": 100.0,
            "audio_content": {
                "en": "Welcome to GPS Tunnel's magical dining boat experience! As we depart from Amsterdam Central Station, you'll notice the beautiful historic architecture surrounding us.",
                "nl": "Welkom bij GPS Tunnel's magische eetboot ervaring! Terwijl we vertrekken vanaf Amsterdam Centraal Station, zult u de prachtige historische architectuur om ons heen opmerken.",
                "si": "GPS Tunnel හි ආශ්චර්යමත් ආහාර නෞකා අත්දැකීමට සාදරයෙන් පිළිගනිමු! අපි ඇම්ස්ටර්ඩෑම් මධ්‍යම දුම්රිය ස්ථානයෙන් පිටත්වන විට, අප වටා ඇති සුන්දර ඓතිහාසික ගෘහනිර්මාණ ශිල්පය ඔබට පෙනෙනු ඇත.",
                "ta": "GPS டன்னலின் மந்திர உணவு படகு அனுபவத்திற்கு வரவேற்கிறோம்! ஆம்ஸ்டர்டாம் மத்திய நிலையத்திலிருந்து புறப்படும்போது, எங்களைச் சுற்றியுள்ள அழகான வரலாற்று கட்டிடக்கலையை நீங்கள் கவனிப்பீர்கள்.",
                "ja": "GPS トンネルの魔法のダイニングボート体験へようこそ！アムステルダム中央駅から出発する際、私たちの周りの美しい歴史的建築物にお気づきでしょう。",
                "zh": "欢迎来到GPS隧道的神奇餐船体验！当我们从阿姆斯特丹中央车站出发时，您会注意到我们周围美丽的历史建筑。"
            },
            "order": 1
        },
        {
            "name": "Jordaan District",
            "description": {
                "en": "We're now entering the charming Jordaan district, known for its narrow streets and cozy cafes.",
                "nl": "We betreden nu de charmante wijk Jordaan, bekend om zijn smalle straatjes en gezellige cafés.",
                "si": "අපි දැන් ජෝර්ඩාන් ප්‍රදේශයට ඇතුළු වෙමු, එය පටු වීදි සහ සුහද කැෆේ සඳහා ප්‍රසිද්ධය.",
                "ta": "இப்போது நாங்கள் அழகான ஜோர்டான் மாவட்டத்தில் நுழைகிறோம், இது குறுகிய தெருக்கள் மற்றும் வசதியான கஃபேக்களுக்கு பிரபலமானது.",
                "ja": "私たちは今、狭い通りと居心地の良いカフェで知られる魅力的なヨルダン地区に入っています。",
                "zh": "我们现在进入迷人的约旦区，以其狭窄的街道和舒适的咖啡馆而闻名。"
            },
            "latitude": 52.3738,
            "longitude": 4.8830,
            "trigger_radius": 75.0,
            "audio_content": {
                "en": "As we glide through the Jordaan district, notice the beautiful houseboats lining the canals. This area was once home to many artists and musicians, giving it a bohemian character that persists today.",
                "nl": "Terwijl we door de Jordaan glijden, let op de prachtige woonboten langs de grachten. Dit gebied was ooit de thuisbasis van veel kunstenaars en muzikanten, wat het een bohemien karakter gaf dat vandaag nog steeds bestaat.",
                "si": "අපි ජෝර්ඩාන් ප්‍රදේශය හරහා යන අතරතුර, ඇළ දිගේ සිටින සුන්දර නිවාස බෝට්ටු නරඹන්න. මෙම ප්‍රදේශය වරෙක බොහෝ කලාකරුවන් සහ සංගීත ians යන්ගේ නිවහන වූ අතර, එය අද දක්වාම පවතින බොහීමියානු චරිතයක් ලබා දුන්නේය.",
                "ta": "நாங்கள் ஜோர்டான் மாவட்டத்தின் வழியாக செல்லும்போது, கால்வாய்களில் வரிசையாக நிற்கும் அழகான வீட்டுப் படகுகளைக் கவனியுங்கள். இந்த பகுதி ஒரு காலத்தில் பல கலைஞர்கள் மற்றும் இசைக்கலைஞர்களின் இல்லமாக இருந்தது, இது இன்றும் நீடிக்கும் போஹேமியன் தன்மையை அளித்தது.",
                "ja": "ヨルダン地区を滑るように進む際、運河沿いに並ぶ美しいハウスボートに注目してください。この地域はかつて多くの芸術家や音楽家の故郷で、今日まで続くボヘミアンな性格を与えました。",
                "zh": "当我们滑过约旦区时，请注意沿着运河排列的美丽船屋。这个地区曾经是许多艺术家和音乐家的家园，赋予了它至今仍然存在的波西米亚风格。"
            },
            "order": 2
        },
        {
            "name": "Anne Frank House",
            "description": {
                "en": "To your right, you can see the famous Anne Frank House, a powerful reminder of Amsterdam's history.",
                "nl": "Aan uw rechterkant ziet u het beroemde Anne Frank Huis, een krachtige herinnering aan de geschiedenis van Amsterdam.",
                "si": "ඔබේ දකුණට, ඇම්ස්ටර්ඩෑම්හි ඉතිහාසය පිළිබඳ ප්‍රබල මතක් කිරීමක් වන ප්‍රසිද්ධ ඈන් ෆ්‍රෑන්ක් මන්දිරය ඔබට දැකිය හැකිය.",
                "ta": "உங்கள் வலதுபுறத்தில், ஆம்ஸ்டர்டாமின் வரலாற்றின் சக்திவாய்ந்த நினைவூட்டலான புகழ்பெற்ற அன்னே ஃபிராங்க் வீட்டைக் காணலாம்.",
                "ja": "右側には、アムステルダムの歴史を力強く思い起こさせる有名なアンネ・フランクの家が見えます。",
                "zh": "在您的右侧，您可以看到著名的安妮·弗兰克之家，这是阿姆斯特丹历史的有力提醒。"
            },
            "latitude": 52.3752,
            "longitude": 4.8840,
            "trigger_radius": 60.0,
            "audio_content": {
                "en": "We're now passing the Anne Frank House, where Anne Frank and her family hid during World War II. This historic site attracts over a million visitors each year and serves as an important memorial to the victims of the Holocaust.",
                "nl": "We passeren nu het Anne Frank Huis, waar Anne Frank en haar familie zich verstopten tijdens de Tweede Wereldoorlog. Deze historische plek trekt jaarlijks meer dan een miljoen bezoekers en dient als een belangrijk monument voor de slachtoffers van de Holocaust.",
                "si": "අපි දැන් ඈන් ෆ්‍රෑන්ක් මන්දිරය පසු කරමු, දෙවන ලෝක යුද්ධ සමයේදී ඈන් ෆ්‍රෑන්ක් සහ ඇගේ පවුල සැඟවී සිටි ස්ථානයයි. මෙම ඓතිහාසික ස්ථානය වසරකට අමුත්තන් මිලියනයකට වඩා ආකර්ෂණය කරන අතර හොලොකෝස්ට් බලිකරුවන්ට වැදගත් ස්මාරකයක් ලෙස සේවය කරයි.",
                "ta": "நாங்கள் இப்போது அன்னே ஃபிராங்க் வீட்டைக் கடந்து செல்கிறோம், இரண்டாம் உலகப் போரின்போது அன்னே ஃபிராங்கும் அவரது குடும்பமும் மறைந்திருந்த இடம். இந்த வரலாற்று தளம் ஆண்டுக்கு ஒரு மில்லியனுக்கும் மேற்பட்ட பார்வையாளர்களை ஈர்க்கிறது மற்றும் ஹோலோகாஸ்ட் பாதிக்கப்பட்டவர்களுக்கு ஒரு முக்கியமான நினைவுச்சின்னமாக செயல்படுகிறது.",
                "ja": "私たちは今、第二次世界大戦中にアンネ・フランクとその家族が隠れていたアンネ・フランクの家を通り過ぎています。この歴史的な場所は年間100万人以上の訪問者を魅力し、ホロコーストの犠牲者への重要な記念碑として機能しています。",
                "zh": "我们现在经过安妮·弗兰克之家，安妮·弗兰克和她的家人在第二次世界大战期间躲藏在那里。这个历史遗址每年吸引超过一百万游客，是大屠杀受害者的重要纪念碑。"
            },
            "order": 3
        },
        {
            "name": "Westerkerk",
            "description": {
                "en": "The impressive Westerkerk church tower rises before us, Amsterdam's tallest church tower.",
                "nl": "De indrukwekkende toren van de Westerkerk rijst voor ons op, Amsterdam's hoogste kerktoren.",
                "si": "අතිවිශිෂ්ට වෙස්ටර්කර්ක් පල්ලි කුළුණ අප ඉදිරියෙන් නැඟී ඇත, ඇම්ස්ටර්ඩෑම්හි උසම පල්ලි කුළුණයි.",
                "ta": "ஈர்க்கக்கூடிய வெஸ்டர்கர்க் தேவாலய கோபுரம் எங்கள் முன் உயர்ந்துள்ளது, ஆம்ஸ்டர்டாமின் மிக உயரமான தேவாலய கோபுரம்.",
                "ja": "印象的なウェスター教会の塔が私たちの前にそびえ立っています。アムステルダムで最も高い教会の塔です。",
                "zh": "令人印象深刻的西教堂塔在我们面前耸立，这是阿姆斯特丹最高的教堂塔。"
            },
            "latitude": 52.3743,
            "longitude": 4.8831,
            "trigger_radius": 80.0,
            "audio_content": {
                "en": "Before us stands the magnificent Westerkerk, completed in 1631. This Protestant church is famous for its 85-meter tall tower, which offers one of the best views of Amsterdam. The great Dutch artist Rembrandt is buried in this churchyard.",
                "nl": "Voor ons staat de prachtige Westerkerk, voltooid in 1631. Deze protestantse kerk is beroemd om zijn 85 meter hoge toren, die een van de beste uitzichten over Amsterdam biedt. De grote Nederlandse kunstenaar Rembrandt ligt begraven op dit kerkhof.",
                "si": "අප ඉදිරියෙන් 1631 දී නිම කරන ලද අපූරු වෙස්ටර්කර්ක් පල්ලිය පිහිටා ඇත. මෙම ප්‍රෝතෙස්තන්ත පල්ලිය මීටර් 85ක් උස කුළුණ සඳහා ප්‍රසිද්ධ වන අතර එය ඇම්ස්ටර්ඩෑම්හි හොඳම දසුන් වලින් එකක් ලබා දෙයි. ශ්‍රේෂ්ඨ ලන්දේසි කලාකරු රෙම්බ්‍රෑන්ට් මෙම පල්ලි භූමියේ වළලනු ලැබ ඇත.",
                "ta": "எங்கள் முன் 1631 இல் நிறைவடைந்த அழகான வெஸ்டர்கர்க் நின்று கொண்டிருக்கிறது. இந்த புராட்டஸ்டன்ட் தேவாலயம் அதன் 85 மீட்டர் உயரமான கோபுரத்திற்கு பிரபலமானது, இது ஆம்ஸ்டர்டாமின் சிறந்த காட்சிகளில் ஒன்றை வழங்குகிறது. சிறந்த டச்சு கலைஞர் ரெம்ப்ராண்ட் இந்த தேவாலய தோட்டத்தில் புதைக்கப்பட்டுள்ளார்.",
                "ja": "私たちの前には1631年に完成した壮大なウェスター教会が立っています。このプロテスタント教会は85メートルの高い塔で有名で、アムステルダムの最高の景色の一つを提供しています。偉大なオランダの芸術家レンブラントがこの教会の墓地に埋葬されています。",
                "zh": "在我们面前矗立着宏伟的西教堂，建成于1631年。这座新教教堂以其85米高的塔楼而闻名，提供阿姆斯特丹最佳景观之一。伟大的荷兰艺术家伦勃朗就埋葬在这个教堂墓地里。"
            },
            "order": 4
        }
    ]
    
    # Insert sample tour points
    inserted_points = []
    for point_data in sample_points:
        point = TourPoint(**point_data)
        result = await db.tour_points.insert_one(point.dict())
        inserted_points.append(point.id)
    
    # Create sample tour route
    sample_route = TourRoute(
        name="Amsterdam Canal Dining Tour",
        description={
            "en": "A magical dining boat tour through Amsterdam's historic canals",
            "nl": "Een magische eetboat tour door Amsterdam's historische grachten",
            "si": "ඇම්ස්ටර්ඩෑම්හි ඓතිහාසික ඇළ මාර්ග හරහා ආශ්චර්යමත් ආහාර නෞකා චාරිකාවක්",
            "ta": "ஆம்ஸ்டர்டாமின் வரலாற்று கால்வாய்கள் வழியாக ஒரு மந்திர உணவு படகு பயணம்",
            "ja": "アムステルダムの歴史的な運河を通る魔法のダイニングボートツアー",
            "zh": "穿越阿姆斯特丹历史运河的神奇餐船之旅"
        },
        tour_points=inserted_points
    )
    
    await db.tour_routes.insert_one(sample_route.dict())
    logger.info("Sample data initialized successfully")

# Routes for Tour Management
@api_router.get("/tour-routes", response_model=List[TourRoute])
async def get_tour_routes():
    routes = await db.tour_routes.find({"is_active": True}).to_list(1000)
    return [TourRoute(**route) for route in routes]

@api_router.get("/tour-routes/{route_id}/points", response_model=List[TourPoint])
async def get_tour_route_points(route_id: str):
    route = await db.tour_routes.find_one({"id": route_id})
    if not route:
        raise HTTPException(status_code=404, detail="Tour route not found")
    
    points = await db.tour_points.find({"id": {"$in": route["tour_points"]}}).to_list(1000)
    sorted_points = sorted([TourPoint(**point) for point in points], key=lambda x: x.order)
    return sorted_points

@api_router.post("/tour-sessions", response_model=TourSession)
async def create_tour_session(session_data: TourSessionCreate):
    # Verify route exists
    route = await db.tour_routes.find_one({"id": session_data.route_id})
    if not route:
        raise HTTPException(status_code=404, detail="Tour route not found")
    
    session = TourSession(**session_data.dict())
    await db.tour_sessions.insert_one(session.dict())
    return session

@api_router.put("/tour-sessions/{session_id}/location")
async def update_tour_session_location(session_id: str, location: UserLocation):
    session = await db.tour_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Tour session not found")
    
    await db.tour_sessions.update_one(
        {"id": session_id},
        {"$set": {"last_location": location.dict()}}
    )
    
    return {"message": "Location updated successfully"}

@api_router.get("/tour-sessions/{session_id}/current-content")
async def get_current_tour_content(session_id: str, language: str = "en"):
    session = await db.tour_sessions.find_one({"id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Tour session not found")
    
    # Get tour route and points
    route = await db.tour_routes.find_one({"id": session["route_id"]})
    if not route:
        raise HTTPException(status_code=404, detail="Tour route not found")
    
    points = await db.tour_points.find({"id": {"$in": route["tour_points"]}}).to_list(1000)
    sorted_points = sorted([TourPoint(**point) for point in points], key=lambda x: x.order)
    
    if session["current_point_index"] < len(sorted_points):
        current_point = sorted_points[session["current_point_index"]]
        return {
            "point": current_point,
            "description": current_point.description.get(language, current_point.description.get("en", "")),
            "audio_content": current_point.audio_content.get(language, current_point.audio_content.get("en", "")),
            "progress": session["current_point_index"] + 1,
            "total_points": len(sorted_points)
        }
    
    return {"message": "Tour completed", "progress": len(sorted_points), "total_points": len(sorted_points)}

# Google Maps Directions API integration
import googlemaps

# Initialize Google Maps client
GOOGLE_MAPS_API_KEY = "AIzaSyARSoKujCNX2odk8wachQyz0DIjBCqJNd4"
gmaps_client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

class PlaceSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    radius: Optional[int] = Field(5000, ge=100, le=50000)
    language: Optional[str] = Field("en")

class RouteRequest(BaseModel):
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lng: float = Field(..., ge=-180, le=180)
    destination_lat: float = Field(..., ge=-90, le=90)
    destination_lng: float = Field(..., ge=-180, le=180)
    travel_mode: str = Field("driving", pattern="^(driving|walking|bicycling|transit)$")
    language: str = Field("en")
    avoid: Optional[List[str]] = Field(None)

class RouteStep(BaseModel):
    instruction: str
    distance_text: str
    distance_value: int
    duration_text: str
    duration_value: int
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    maneuver: Optional[str] = None
    polyline: str

class RouteResponse(BaseModel):
    total_distance_text: str
    total_distance_value: int
    total_duration_text: str
    total_duration_value: int
    start_address: str
    end_address: str
    overview_polyline: str
    steps: List[RouteStep]
    bounds: Dict[str, Any]

class SearchResult(BaseModel):
    place_id: str
    name: str
    formatted_address: str
    latitude: float
    longitude: float
    types: List[str] = []
    rating: Optional[float] = None

# Enhanced API Routes for Destination Search and Navigation
@api_router.post("/search/places")
async def search_places(search_request: PlaceSearchRequest):
    """Search for places/destinations using text query"""
    try:
        search_params = {
            'query': search_request.query,
            'language': search_request.language
        }
        
        if search_request.latitude and search_request.longitude:
            search_params['location'] = (search_request.latitude, search_request.longitude)
            search_params['radius'] = search_request.radius
        
        logger.info(f"Searching places for: {search_request.query}")
        results = gmaps_client.places(**search_params)
        
        search_results = []
        for place in results.get('results', []):
            try:
                search_result = SearchResult(
                    place_id=place['place_id'],
                    name=place['name'],
                    formatted_address=place.get('formatted_address', ''),
                    latitude=place['geometry']['location']['lat'],
                    longitude=place['geometry']['location']['lng'],
                    types=place.get('types', []),
                    rating=place.get('rating')
                )
                search_results.append(search_result)
            except KeyError:
                continue
        
        return {
            "status": "success",
            "results": search_results,
            "total": len(search_results)
        }
        
    except googlemaps.exceptions.ApiError as e:
        logger.error(f"Google Maps API error: {e}")
        raise HTTPException(status_code=400, detail=f"Search failed: {str(e)}")
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search service unavailable")

@api_router.post("/directions/calculate", response_model=RouteResponse)
async def calculate_route(route_request: RouteRequest):
    """Calculate route with turn-by-turn directions"""
    try:
        origin = (route_request.origin_lat, route_request.origin_lng)
        destination = (route_request.destination_lat, route_request.destination_lng)
        
        directions_params = {
            'origin': origin,
            'destination': destination,
            'mode': route_request.travel_mode,
            'language': route_request.language,
            'alternatives': True
        }
        
        if route_request.avoid:
            directions_params['avoid'] = '|'.join(route_request.avoid)
        
        logger.info(f"Calculating route from {origin} to {destination}")
        directions_result = gmaps_client.directions(**directions_params)
        
        if not directions_result:
            raise HTTPException(status_code=404, detail="No route found")
        
        # Process the primary route
        route = directions_result[0]
        leg = route['legs'][0]
        
        # Process turn-by-turn steps
        steps = []
        for step in leg['steps']:
            route_step = RouteStep(
                instruction=step['html_instructions'],
                distance_text=step['distance']['text'],
                distance_value=step['distance']['value'],
                duration_text=step['duration']['text'],
                duration_value=step['duration']['value'],
                start_lat=step['start_location']['lat'],
                start_lng=step['start_location']['lng'],
                end_lat=step['end_location']['lat'],
                end_lng=step['end_location']['lng'],
                maneuver=step.get('maneuver'),
                polyline=step['polyline']['points']
            )
            steps.append(route_step)
        
        # Extract route bounds
        bounds = route['bounds']
        
        route_response = RouteResponse(
            total_distance_text=leg['distance']['text'],
            total_distance_value=leg['distance']['value'],
            total_duration_text=leg['duration']['text'],
            total_duration_value=leg['duration']['value'],
            start_address=leg['start_address'],
            end_address=leg['end_address'],
            overview_polyline=route['overview_polyline']['points'],
            steps=steps,
            bounds={
                'northeast': {
                    'lat': bounds['northeast']['lat'],
                    'lng': bounds['northeast']['lng']
                },
                'southwest': {
                    'lat': bounds['southwest']['lat'],
                    'lng': bounds['southwest']['lng']
                }
            }
        )
        
        return route_response
        
    except googlemaps.exceptions.ApiError as e:
        logger.error(f"Google Directions API error: {e}")
        raise HTTPException(status_code=400, detail=f"Route calculation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Route calculation error: {e}")
        raise HTTPException(status_code=500, detail="Navigation service unavailable")

@api_router.post("/geocode/address")
async def geocode_address(address: str, language: str = "en"):
    """Convert address to coordinates"""
    try:
        logger.info(f"Geocoding address: {address}")
        geocode_result = gmaps_client.geocode(address=address, language=language)
        
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return {
                "status": "success",
                "address": address,
                "latitude": location['lat'],
                "longitude": location['lng'],
                "formatted_address": geocode_result[0]['formatted_address']
            }
        else:
            raise HTTPException(status_code=404, detail="Address not found")
            
    except googlemaps.exceptions.ApiError as e:
        logger.error(f"Geocoding API error: {e}")
        raise HTTPException(status_code=400, detail=f"Geocoding failed: {str(e)}")
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        raise HTTPException(status_code=500, detail="Geocoding service unavailable")

@api_router.get("/languages")
async def get_supported_languages():
    """Get supported language codes for navigation"""
    supported_languages = [
        {"code": "en", "name": "English", "flag": "🇬🇧"},
        {"code": "nl", "name": "Nederlands", "flag": "🇳🇱"},
        {"code": "si", "name": "සිංහල", "flag": "🇱🇰"},
        {"code": "ta", "name": "தமிழ்", "flag": "🇱🇰"},
        {"code": "ja", "name": "日本語", "flag": "🇯🇵"},
        {"code": "zh", "name": "中文", "flag": "🇨🇳"},
        {"code": "es", "name": "Español", "flag": "🇪🇸"},
        {"code": "fr", "name": "Français", "flag": "🇫🇷"},
        {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
        {"code": "it", "name": "Italiano", "flag": "🇮🇹"},
        {"code": "pt", "name": "Português", "flag": "🇵🇹"},
        {"code": "ru", "name": "Русский", "flag": "🇷🇺"},
        {"code": "ar", "name": "العربية", "flag": "🇸🇦"},
        {"code": "hi", "name": "हिन्दी", "flag": "🇮🇳"},
        {"code": "th", "name": "ไทย", "flag": "🇹🇭"},
        {"code": "ko", "name": "한국어", "flag": "🇰🇷"}
    ]
    
    return {
        "status": "success",
        "languages": supported_languages,
        "total": len(supported_languages)
    }

# Initialize app
@app.on_event("startup")
async def startup_event():
    await init_sample_data()

# Original routes
@api_router.get("/")
async def root():
    return {"message": "GPS Tunnel - Dining Boat Tour Navigation API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
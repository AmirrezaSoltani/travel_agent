-- AI Travel Recommender Agent - Iranian Database Schema
-- Comprehensive database for Iran-focused travel recommendations

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Iranian provinces table
CREATE TABLE provinces (
    id SERIAL PRIMARY KEY,
    name_fa VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    capital_fa VARCHAR(100) NOT NULL,
    capital_en VARCHAR(100) NOT NULL,
    population INTEGER,
    area_km2 INTEGER,
    climate_type VARCHAR(50),
    best_season VARCHAR(50),
    tourism_rating DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Iranian cities table
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name_fa VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    province_id INTEGER REFERENCES provinces(id),
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    population INTEGER,
    elevation_m INTEGER,
    timezone VARCHAR(50) DEFAULT 'Asia/Tehran',
    airport_code VARCHAR(10),
    train_station BOOLEAN DEFAULT FALSE,
    bus_terminal BOOLEAN DEFAULT FALSE,
    tourism_rating DECIMAL(3,2) DEFAULT 0.0,
    cost_index DECIMAL(5,2) DEFAULT 100.0,
    description_fa TEXT,
    description_en TEXT,
    best_time_to_visit VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comprehensive attractions table
CREATE TABLE attractions (
    id SERIAL PRIMARY KEY,
    name_fa VARCHAR(200) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    city_id INTEGER REFERENCES cities(id),
    category VARCHAR(50) NOT NULL, -- historical, natural, religious, modern, cultural
    subcategory VARCHAR(50), -- mosque, palace, museum, park, etc.
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    description_fa TEXT,
    description_en TEXT,
    rating DECIMAL(3,2) DEFAULT 0.0,
    price_range VARCHAR(20), -- free, low, medium, high, luxury
    opening_hours TEXT,
    best_time_to_visit VARCHAR(100),
    accessibility_info TEXT,
    photos_urls TEXT, -- JSON array of photo URLs
    unesco_heritage BOOLEAN DEFAULT FALSE,
    cultural_significance TEXT,
    historical_period VARCHAR(100),
    architecture_style VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Route segments with real data
CREATE TABLE route_segments (
    id SERIAL PRIMARY KEY,
    origin_city_id INTEGER REFERENCES cities(id),
    destination_city_id INTEGER REFERENCES cities(id),
    distance_km INTEGER NOT NULL,
    duration_hours DECIMAL(4,2) NOT NULL,
    road_type VARCHAR(50), -- highway, freeway, provincial, rural
    toll_cost INTEGER DEFAULT 0,
    fuel_cost INTEGER DEFAULT 0,
    scenic_rating DECIMAL(3,2) DEFAULT 0.0,
    safety_rating DECIMAL(3,2) DEFAULT 0.0,
    seasonal_restrictions TEXT,
    road_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(origin_city_id, destination_city_id)
);

-- User profiles table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name_fa VARCHAR(100),
    name_en VARCHAR(100),
    phone VARCHAR(20),
    language_preference VARCHAR(10) DEFAULT 'fa',
    travel_style VARCHAR(50), -- budget, luxury, adventure, cultural, family
    budget_range VARCHAR(20), -- low, medium, high, luxury
    accessibility_needs TEXT,
    cultural_interests TEXT, -- JSON array
    seasonal_preferences TEXT, -- JSON array
    group_size INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User travel history
CREATE TABLE user_travel_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    route_id INTEGER,
    origin_city_id INTEGER REFERENCES cities(id),
    destination_city_id INTEGER REFERENCES cities(id),
    travel_date DATE,
    duration_days INTEGER,
    budget_spent INTEGER,
    rating DECIMAL(3,2),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User preferences and ratings
CREATE TABLE user_attraction_ratings (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    attraction_id INTEGER REFERENCES attractions(id),
    rating DECIMAL(3,2) NOT NULL,
    review_text TEXT,
    visit_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, attraction_id)
);

-- Chat conversation history
CREATE TABLE chat_conversations (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(100),
    language VARCHAR(10) DEFAULT 'fa',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES chat_conversations(id),
    message_text TEXT NOT NULL,
    response_text TEXT,
    intent VARCHAR(50),
    entities TEXT, -- JSON object
    language VARCHAR(10) DEFAULT 'fa',
    is_user_message BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seasonal events and festivals
CREATE TABLE seasonal_events (
    id SERIAL PRIMARY KEY,
    name_fa VARCHAR(200) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    city_id INTEGER REFERENCES cities(id),
    event_type VARCHAR(50), -- religious, cultural, seasonal, national
    start_date DATE NOT NULL,
    end_date DATE,
    description_fa TEXT,
    description_en TEXT,
    cultural_significance TEXT,
    tourist_attraction_rating DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weather data for cities
CREATE TABLE city_weather (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id),
    month INTEGER NOT NULL, -- 1-12
    avg_temperature_c DECIMAL(4,2),
    avg_precipitation_mm DECIMAL(6,2),
    weather_condition VARCHAR(50),
    best_for_tourism BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, month)
);

-- Transportation options
CREATE TABLE transportation_options (
    id SERIAL PRIMARY KEY,
    origin_city_id INTEGER REFERENCES cities(id),
    destination_city_id INTEGER REFERENCES cities(id),
    transport_type VARCHAR(50), -- bus, train, plane, car
    duration_hours DECIMAL(4,2),
    cost_toman INTEGER,
    frequency VARCHAR(100), -- daily, weekly, etc.
    operator_name VARCHAR(100),
    comfort_level VARCHAR(20), -- economy, business, luxury
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accommodation options
CREATE TABLE accommodations (
    id SERIAL PRIMARY KEY,
    name_fa VARCHAR(200) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    city_id INTEGER REFERENCES cities(id),
    category VARCHAR(50), -- hotel, hostel, guesthouse, traditional
    price_range VARCHAR(20),
    rating DECIMAL(3,2) DEFAULT 0.0,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    amenities TEXT, -- JSON array
    halal_certified BOOLEAN DEFAULT TRUE,
    accessibility_features TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Restaurant and food options
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name_fa VARCHAR(200) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    city_id INTEGER REFERENCES cities(id),
    cuisine_type VARCHAR(100),
    price_range VARCHAR(20),
    rating DECIMAL(3,2) DEFAULT 0.0,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    halal_certified BOOLEAN DEFAULT TRUE,
    vegetarian_friendly BOOLEAN DEFAULT FALSE,
    traditional_dishes TEXT, -- JSON array
    opening_hours TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_cities_province ON cities(province_id);
CREATE INDEX idx_cities_coordinates ON cities(latitude, longitude);
CREATE INDEX idx_attractions_city ON attractions(city_id);
CREATE INDEX idx_attractions_category ON attractions(category);
CREATE INDEX idx_attractions_unesco ON attractions(unesco_heritage);
CREATE INDEX idx_route_segments_origin ON route_segments(origin_city_id);
CREATE INDEX idx_route_segments_destination ON route_segments(destination_city_id);
CREATE INDEX idx_user_travel_history_user ON user_travel_history(user_id);
CREATE INDEX idx_chat_messages_conversation ON chat_messages(conversation_id);
CREATE INDEX idx_seasonal_events_city ON seasonal_events(city_id);
CREATE INDEX idx_city_weather_city ON city_weather(city_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to all tables
CREATE TRIGGER update_provinces_updated_at BEFORE UPDATE ON provinces FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cities_updated_at BEFORE UPDATE ON cities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_attractions_updated_at BEFORE UPDATE ON attractions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_route_segments_updated_at BEFORE UPDATE ON route_segments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample Iranian provinces
INSERT INTO provinces (name_fa, name_en, capital_fa, capital_en, population, area_km2, climate_type, best_season, tourism_rating) VALUES
('تهران', 'Tehran', 'تهران', 'Tehran', 13267637, 18814, 'semi_arid', 'spring,fall', 4.2),
('اصفهان', 'Isfahan', 'اصفهان', 'Isfahan', 5120850, 107029, 'desert', 'spring,fall', 4.8),
('فارس', 'Fars', 'شیراز', 'Shiraz', 4851274, 122608, 'semi_arid', 'spring,fall', 4.7),
('آذربایجان شرقی', 'East Azerbaijan', 'تبریز', 'Tabriz', 3909652, 45650, 'continental', 'spring,summer', 4.3),
('خراسان رضوی', 'Razavi Khorasan', 'مشهد', 'Mashhad', 6434501, 118851, 'continental', 'spring,fall', 4.5),
('یزد', 'Yazd', 'یزد', 'Yazd', 1138533, 129285, 'desert', 'fall,winter', 4.4),
('اصفهان', 'Isfahan', 'کاشان', 'Kashan', 364482, 9641, 'desert', 'spring,fall', 4.6),
('قم', 'Qom', 'قم', 'Qom', 1292283, 11526, 'desert', 'spring,fall', 4.1),
('البرز', 'Alborz', 'کرج', 'Karaj', 2712400, 5833, 'semi_arid', 'spring,fall', 3.8),
('خوزستان', 'Khuzestan', 'اهواز', 'Ahvaz', 4710509, 64055, 'desert', 'winter,spring', 3.9);

-- Insert sample Iranian cities
INSERT INTO cities (name_fa, name_en, province_id, latitude, longitude, population, elevation_m, airport_code, train_station, bus_terminal, tourism_rating, cost_index, description_fa, description_en, best_time_to_visit) VALUES
('تهران', 'Tehran', 1, 35.6892, 51.3890, 8693706, 1200, 'IKA', TRUE, TRUE, 4.2, 120.0, 'پایتخت ایران و مرکز سیاسی و اقتصادی کشور', 'Capital of Iran and political and economic center', 'spring,fall'),
('اصفهان', 'Isfahan', 2, 32.6546, 51.6680, 1961260, 1590, 'IFN', TRUE, TRUE, 4.8, 95.0, 'شهر نصف جهان با معماری تاریخی باشکوه', 'Half the World city with magnificent historical architecture', 'spring,fall'),
('شیراز', 'Shiraz', 3, 29.5916, 52.5836, 1565572, 1500, 'SYZ', TRUE, TRUE, 4.7, 90.0, 'شهر شعر و ادب و باغ‌های زیبا', 'City of poetry and beautiful gardens', 'spring,fall'),
('تبریز', 'Tabriz', 4, 38.0962, 46.2738, 1558693, 1350, 'TBZ', TRUE, TRUE, 4.3, 85.0, 'شهر اولین‌ها و مرکز تجاری شمال غرب', 'City of firsts and commercial center of northwest', 'spring,summer'),
('مشهد', 'Mashhad', 5, 36.2605, 59.6168, 3001184, 985, 'MHD', TRUE, TRUE, 4.5, 100.0, 'شهر مقدس و مرکز زیارتی ایران', 'Holy city and pilgrimage center of Iran', 'spring,fall'),
('یزد', 'Yazd', 6, 31.8974, 54.3569, 529673, 1216, 'AZD', TRUE, TRUE, 4.4, 80.0, 'شهر بادگیرها و معماری سنتی', 'City of wind towers and traditional architecture', 'fall,winter'),
('کاشان', 'Kashan', 7, 33.9850, 51.4100, 304487, 982, NULL, TRUE, TRUE, 4.6, 75.0, 'شهر گلاب و خانه‌های تاریخی', 'City of rosewater and historical houses', 'spring,fall'),
('قم', 'Qom', 8, 34.6416, 50.8746, 1201158, 928, NULL, TRUE, TRUE, 4.1, 85.0, 'شهر مقدس و مرکز علوم دینی', 'Holy city and center of religious studies', 'spring,fall'),
('کرج', 'Karaj', 9, 35.8400, 50.9391, 1973470, 1312, 'PYK', TRUE, TRUE, 3.8, 110.0, 'شهر صنعتی و خوابگاه تهران', 'Industrial city and Tehran dormitory', 'spring,fall'),
('اهواز', 'Ahvaz', 10, 31.3183, 48.6706, 1184788, 17, 'AWZ', TRUE, TRUE, 3.9, 90.0, 'شهر نفت و مرکز خوزستان', 'Oil city and center of Khuzestan', 'winter,spring');

-- Insert sample attractions
INSERT INTO attractions (name_fa, name_en, city_id, category, subcategory, latitude, longitude, description_fa, description_en, rating, price_range, opening_hours, best_time_to_visit, unesco_heritage, cultural_significance, historical_period, architecture_style) VALUES
('میدان امام', 'Imam Square', 2, 'historical', 'square', 32.6577, 51.6775, 'میدان تاریخی و مرکز شهر اصفهان', 'Historical square and center of Isfahan', 4.8, 'free', '24/7', 'spring,fall', TRUE, 'UNESCO World Heritage Site', 'Safavid', 'Islamic'),
('تخت جمشید', 'Persepolis', 3, 'historical', 'palace', 29.9354, 52.8916, 'پایتخت امپراتوری هخامنشی', 'Capital of Achaemenid Empire', 4.9, 'medium', '8:00-17:00', 'spring,fall', TRUE, 'UNESCO World Heritage Site', 'Achaemenid', 'Persian'),
('مسجد نصیرالملک', 'Nasir al-Mulk Mosque', 3, 'religious', 'mosque', 29.6083, 52.5432, 'مسجد صورتی با شیشه‌های رنگی', 'Pink mosque with stained glass', 4.7, 'low', '8:00-17:00', 'morning', FALSE, 'Cultural landmark', 'Qajar', 'Islamic'),
('کاخ گلستان', 'Golestan Palace', 1, 'historical', 'palace', 35.6804, 51.4203, 'کاخ سلطنتی قاجار', 'Qajar royal palace', 4.5, 'medium', '9:00-17:00', 'spring,fall', TRUE, 'UNESCO World Heritage Site', 'Qajar', 'Persian-Islamic'),
('برج آزادی', 'Azadi Tower', 1, 'modern', 'monument', 35.6994, 51.3375, 'نماد تهران و مدرنیته ایران', 'Symbol of Tehran and Iranian modernity', 4.4, 'free', '24/7', 'evening', FALSE, 'National symbol', 'Pahlavi', 'Modern'),
('باغ ارم', 'Eram Garden', 3, 'natural', 'garden', 29.6361, 52.5247, 'باغ تاریخی و زیبای شیراز', 'Historical and beautiful garden of Shiraz', 4.6, 'low', '8:00-18:00', 'spring', FALSE, 'Cultural heritage', 'Qajar', 'Persian'),
('مسجد جامع یزد', 'Jameh Mosque of Yazd', 6, 'religious', 'mosque', 31.8974, 54.3569, 'مسجد جامع با مناره‌های بلند', 'Grand mosque with tall minarets', 4.5, 'free', '24/7', 'morning', FALSE, 'Religious center', 'Ilkhanid', 'Islamic'),
('خانه بروجردی‌ها', 'Borujerdi House', 7, 'historical', 'house', 33.9850, 51.4100, 'خانه تاریخی با معماری سنتی', 'Historical house with traditional architecture', 4.4, 'medium', '9:00-17:00', 'spring,fall', FALSE, 'Cultural heritage', 'Qajar', 'Traditional'),
('حرم امام رضا', 'Imam Reza Shrine', 5, 'religious', 'shrine', 36.2605, 59.6168, 'حرم مطهر امام رضا', 'Holy shrine of Imam Reza', 4.8, 'free', '24/7', 'year_round', FALSE, 'Religious center', 'Various', 'Islamic'),
('پل خواجو', 'Khaju Bridge', 2, 'historical', 'bridge', 32.6333, 51.6833, 'پل تاریخی روی زاینده‌رود', 'Historical bridge over Zayandeh River', 4.6, 'free', '24/7', 'evening', FALSE, 'Cultural landmark', 'Safavid', 'Islamic');

-- Insert sample route segments
INSERT INTO route_segments (origin_city_id, destination_city_id, distance_km, duration_hours, road_type, toll_cost, fuel_cost, scenic_rating, safety_rating, seasonal_restrictions) VALUES
(1, 2, 450, 5.5, 'highway', 50000, 225000, 4.2, 4.5, NULL),
(1, 3, 920, 11.0, 'highway', 80000, 460000, 4.5, 4.3, NULL),
(1, 4, 620, 7.5, 'highway', 60000, 310000, 4.0, 4.4, 'winter_snow'),
(1, 5, 890, 10.5, 'highway', 75000, 445000, 4.1, 4.6, NULL),
(2, 3, 480, 6.0, 'highway', 45000, 240000, 4.8, 4.2, NULL),
(2, 6, 320, 4.0, 'provincial', 25000, 160000, 4.3, 4.0, NULL),
(3, 7, 220, 3.0, 'provincial', 20000, 110000, 4.4, 4.1, NULL),
(5, 4, 780, 9.5, 'highway', 70000, 390000, 4.2, 4.5, 'winter_snow'),
(6, 7, 180, 2.5, 'provincial', 15000, 90000, 4.1, 4.0, NULL),
(1, 6, 650, 8.0, 'highway', 55000, 325000, 4.0, 4.3, NULL);

-- Insert sample seasonal events
INSERT INTO seasonal_events (name_fa, name_en, city_id, event_type, start_date, end_date, description_fa, description_en, cultural_significance, tourist_attraction_rating) VALUES
('جشنواره گلاب‌گیری', 'Rosewater Festival', 7, 'cultural', '2024-05-01', '2024-05-15', 'جشنواره سنتی گلاب‌گیری در کاشان', 'Traditional rosewater festival in Kashan', 'Cultural heritage', 4.7),
('جشنواره نوروز', 'Nowruz Festival', 1, 'national', '2024-03-20', '2024-03-21', 'جشن باستانی نوروز در تهران', 'Ancient Nowruz celebration in Tehran', 'National holiday', 4.8),
('جشنواره شعر شیراز', 'Shiraz Poetry Festival', 3, 'cultural', '2024-09-01', '2024-09-07', 'جشنواره شعر و ادب در شیراز', 'Poetry and literature festival in Shiraz', 'Cultural heritage', 4.5),
('مراسم محرم', 'Muharram Ceremonies', 5, 'religious', '2024-07-07', '2024-07-17', 'مراسم مذهبی محرم در مشهد', 'Religious Muharram ceremonies in Mashhad', 'Religious significance', 4.6),
('جشنواره بادگیر', 'Wind Tower Festival', 6, 'cultural', '2024-06-15', '2024-06-22', 'جشنواره معماری سنتی در یزد', 'Traditional architecture festival in Yazd', 'Cultural heritage', 4.4);

-- Insert sample weather data
INSERT INTO city_weather (city_id, month, avg_temperature_c, avg_precipitation_mm, weather_condition, best_for_tourism) VALUES
(1, 3, 12.5, 45.2, 'mild', TRUE),
(1, 4, 18.2, 38.1, 'pleasant', TRUE),
(1, 5, 24.8, 25.3, 'warm', TRUE),
(1, 6, 30.1, 8.7, 'hot', FALSE),
(1, 9, 26.3, 12.4, 'warm', TRUE),
(1, 10, 19.8, 28.9, 'pleasant', TRUE),
(2, 3, 14.2, 32.1, 'mild', TRUE),
(2, 4, 20.1, 28.5, 'pleasant', TRUE),
(2, 5, 26.8, 18.2, 'warm', TRUE),
(2, 9, 24.5, 8.9, 'warm', TRUE),
(2, 10, 18.9, 22.1, 'pleasant', TRUE),
(3, 3, 16.8, 28.4, 'mild', TRUE),
(3, 4, 22.5, 24.1, 'pleasant', TRUE),
(3, 5, 28.9, 15.6, 'warm', TRUE),
(3, 9, 26.2, 6.8, 'warm', TRUE),
(3, 10, 21.4, 18.9, 'pleasant', TRUE);

-- Insert sample transportation options
INSERT INTO transportation_options (origin_city_id, destination_city_id, transport_type, duration_hours, cost_toman, frequency, operator_name, comfort_level) VALUES
(1, 2, 'bus', 6.0, 150000, 'hourly', 'Iran Peyma', 'economy'),
(1, 2, 'train', 7.5, 200000, 'daily', 'RAI', 'business'),
(1, 3, 'plane', 1.5, 800000, 'daily', 'Iran Air', 'economy'),
(1, 3, 'bus', 12.0, 250000, 'daily', 'Iran Peyma', 'economy'),
(1, 4, 'plane', 1.0, 600000, 'daily', 'Iran Air', 'economy'),
(1, 5, 'plane', 1.5, 700000, 'daily', 'Iran Air', 'economy'),
(2, 3, 'bus', 6.5, 180000, 'daily', 'Iran Peyma', 'economy'),
(2, 6, 'bus', 4.5, 120000, 'daily', 'Iran Peyma', 'economy'),
(3, 7, 'bus', 3.5, 80000, 'daily', 'Iran Peyma', 'economy'),
(5, 4, 'plane', 1.0, 500000, 'daily', 'Iran Air', 'economy');

-- Insert sample accommodations
INSERT INTO accommodations (name_fa, name_en, city_id, category, price_range, rating, latitude, longitude, amenities, halal_certified, accessibility_features) VALUES
('هتل پارسیان آزادی', 'Parsian Azadi Hotel', 1, 'hotel', 'luxury', 4.5, 35.6994, 51.3375, '["wifi", "pool", "gym", "restaurant"]', TRUE, '["wheelchair", "elevator"]'),
('هتل عباسی', 'Abbasi Hotel', 2, 'hotel', 'luxury', 4.8, 32.6577, 51.6775, '["wifi", "garden", "restaurant", "spa"]', TRUE, '["wheelchair", "elevator"]'),
('هتل هما', 'Homa Hotel', 3, 'hotel', 'high', 4.6, 29.5916, 52.5836, '["wifi", "pool", "restaurant"]', TRUE, '["wheelchair", "elevator"]'),
('هتل لاله', 'Laleh Hotel', 4, 'hotel', 'medium', 4.2, 38.0962, 46.2738, '["wifi", "restaurant"]', TRUE, '["elevator"]'),
('هتل قصر', 'Ghasr Hotel', 5, 'hotel', 'high', 4.4, 36.2605, 59.6168, '["wifi", "restaurant", "prayer_room"]', TRUE, '["wheelchair", "elevator"]'),
('خانه سنتی یزد', 'Traditional House Yazd', 6, 'guesthouse', 'low', 4.3, 31.8974, 54.3569, '["wifi", "traditional_courtyard"]', TRUE, '["traditional_access"]'),
('خانه بروجردی‌ها', 'Borujerdi House', 7, 'guesthouse', 'medium', 4.5, 33.9850, 51.4100, '["wifi", "traditional_architecture"]', TRUE, '["traditional_access"]');

-- Insert sample restaurants
INSERT INTO restaurants (name_fa, name_en, city_id, cuisine_type, price_range, rating, latitude, longitude, halal_certified, vegetarian_friendly, traditional_dishes, opening_hours) VALUES
('رستوران شاندیز', 'Shandiz Restaurant', 1, 'Persian', 'high', 4.6, 35.6892, 51.3890, TRUE, TRUE, '["kabab", "ghormeh_sabzi", "fesenjan"]', '12:00-23:00'),
('رستوران باغ رستوران', 'Garden Restaurant', 2, 'Persian', 'medium', 4.7, 32.6546, 51.6680, TRUE, TRUE, '["biriyani", "kabab", "ash"]', '12:00-22:00'),
('رستوران هفت خوان', 'Haft Khan Restaurant', 3, 'Persian', 'high', 4.8, 29.5916, 52.5836, TRUE, TRUE, '["kabab", "ghormeh_sabzi", "khoresh"]', '12:00-23:00'),
('رستوران سنتی تبریز', 'Traditional Tabriz Restaurant', 4, 'Azerbaijani', 'medium', 4.4, 38.0962, 46.2738, TRUE, TRUE, '["dolma", "kabab", "ash"]', '12:00-22:00'),
('رستوران حرم', 'Shrine Restaurant', 5, 'Persian', 'medium', 4.3, 36.2605, 59.6168, TRUE, TRUE, '["kabab", "ghormeh_sabzi", "ash"]', '24/7'),
('رستوران سنتی یزد', 'Traditional Yazd Restaurant', 6, 'Persian', 'low', 4.5, 31.8974, 54.3569, TRUE, TRUE, '["kabab", "ghormeh_sabzi", "ash"]', '12:00-21:00'),
('رستوران کاشان', 'Kashan Restaurant', 7, 'Persian', 'medium', 4.4, 33.9850, 51.4100, TRUE, TRUE, '["kabab", "ghormeh_sabzi", "ash"]', '12:00-22:00'); 
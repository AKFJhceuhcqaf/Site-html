-- 1. Создание таблицы записей (bookings)
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    service TEXT NOT NULL,
    date TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Создание таблицы отзывов (reviews)
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    author TEXT NOT NULL,
    text TEXT NOT NULL,
    date TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Включение Row Level Security (RLS)
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

-- 4. Политики безопасности для анонимных пользователей
CREATE POLICY "Allow anonymous inserts to bookings" ON bookings
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow anonymous reads from bookings" ON bookings
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous reads to reviews" ON reviews
    FOR SELECT USING (true);

CREATE POLICY "Allow anonymous inserts to reviews" ON reviews
    FOR INSERT WITH CHECK (true);
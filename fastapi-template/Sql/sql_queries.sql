CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    subscription_type TEXT CHECK (subscription_type IN ('basic', 'premium')) NOT NULL,
    max_limit INTEGER NOT NULL,
    current_total INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    rent_per_week INTEGER NOT NULL,
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status TEXT CHECK (status IN ('available', 'pending', 'rented')) DEFAULT 'available',
    current_renter_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE rent_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    renter_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status TEXT CHECK (status IN ('pending', 'accepted', 'declined')) DEFAULT 'pending',
    request_date TIMESTAMP DEFAULT NOW(),
    decision_date TIMESTAMP
);
CREATE TABLE waitlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE INDEX idx_book_status ON books(status);
CREATE INDEX idx_rent_requests_status ON rent_requests(status);
CREATE INDEX idx_waitlist_book_position ON waitlists(book_id, position);

ALTER TABLE users
ADD COLUMN password_hash TEXT;




INSERT INTO users (id, name, email, phone, is_admin, subscription_type, max_limit, current_total)
VALUES (
    gen_random_uuid(),
    'Admin User',
    'admin@booknest.com',
    '9999999999',
    TRUE,
    'premium',
    1000,
    0
);

#pip install psycopg2-binary passlib
pip uninstall bcrypt passlib -y
pip install bcrypt passlib

CREATE TABLE rental_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    renter_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rented_by_owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    rent_start TIMESTAMP NOT NULL DEFAULT NOW(),
    rent_end TIMESTAMP,  -- NULL if still ongoing
    status TEXT CHECK (status IN ('rented', 'returned')),
    note TEXT  -- optional field for manual remarks
);

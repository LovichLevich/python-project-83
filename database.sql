CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE
);

CREATE TABLE url_checks (
    id SERIAL PRIMARY KEY,
    url_id INTEGER NOT NULL,
    status_code INTEGER,
    h1 TEXT,
    title TEXT,
    description TEXT,
    created_at DATE DEFAULT CURRENT_DATE
);

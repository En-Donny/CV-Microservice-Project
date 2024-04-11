CREATE TABLE IF NOT EXISTS scrapped_images (
    id SERIAL PRIMARY KEY,
    img_name TEXT NOT NULL,
    img_hash TEXT NOT NULL UNIQUE,
    img_path TEXT NOT NULL,
    is_highlighted BOOLEAN NOT NULL DEFAULT FALSE
);

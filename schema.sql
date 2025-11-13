-- =============================
-- Drop existing tables (orden correcto por dependencias)
-- =============================
DROP TABLE IF EXISTS price_history;
DROP TABLE IF EXISTS card_in_collection;
DROP TABLE IF EXISTS collection;
DROP TABLE IF EXISTS price;
DROP TABLE IF EXISTS card_condition;
DROP TABLE IF EXISTS card;
DROP TABLE IF EXISTS "user";
DROP TABLE IF EXISTS language;
DROP TABLE IF EXISTS edition;
DROP TABLE IF EXISTS set_name;
DROP TABLE IF EXISTS image;

-- =============================
-- Users table
-- =============================
CREATE TABLE "user" (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- =============================
-- Card conditions table
-- =============================
CREATE TABLE card_condition (
    condition_id SERIAL PRIMARY KEY,
    description VARCHAR(100) UNIQUE NOT NULL
);

-- =============================
-- Cards table
-- =============================
CREATE TABLE card (
    card_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    language_id INTEGER NOT NULL,
    set_name_id INTEGER NOT NULL,
    set_number VARCHAR(50),
    image_id INTEGER NOT NULL,
    edition_id INTEGER,
    CONSTRAINT card_unique UNIQUE (name, language_id, set_name_id, set_number, image_id, edition_id)
);

-- =============================
-- Languages, editions, set names, and images
-- =============================
CREATE TABLE language (
    language_id SERIAL PRIMARY KEY,
    description VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE edition (
    edition_id SERIAL PRIMARY KEY,
    description VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE set_name (
    set_name_id SERIAL PRIMARY KEY,
    description VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE image (
    image_url_id SERIAL PRIMARY KEY,
    url VARCHAR(255) UNIQUE NOT NULL
);

-- =============================
-- Prices table
-- =============================
CREATE TABLE price (
    card_id INTEGER,
    condition_id INTEGER,
    price_usd DECIMAL NOT NULL,
    date TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (card_id, condition_id)
);

-- =============================
-- Collections table
-- =============================
CREATE TABLE collection (
    collection_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    exchange_rate DECIMAL,
    collection_price_usd DECIMAL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================
-- Cards in collections
-- =============================
CREATE TABLE card_in_collection (
    card_collection_id SERIAL PRIMARY KEY,
    collection_id INTEGER NOT NULL,
    card_id INTEGER NOT NULL,
    condition_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL
);

-- =============================
-- Price history (historial de precios)
-- =============================
CREATE TABLE price_history (
    price_history_id SERIAL PRIMARY KEY,
    card_id INTEGER NOT NULL,
    condition_id INTEGER NOT NULL,
    price_usd DECIMAL NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (card_id, condition_id) REFERENCES price (card_id, condition_id)
);

-- =============================
-- Comments
-- =============================
COMMENT ON COLUMN card.language_id IS 'EN or JP';
COMMENT ON COLUMN card.set_name_id IS 'e.g., Legend of Blue Eyes White Dragon';
COMMENT ON COLUMN card.set_number IS 'e.g., LOB-001';
COMMENT ON COLUMN card.image_id IS 'link to official image';
COMMENT ON COLUMN card_condition.description IS 'Example: Near Mint, Lightly Played';
COMMENT ON COLUMN collection.exchange_rate IS 'Negotiable per collection';
COMMENT ON COLUMN collection.collection_price_usd IS 'Calculated from sum of individual cards';

-- =============================
-- Foreign keys
-- =============================
ALTER TABLE collection 
    ADD FOREIGN KEY (user_id) REFERENCES "user" (user_id);

ALTER TABLE card 
    ADD FOREIGN KEY (language_id) REFERENCES language (language_id),
    ADD FOREIGN KEY (edition_id) REFERENCES edition (edition_id),
    ADD FOREIGN KEY (set_name_id) REFERENCES set_name (set_name_id),
    ADD FOREIGN KEY (image_id) REFERENCES image (image_url_id);

ALTER TABLE price 
    ADD FOREIGN KEY (card_id) REFERENCES card (card_id),
    ADD FOREIGN KEY (condition_id) REFERENCES card_condition (condition_id);

ALTER TABLE card_in_collection 
    ADD FOREIGN KEY (collection_id) REFERENCES collection (collection_id),
    ADD FOREIGN KEY (card_id, condition_id) REFERENCES price (card_id, condition_id);

-- =============================
-- Trigger para registrar el historial de precios
-- =============================

CREATE OR REPLACE FUNCTION log_price_update()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.price_usd IS DISTINCT FROM OLD.price_usd THEN
        INSERT INTO price_history (card_id, condition_id, price_usd, updated_at)
        VALUES (NEW.card_id, NEW.condition_id, NEW.price_usd, NOW());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_price_history
AFTER UPDATE ON price
FOR EACH ROW
EXECUTE FUNCTION log_price_update();

-- =============================
-- Ejemplo opcional de uso
-- =============================
-- INSERT INTO language (description) VALUES ('EN');
-- INSERT INTO set_name (description) VALUES ('Legend of Blue Eyes White Dragon');
-- INSERT INTO edition (description) VALUES ('1st Edition');
-- INSERT INTO image (url) VALUES ('https://example.com/blueeyes.jpg');
-- INSERT INTO card_condition (description) VALUES ('Near Mint');
-- INSERT INTO card (name, language_id, set_name_id, set_number, image_id, edition_id)
-- VALUES ('Blue-Eyes White Dragon', 1, 1, 'LOB-001', 1, 1);
-- INSERT INTO price (card_id, condition_id, price_usd) VALUES (1, 1, 50.00);
-- UPDATE price SET price_usd = 55.00 WHERE card_id = 1 AND condition_id = 1; -- Esto genera un registro en price_history

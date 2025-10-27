-- Drop tables if they already exist

DROP TABLE IF EXISTS card_in_collection;
DROP TABLE IF EXISTS collection;
DROP TABLE IF EXISTS price;
DROP TABLE IF EXISTS card_condition;
DROP TABLE IF EXISTS card;
DROP TABLE IF EXISTS "user";

DROP TABLE IF EXISTS "card_set";
DROP TABLE IF EXISTS "language";
DROP TABLE IF EXISTS "finish_type";

-- Users table
CREATE TABLE "user" (
    "user_id" SERIAL PRIMARY KEY,
    "name" VARCHAR,
    "email" VARCHAR UNIQUE,
    "created_at" TIMESTAMP
);

-- Card conditions table
CREATE TABLE card_condition (
    condition_id SERIAL PRIMARY KEY,
    description VARCHAR UNIQUE
);

-- Prices table
CREATE TABLE "price" (
    "card_id" INTEGER,
    "condition_id" INTEGER,
    "price_usd" DECIMAL NOT NULL,
    "date" TIMESTAMP,
    PRIMARY KEY ("card_id", "condition_id")
);

-- Collections table
CREATE TABLE collection (
    "collection_id" SERIAL PRIMARY KEY,
    "title" VARCHAR,
    "user_id" INTEGER NOT NULL,
    "exchange_rate" DECIMAL,
    "collection_price_usd" DECIMAL,
    "created_at" TIMESTAMP
);

-- Cards in collections table
CREATE TABLE card_in_collection (
    "card_collection_id" SERIAL PRIMARY KEY,
    "collection_id" INTEGER NOT NULL,
    "card_id" INTEGER NOT NULL,
    "condition_id" INTEGER NOT NULL,
    "quantity" INTEGER
);

-- Cards table
CREATE TABLE "card" (
    "card_id" SERIAL PRIMARY KEY,
    "name" VARCHAR,
    "language_id" INTEGER NOT NULL,
    "set_name_id" INTEGER NOT NULL,
    "set_number" VARCHAR,
    "image_id" INTEGER NOT NULL,
    "edition_id" INTEGER,
    CONSTRAINT card_unique UNIQUE (name, language_id, set_name_id, set_number, image_id, edition_id)
);

-- Card language table
CREATE TABLE language (
    language_id SERIAL PRIMARY KEY,
    description VARCHAR UNIQUE
);

-- Card edition table
CREATE TABLE edition (
    edition_id SERIAL PRIMARY KEY,
    description VARCHAR UNIQUE
);

-- Card set name table
CREATE TABLE set_name (
    set_name_id SERIAL PRIMARY KEY,
    description VARCHAR UNIQUE
);

-- Card set name table
CREATE TABLE image (
    image_url_id SERIAL PRIMARY KEY,
    url VARCHAR UNIQUE
);

-- Comments
COMMENT ON COLUMN "card"."language" IS 'EN or JP';
COMMENT ON COLUMN "card"."set_name" IS 'e.g., Legend of Blue Eyes White Dragon';
COMMENT ON COLUMN "card"."set_number" IS 'e.g., LOB-001';
COMMENT ON COLUMN "card"."image_url" IS 'link to official image';
COMMENT ON COLUMN "card_condition"."description" IS 'Example: Near Mint, Lightly Played';
COMMENT ON COLUMN "collection"."exchange_rate" IS 'Negotiable per collection';
COMMENT ON COLUMN "collection"."collection_price_usd" IS 'Calculated from sum of individual cards';

-- Foreign keys
ALTER TABLE collection 
    ADD FOREIGN KEY (user_id) REFERENCES "user" (user_id);

ALTER TABLE card 
    ADD FOREIGN KEY (language_id) REFERENCES "language" (language_id);

ALTER TABLE card 
    ADD FOREIGN KEY (edition_id) REFERENCES "edition" (edition_id);

ALTER TABLE card 
    ADD FOREIGN KEY (set_name_id) REFERENCES "set_name" (set_name_id);

ALTER TABLE card 
    ADD FOREIGN KEY (image_id) REFERENCES "image" (image_url_id);

ALTER TABLE card_in_collection 
    ADD FOREIGN KEY (collection_id) REFERENCES collection (collection_id);

ALTER TABLE price 
    ADD FOREIGN KEY (card_id) REFERENCES card (card_id);

ALTER TABLE price 
    ADD FOREIGN KEY (condition_id) REFERENCES card_condition (condition_id);

ALTER TABLE card_in_collection 
    ADD FOREIGN KEY (card_id, condition_id) REFERENCES price (card_id, condition_id);
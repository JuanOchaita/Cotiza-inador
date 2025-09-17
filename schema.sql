
CREATE TABLE "user" (
  "user_id" SERIAL PRIMARY KEY,
  "name" varchar,
  "email" varchar UNIQUE,
  "created_at" timestamp DEFAULT now()
);

CREATE TABLE "card" (
  "card_id" SERIAL PRIMARY KEY,
  "name" varchar,
  "language" varchar,
  "set_name" varchar,
  "set_number" varchar,
  "finish_type" varchar,
  "image_url" varchar
);

CREATE TABLE "card_condition" (
  "condition_id" SERIAL PRIMARY KEY,
  "description" varchar
);

CREATE TABLE "price" (
  "card_id" integer NOT NULL,
  "condition_id" integer NOT NULL,
  "price_usd" decimal,
  "created_at" timestamp DEFAULT now(),
  PRIMARY KEY ("card_id", "condition_id", "created_at"),
  FOREIGN KEY ("card_id") REFERENCES "card" ("card_id"),
  FOREIGN KEY ("condition_id") REFERENCES "card_condition" ("condition_id")
);

CREATE TABLE "collection" (
  "collection_id" SERIAL PRIMARY KEY,
  "title" varchar,
  "user_id" integer NOT NULL,
  "exchange_rate" decimal,
  "collection_price_usd" decimal,
  "created_at" timestamp DEFAULT now(),
  FOREIGN KEY ("user_id") REFERENCES "user" ("user_id")
);

CREATE TABLE "card_in_collection" (
  "card_collection_id" SERIAL PRIMARY KEY,
  "collection_id" integer NOT NULL,
  "card_id" integer NOT NULL,
  "condition_id" integer NOT NULL,
  "quantity" integer,
  "price" decimal,
  FOREIGN KEY ("collection_id") REFERENCES "collection" ("collection_id"),
  FOREIGN KEY ("card_id") REFERENCES "card" ("card_id"),
  FOREIGN KEY ("condition_id") REFERENCES "card_condition" ("condition_id")
);

COMMENT ON COLUMN "card"."language" IS 'EN or JP';
COMMENT ON COLUMN "card"."set_name" IS 'e.g: Legend of Blue Eyes White Dragon';
COMMENT ON COLUMN "card"."set_number" IS 'e.g: LOB-001';
COMMENT ON COLUMN "card"."finish_type" IS 'Normal, Holofoil, Reverse Holofoil';
COMMENT ON COLUMN "card"."image_url" IS 'link to official image';
COMMENT ON COLUMN "card_condition"."description" IS 'Example: Near Mint, Lightly Played';
COMMENT ON COLUMN "collection"."exchange_rate" IS 'Negotiable per collection';
COMMENT ON COLUMN "collection"."collection_price_usd" IS 'CALCULATED VALUE FROM SUM OF INDIVIDUAL CARDS';

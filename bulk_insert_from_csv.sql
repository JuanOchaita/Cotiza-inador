-- ============================================================
-- BULK INSERT desde CSV a PostgreSQL
-- ============================================================
-- Este script importa datos desde un CSV a una estructura normalizada
-- Asume que el archivo CSV está en: /path/to/your/file.csv
-- Reemplaza la ruta con la ubicación real de tu archivo

-- Paso 1: Crear tabla temporal para cargar el CSV
DROP TABLE IF EXISTS temp_csv_import;

CREATE TEMP TABLE temp_csv_import (
    card_name VARCHAR,
    set_name VARCHAR,
    number_in_set VARCHAR,
    printing_option VARCHAR,
    condition VARCHAR,
    market_price DECIMAL,
    image VARCHAR
);

-- Paso 2: Cargar datos del CSV a la tabla temporal
-- IMPORTANTE: Reemplaza '/path/to/your/file.csv' con la ruta real
COPY temp_csv_import(card_name, set_name, number_in_set, printing_option, condition, market_price, image)
FROM '/tmp/cards.csv'
DELIMITER ','
CSV HEADER;

-- Paso 3: Insertar valores únicos en tablas de referencia

-- 3.1 Insertar condiciones únicas
INSERT INTO card_condition (description)
SELECT DISTINCT TRIM(condition)
FROM temp_csv_import
WHERE condition IS NOT NULL 
  AND TRIM(condition) != ''
ON CONFLICT (description) DO NOTHING;

-- 3.2 Insertar nombres de sets únicos
INSERT INTO set_name (description)
SELECT DISTINCT TRIM(set_name)
FROM temp_csv_import
WHERE set_name IS NOT NULL 
  AND TRIM(set_name) != ''
ON CONFLICT (description) DO NOTHING;

-- 3.3 Insertar ediciones únicas (printing_option)
INSERT INTO edition (description)
SELECT DISTINCT TRIM(printing_option)
FROM temp_csv_import
WHERE printing_option IS NOT NULL 
  AND TRIM(printing_option) != ''
ON CONFLICT (description) DO NOTHING;

-- 3.4 Insertar URLs de imágenes únicas
INSERT INTO image (url)
SELECT DISTINCT TRIM(image)
FROM temp_csv_import
WHERE image IS NOT NULL 
  AND TRIM(image) != ''
ON CONFLICT (url) DO NOTHING;

-- 3.5 Insertar idioma por defecto si no existe
INSERT INTO language (description)
VALUES ('EN')
ON CONFLICT (description) DO NOTHING;

-- Paso 4: Insertar cartas en la tabla card
INSERT INTO card (name, language_id, set_name_id, set_number, image_id, edition_id)
SELECT DISTINCT
    TRIM(t.card_name),
    (SELECT language_id FROM language WHERE description = 'EN' LIMIT 1),
    sn.set_name_id,
    TRIM(t.number_in_set),
    img.image_url_id,
    ed.edition_id
FROM temp_csv_import t
INNER JOIN set_name sn ON TRIM(t.set_name) = sn.description
LEFT JOIN edition ed ON TRIM(t.printing_option) = ed.description
INNER JOIN image img ON TRIM(t.image) = img.url
WHERE t.card_name IS NOT NULL 
  AND TRIM(t.card_name) != ''
ON CONFLICT (name, language_id, set_name_id, set_number, image_id, edition_id) DO NOTHING;

-- Paso 5: Insertar precios en la tabla price
INSERT INTO price (card_id, condition_id, price_usd, date)
SELECT DISTINCT
    c.card_id,
    cc.condition_id,
    t.market_price,
    CURRENT_TIMESTAMP
FROM temp_csv_import t
INNER JOIN set_name sn ON TRIM(t.set_name) = sn.description
LEFT JOIN edition ed ON TRIM(t.printing_option) = ed.description
INNER JOIN image img ON TRIM(t.image) = img.url
INNER JOIN card c ON 
    TRIM(t.card_name) = c.name
    AND c.language_id = (SELECT language_id FROM language WHERE description = 'EN' LIMIT 1)
    AND sn.set_name_id = c.set_name_id
    AND TRIM(t.number_in_set) = c.set_number
    AND img.image_url_id = c.image_id
    AND (ed.edition_id = c.edition_id OR (ed.edition_id IS NULL AND c.edition_id IS NULL))
INNER JOIN card_condition cc ON TRIM(t.condition) = cc.description
WHERE t.market_price IS NOT NULL
ON CONFLICT (card_id, condition_id) DO UPDATE
SET 
    price_usd = EXCLUDED.price_usd,
    date = EXCLUDED.date;

-- Paso 6: Verificar resultados
SELECT 'Registros importados desde CSV:' as info, COUNT(*) as count FROM temp_csv_import
UNION ALL
SELECT 'Condiciones creadas:', COUNT(*) FROM card_condition
UNION ALL
SELECT 'Sets creados:', COUNT(*) FROM set_name
UNION ALL
SELECT 'Ediciones creadas:', COUNT(*) FROM edition
UNION ALL
SELECT 'Imágenes creadas:', COUNT(*) FROM image
UNION ALL
SELECT 'Cartas creadas:', COUNT(*) FROM card
UNION ALL
SELECT 'Precios creados:', COUNT(*) FROM price;

-- Paso 7: Limpiar tabla temporal (opcional, se elimina automáticamente al final de la sesión)
-- DROP TABLE IF EXISTS temp_csv_import;
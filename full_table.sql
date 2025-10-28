SELECT 
    c.name AS card_name,
    sn.description AS set_name,
    c.set_number AS number_in_set,
    COALESCE(e.description, 'Normal') AS printing_option,
    cc.description AS condition,
    p.price_usd AS market_price,
    i.url AS image
FROM card c
INNER JOIN set_name sn ON c.set_name_id = sn.set_name_id
LEFT JOIN edition e ON c.edition_id = e.edition_id
INNER JOIN image i ON c.image_id = i.image_url_id
INNER JOIN price p ON c.card_id = p.card_id
INNER JOIN card_condition cc ON p.condition_id = cc.condition_id
ORDER BY 
    c.name,
    sn.description,
    c.set_number,
    COALESCE(e.description, 'Normal'),
    CASE cc.description
        WHEN 'Damaged' THEN 1
        WHEN 'Heavily Played' THEN 2
        WHEN 'Moderately Played' THEN 3
        WHEN 'Lightly Played' THEN 4
        WHEN 'Near Mint' THEN 5
        ELSE 6
    END;
-- upgrade --
UPDATE properties_property AS p
SET property_type_id = ppt.id
FROM properties_property_type AS ppt
WHERE ppt.slug ILIKE p.type;
-- downgrade --
SELECT *
FROM properties_property_type;

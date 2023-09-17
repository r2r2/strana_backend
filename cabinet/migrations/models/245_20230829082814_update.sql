-- upgrade --
DELETE FROM properties_feature;
CREATE UNIQUE INDEX "uid_properties__backend_7f7e4c" ON "properties_feature" ("backend_id");
-- downgrade --
DROP INDEX "idx_properties__backend_7f7e4c";

-- upgrade --
UPDATE cautions_caution SET created_at = now() WHERE id > 0;
ALTER TABLE cautions_caution ALTER COLUMN created_at SET NOT NULL;
ALTER TABLE cautions_caution ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE cautions_caution
    ALTER COLUMN created_at TYPE timestamptz,
    ALTER COLUMN expires_at TYPE timestamptz,
    ALTER COLUMN updated_at TYPE timestamptz;
-- downgrade --
ALTER TABLE cautions_caution ALTER COLUMN created_at DROP NOT NULL;
ALTER TABLE cautions_caution
    ALTER COLUMN created_at TYPE date,
    ALTER COLUMN expires_at TYPE date,
    ALTER COLUMN updated_at TYPE date;
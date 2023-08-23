-- upgrade --
CREATE TABLE IF NOT EXISTS "task_management_taskstatus_buttons" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "button_id" INT NOT NULL REFERENCES "task_management_button" ("id") ON DELETE CASCADE,
    "task_status_id" INT NOT NULL REFERENCES "task_management_taskstatus" ("id") ON DELETE CASCADE
);

INSERT INTO task_management_taskstatus_buttons (button_id, task_status_id)
SELECT id AS button_id, status_id AS task_status_id
FROM task_management_button;

ALTER TABLE task_management_button DROP COLUMN IF EXISTS status_id;
-- downgrade --
ALTER TABLE task_management_button
ADD COLUMN status_id INT;

UPDATE task_management_button AS tmb
SET status_id = tmtb.task_status_id
FROM task_management_taskstatus_buttons AS tmtb
WHERE tmb.id = tmtb.button_id;

ALTER TABLE task_management_button
ADD CONSTRAINT fk_task_management_button_status_id_fkey FOREIGN KEY (status_id)
REFERENCES task_management_taskstatus (id) ON DELETE CASCADE;

DROP TABLE IF EXISTS task_management_taskstatus_buttons;

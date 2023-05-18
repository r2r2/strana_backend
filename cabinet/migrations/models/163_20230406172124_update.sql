-- upgrade --
ALTER TABLE "taskchain_status_through" RENAME COLUMN "status_id" TO "status_substage_id";
ALTER TABLE "taskchain_status_through" RENAME COLUMN "task_chain_id" TO "task_chain_substage_id";
ALTER TABLE "taskchain_taskvisibility_status_through" RENAME COLUMN "status_id" TO "status_visibility_id";
ALTER TABLE "taskchain_taskvisibility_status_through" RENAME COLUMN "task_chain_id" TO "task_chain_visibility_id";
-- downgrade --
ALTER TABLE "taskchain_status_through" RENAME COLUMN "status_substage_id" TO "status_id";
ALTER TABLE "taskchain_status_through" RENAME COLUMN "task_chain_substage_id" TO "task_chain_id";
ALTER TABLE "taskchain_taskvisibility_status_through" RENAME COLUMN "status_visibility_id" TO "status_id";
ALTER TABLE "taskchain_taskvisibility_status_through" RENAME COLUMN "task_chain_visibility_id" TO "task_chain_id";

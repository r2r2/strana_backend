-- upgrade --
ALTER TABLE public.task_management_button ADD COLUMN IF NOT EXISTS priority INTEGER NULL;
COMMENT ON COLUMN public.task_management_button.priority IS 'Чем меньше приоритет - тем выше выводится кнопка в интерфейсе задания';
-- downgrade --
ALTER TABLE public.task_management_button DROP COLUMN IF EXISTS priority;

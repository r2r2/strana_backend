-- upgrade --

-- временно убираем констрейнты потому что с ними ломается
ALTER TABLE "users_user" DROP CONSTRAINT users_user_unique_together_username_type;
ALTER TABLE "users_user" DROP CONSTRAINT users_user_unique_together_phone_type;
ALTER TABLE "users_user" DROP CONSTRAINT users_user_unique_together_email_type;


-- заменяем любые символы которые не являются цифрами от 0 до 9 на '', g: неограниченное числов вхождений
UPDATE users_user SET phone = REGEXP_REPLACE(phone, '[^0-9]', '', 'g');

-- в строке начинающейся с 7 меняем на +7
UPDATE users_user SET phone = REGEXP_REPLACE(phone, '^7', '+7');

-- в строке начинающейся с 8 меняем на +7
UPDATE users_user SET phone = REGEXP_REPLACE(phone, '^8', '+7');

-- в строке начинающейся с 9 меняем на +79
UPDATE users_user SET phone = REGEXP_REPLACE(phone, '^9', '+79');


WITH
      -- получаем дубли по amocrm_id
	duplicates_amocrm AS (
	    SELECT id, amocrm_id, created_at FROM users_user WHERE amocrm_id IN (
		    SELECT amocrm_id FROM users_user GROUP BY amocrm_id HAVING COUNT(*) > 1
		)
	),
	-- юзеры клиенты чей amocrm_id попал в дубли
	clients AS (
	    SELECT amocrm_id FROM users_user WHERE "type"='client' AND amocrm_id IS NOT NULL AND amocrm_id IN (
	        SELECT amocrm_id FROM duplicates_amocrm
	    )
	),
	-- юзеры агенты чей amocrm_id попал в дубли
	agents AS (
	    SELECT amocrm_id FROM users_user WHERE "type"='agent' AND amocrm_id IS NOT NULL AND amocrm_id IN (
	        SELECT amocrm_id FROM duplicates_amocrm
	    )
	),
	-- пересечение множества юзеров клиентов и юзеров агентов
	-- которое даёт нам множество юзеров которые агенты и клиенты одновременно
	inter AS (SELECT * FROM agents intersect SELECT * FROM clients),
	-- самые новые юзеры чьи amocrm_id попал в дубли
	newest_amorcrm AS (
	    SELECT DISTINCT ON (amocrm_id) * FROM duplicates_amocrm order by amocrm_id, created_at desc
	),
	-- удаляем всех юзеров чьи amocrm_id попал в дубли но таких которые не попали в пересечение выше (кто и агент и юзер одновременно)
	-- и которые не относяться к самым новым записям
	deleted_by_amocrm AS (
	 	DELETE FROM users_user WHERE amocrm_id IN (SELECT amocrm_id FROM duplicates_amocrm)
	 	AND amocrm_id NOT IN (SELECT * FROM inter)
	 	AND amocrm_id NOT IN (SELECT amocrm_id FROM newest_amorcrm)
	 	returning id
	 ),

	-- получаем все дубли телефонных номеров которые образовались после форматирования и которые остались
	-- после очистки дублей по amocrm_id
	duplicates_phone AS (
	    SELECT id, phone, created_at FROM users_user WHERE phone IN (
		    SELECT phone FROM users_user GROUP BY phone HAVING COUNT(*) > 1
	    )
	),
	-- самые новые записи среди дублирующихся телефонов
	newest_phone AS (
	    SELECT DISTINCT ON (phone) * FROM duplicates_phone order by phone, created_at desc
    ),
	-- удаляем юзеров среди дублирующихся телефонов таких которые
	-- -не являются самыми новыми записями
	-- -которые имеют amocrm_id
	-- -чей amocrm_id не попал в валидное пересечение клиент и агент
	deleted_by_phone AS (
	    DELETE FROM users_user WHERE id IN (
	        SELECT id FROM users_user WHERE phone IN (SELECT phone FROM duplicates_phone)
	        AND id NOT IN (SELECT id FROM newest_phone)
	        AND amocrm_id is NOT NULL AND amocrm_id NOT IN (SELECT * FROM inter)
	    ) returning id
    )
-- удаляем телефоны такие которые попали в дубли телефонов и не являются самыми новыми и не имеют amocrm_id
DELETE FROM users_user WHERE id IN (
	SELECT id FROM users_user WHERE phone IN (SELECT phone FROM duplicates_phone)
	AND id NOT IN (SELECT id FROM newest_phone)
	AND amocrm_id is NULL
);

-- возвращаем констрейнты
ALTER TABLE "users_user" ADD CONSTRAINT users_user_unique_together_username_type UNIQUE (username, type);
ALTER TABLE "users_user" ADD CONSTRAINT users_user_unique_together_phone_type UNIQUE (phone, type);
ALTER TABLE "users_user" ADD CONSTRAINT users_user_unique_together_email_type UNIQUE (email, type);


-- c users_manages все проще, там нет дублей и не образуются дубли, просто форматируем
UPDATE users_managers SET phone = REGEXP_REPLACE(phone, '[^0-9]', '', 'g');
UPDATE users_managers SET phone = REGEXP_REPLACE(phone, '^7', '+7');
UPDATE users_managers SET phone = REGEXP_REPLACE(phone, '^8', '+7');
UPDATE users_managers SET phone = REGEXP_REPLACE(phone, '^9', '+79');


-- downgrade --
SELECT 1;

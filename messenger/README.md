# Sportlevel messenger service, v. 0.1.0
Чат для сервисов экосистемы Sportlevel


# Локальная разработка
1. Создать venv: `python -m venv .venv`
2. Установить в неё poetry `pip install poetry`, установить зависимости `poetry install`
3. Создать локальный конфиг: `cp config.example.yml config.yml`
3. Запустить локальные контейнеры (postgres, redis, rabbitmq): `docker-compose up -d`
4. Выполнить миграции бд: `python cli.py migrator upgrade head`
5. Запустить сервис:
  * `python cli.py service run http_server --port HTTP_PORT`
  * `python cli.py service run jobs --port JOBS_PORT`
  * `python cli.py service run ws_server --port WS_PORT`
  * `python cli.py service run worker --port WORKER_PORT`
  * `python cli.py service run updates_streamer --port STREAMER_PORT`


### Использование CLI

Основная точка входа: `python cli.py`. Выполнив команду, можно увидеть все опции и варианты (запуск компонентов, миграции, запуск тестклиента).

### Codestyle

На проекте на данный момент используются:
* ruff
* pyright

# Протокол общения с клиентом

HTTP - REST Api (JSON)

WS - Protobuf

## HTTP

HTTP соединение используется для получения списка чатов, фильтрации и поиска, первичного получения списка сообщений при запуска виджета чата и т.п.


**Общие ошибки при взаимодействии:**

* 422 - Ошибка валидации запроса
* 500 - Внутренняя ошибка на сервере
* 401 - Необходима авторизация
* 403 - Неверные данные авторизации

## WS

WS соединение используется для обмена оперативными данными (получение сообщений, уведомлений об активности (напр. онлайн/оффлайн), отправка сообщений и т.п.)

**Общие ошибки при взаимодействии:**

* Не указаны данные для авторизации - WS 1002
* Неверные данные для авторизации - WS 1003
* Недостаточно прав (авторизация) - WS 1008
* Сервер выключен / редеплой / перезапуск - WS 1001

### Авторизация

Для авторизации используются токены, выданные сервисом SL Auth.

Для HTTP запросов токены передаются в заголовке (`Authorization: Bearer <token>`), для WS - через query `ws://host/chat?token=<token>`


### Протокол обмена сообщениями через Websocket

Выбран protobuf как оптимальный вариант по скорости, потреблению ресурсов и поддерживаемости.
Файл с описанием протокола находится в репозитории [sl-messenger-protobuf](https://gitlab.fbsvc.bz/sl-protobuf/sl-messenger-protobuf)

Все сообщения разбиты на 2 вида:

`ServerMessage` - сообщения, которые могут быть отправлены с сервера клиенту

`ClientMessage` - сообщения, которые могут быть отправлены с клиента серверу

При отправке сообщения не используется (для ускорения [де]сериализации) структура с oneof (`ServerMessage/ClientMessage`), сообщения запаковываются по алгоритму:

1. Взять id сообщения из справочника `ServerMessage/ClientMessage`
2. Добавить его в буфер (1 байт двоичных данных)
3. Добавить в буфер само сериализованное сообщение
4. Отправить буфер

Для распаковки:

1. Извлечь id сообщения из первого байта данных
2. По id сообщения узнать его тип и распаковать само сообщение

Псевдокод:
```python

Heartbeat: google.protobuf.message.Message
ws: Websocket
get_message_type_id: Callable[[google.protobuf.message.Message], int]

message = Heartbeat(timestamp=time.time())
message_type_id = get_message_type_id(message)

ws.send_bytes(
    message_type_id.to_bytes() + message.SerializeToString()
)
```
В итоге получается оверхед в 1 байт для каждого сообщения при сохранении условия, что максимально мы поддерживаем 256 типов сообщений.

# Архитектура приложения-чата

Приложение состоит из нескольких компонентов (модулей), часть из которых может быть использована независимо от других. Список модулей (`src/modules`):

1. **Auth** (`sl_auth_client`) - Предоставляет функционал авторизации для пользовательского API
2. **Chat** (`websockets, protobuf`) - Контроллер для вебсокет соединений. Принимает соединения, общается с клиентом
3. **Connections** (`redis-py`) - Сервис для контроля за текущими пользовательскими соединениями (добавление/удаление/получение списка соединений, статистика)
4. **Presence** (`redis-py`) - Сервис для контроля за статусами онлайн у пользователей
5. **Service_updates** состоит из 2 компонентов:
    1. **Publisher** (`aio_pika`) - Отправляет в очередь все обновления по сервису (новые сообщения, обновления статусов доставки, обновления статусов онлайна, статус "печатает сообщение")
    2. **Listener** (`aio_pika, protobuf`) - Обрабатывает события, опубликованные `5.1`, и, при необходимости, рассылает уведомления/сообщения пользователям
6. **Storage** (`sqlalchemy`) - Модуль для хранения данных (работа с БД)

Модули могут быть запущены как все вместе, так и отдельными группами (`python cli.py run --help`).


## Флоу обработки сообщений

- Пользователь подключается к вебсокету, `chat`:
    - подтверждает соединение
    - аутентифицирует при помощи `auth`
    - добавляет соединение в список активных (через `connections`)
    - подписывается на обновления для этого соединения через `redis channel`

**Обработка нового сообщения:**

Пользователь отправляет новое сообщение
- `chat`:
    - валидирует сообщение, сохраняет в бд
    - отвечает пользователю об успешной доставке
    - отправляет сообщение в очередь rabbitmq (через `service_updates.publisher`)
- `service_updates.listener`:
    - получает сообщение из очереди
    - проверяет, кому необходимо доставить сообщения (используя `storage, presence, connections`)
    - публикует сообщения в необходимый `redis channel`
- `chat` на нужном сервере получает опубликованное сообщение и отправляет его клиенту

**Обработка статуса онлайн:**

- Подключенный к чату пользователь периодически отправляет сообщения `Activity` на сервер
- Даты активности пользователя запоминаются `presence` модулем
- `presence` модуль периодически проверяет изменения статусов онлайн, исходя из активностей
- При изменении статуса активности, `presence` отправляет сообщения в очередь через `service_updates.publisher`
- Далее следует примерно тот же алгоритм, что при обработке нового сообщения


## Возможный вариант деплоя

1. Несколько инстансов для Websockets соединений (`python cli.py run ws_server`)
2. Инстанс с HTTP API (`python cli.py run api_server`)
3. Несколько инстансов обработки событий (`python cli.py run worker`)
4. Один инстанс с проверкой статусов онлайна (`python cli.py run presence`)


# Тестирование

## Interactive TestClient

Есть возможность запустить интерактивного чат-клиента `python cli.py --log-level INFO client connect <user_id>`. Для успешной авторизации необходимо в настройках приложения отключить верификацию токена (`auth.verify_signature = False`)

В рамках сессии можно отправлять сообщения в указанный чат, менять чат, получать список чатов, получать изменения статусов доставки сообщений, получать изменения статусов онлайн других пользователей в чате, получать сообщения от других пользователей чата. Если получено новое сообщение от другого пользователя и пользователь находится в том же чате, для него автоматически выставляется отметка "получено"+"прочитано". Подробнее о возможностях можно узнать, введя `/help` в интерфейсе запущенного клиента

Интерфейс:
```bash
$ python cli.py --log-level INFO client connect <user_id>

    Commands:
    /help - show this message
    /online - go online
    /offline - go offline
    /chat <chat_id> - enter chat room
    /exitchat - exit chat room
    /chats - show all chats
    /t - imitate *typing in chat* behaviour
    *anytext* - Send message to the current chat

> /chat 1
$ Chat switched to 1
>
```

# Ссылки
1. [Репозиторий в GitLab (backend)](https://gitlab.fbsvc.bz/sl-constanta/backend/sportlevel-messenger)
2. [Страница в notion](https://www.notion.so/constanta/SL-Messenger-8f40dc2cb4ab426cb6b6fc30e48bb09a)


# TODOs
1. Добавить тесты
2. Подумать над вариантами определять статус онлайн пользователя (считать не только Activity, но и прочтение сообщения, отправку сообщения?)
3. Доработать db_filler
4. Кеширование счётчиков тикетов
5. Кеширование счётчиков непрочитанных по типу чата
6. InMemoryCacher.get_statistics нет профайлинга
7. 
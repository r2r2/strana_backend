# Методология gitflow на проекте


## Значение веток

- ```production```
  
  Основная и единственная ветка разработка. От неё создаются ветки новых задач, а также ветки хотфиксов.

## Работа над задачами, создание новых веток

1. Исполнитель создает ветку задачи от `production`. Ветка должна начинаться с названия задачи (это важно), например `strana_lk-101-...`
2. В название ветки добавляется короткое дополнение из 2-3 слов для того, чтобы не было необходимости держать в голове последовательности цифр и по названию ветки определять ее назначение. При этом название ветки не должно быть длинным и занимать слишком много места.
3. Названия коммитов: `strana_lk-101 Текстовое описание задачи` (можно скопировать из youtrack, для чего там есть специальная кнопка (два квадратика) около номера задачи).
   > Название коммита должно быть строго такого формата. Никаких подчеркиваний вокруг номера задачи быть не должно. Номер задачи, потом текст. Только в таком формате корректно работает парсинг ссылок на задачу в gitlab.
4. Задача разбивается на множетсов мелких МРов, каждый имеет часть реализации задачи и вливается по завершении логической цепочки.
5. "Уплотнение" коммитов в ветках перед отправкой задачи на Code Review приветствуется. Если в ходе работы над задачей были серии коммитов, которые уместно объединить в один, то стоит это сделать. Для этого можно воспользоваться инструментом ``Squash commits`` в IDE: выбрать нужные коммиты в списке и выбрать соответствующий пункт из контекстного меню, задав новому объединенному коммиту соответствующее наименование.
   > "Уплотнение" коммитов является рекомендацией и правилом хорошего тона, а не строгим требованием. Но зачастую уменьшение количества коммитов может оказаться полезным при "разруливании" некоторых специфичных ситуаций.
6. При необходимости исполнитель создаёт feature flag и закрывает изменения под feature flag. Feature flag не требуется при расширении, либо при `bugfix`. Важно! Добавлять Feature flag при внесении изменений в существующий код, функциональность.
7. Оформление MR: по мере готовности задачи исполнитель создает **Один** MR – в ветку `production`. Включает feature flag на dev окружении для тестирование при необходимости.
    1. Наименование MR – `strana_lk-101 Текстовое описание задачи` (можно скопировать из youtrack, для чего там есть специальная кнопка около номера задачи).
       > Название MR должно быть строго такого формата. Никаких подчеркиваний вокруг номера задачи быть не должно. Номер задачи, потом текст. Только в таком формате корректно работает парсинг ссылок на задачу в gitlab.
    2. Важно! При создании MR необходимо корректно заполнять **лейблы** в соответствии с назначением реквеста. MR, создаваемые для *hotfix*  должны помечаться как `bugfix`.
    3. Все MR проливаются в одну ветку `production`. Feature flags требуется только для изменений существующего кода.

## Релиз

Релиз проходит путём включения\выключения feature flag на нужном окружении.
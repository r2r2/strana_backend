Для выпуска новой версии требуется сделать:

1. Закоммитить изменения в dev/master
2. Нажать play на стейджах с деплоем 

Для рестарта контейнера при изменении конфига:

1. Перейти в Deployments > Environments > test(production)
2. Выбрать последний удачный деплой
3. Нажать на кнопку `Re-deploy environment`
4. Подтвердить намерение

Для rollback'a изменений

1. Перейти в Deployments > Environments > test(production)
2. Выбрать нужный деплой 
3. Нажать кнопку `Rollback environment`
4. Подтвердить намерение

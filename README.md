# Страна Девелопмент

> ### Info:
> 
> > #### [TZ](https://docs.google.com/document/d/1RawsXArHg90TCpl2ev2jGgHS5bRGM7vPc8OQIdF7r6g/edit#)
>
> > #### [Production](https://msk.strana.com/) 
> 
> > #### [Development](https://strana.strana.com/)
> 
> > #### [Documentation](https://lk.strana.idacloud.ru/api/docs/)
>
> > #### [Структура проекта](https://docs.google.com/document/d/1mNYIEnMtVm5UQJHZ4k2pJVspPxObzXgTS2xrWtl-qn8/edit?usp=sharing)

> ### Данные для документации:
> ><strong>stranadocs:ida223322</strong>


> [Фронтенд ENV](https://gitlab.idacloud.ru/Idaproject/strana/strana/-/blob/master/frontends/README.md)
> ### Назначение директорий:
> 
> >[Фронтенд ЛК - lk](https://gitlab.idacloud.ru/Idaproject/strana/strana/-/tree/master/lk)
> 
> >[Бэкенд ЛК - cabinet](https://gitlab.idacloud.ru/Idaproject/strana/strana/-/tree/master/cabinet)
> 
> >[Бэкенд портала - backend](https://gitlab.idacloud.ru/Idaproject/strana/strana/-/tree/master/backend)
> 
> >[Фронтенд портала - frontend](https://gitlab.idacloud.ru/Idaproject/strana/strana/-/tree/master/frontend)

> ### Боевые сервисы:
> > [Flower](https://msk.strana.com/flower)
> 
> > [Imgproxy](https://imgproxy.strana.com)

> ### Девелоп сервисы:
> > [Flower](https://strana.idacloud.ru/flower)
> 
> > [Imgproxy](https://imgproxy.strana.idacloud.ru)


<details>
<summary>acme.sh</summary>

<p>

```sh
acme.sh --issue \
 -d www.strana.com \
 -d strana.com \
 -d msk.strana.com \
 -d lk.strana.com \
 -d mo.strana.com \
 -d tmn.strana.com \
 -d ekb.strana.com \
 -d spb.strana.com \
 -d imgproxy.strana.com \
-w /var/www/local_static --config-home /acme.sh
```
</p>

<p>

```sh
acme.sh --install-cert \
 -d www.strana.com \
 -d strana.com \
 -d msk.strana.com \
 -d lk.strana.com \
 -d mo.strana.com \
 -d tmn.strana.com \
 -d ekb.strana.com \
 -d spb.strana.com \
 -d imgproxy.strana.com \
--config-home /acme.sh --key-file /etc/nginx/certs/key.pem --fullchain-file /etc/nginx/certs/cert.pem --reloadcmd "nginx -s reload"
```
</p>

</details>

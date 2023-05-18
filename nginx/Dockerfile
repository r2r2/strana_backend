FROM itpro72.ru:5050/strana-artw/strana-backend/nginx_vts_module:latest
EXPOSE 80/tcp
EXPOSE 443/tcp
EXPOSE 8888/tcp
ENV ENVIRONMENT development
ENV TLS_MODE off
ENV SITE_HOST localhost
ENV LK_SITE_HOST lk.localhost
ENV DOCS_SITE_HOST docs.strana.artw.dev
ENV BROKER_LK_SITE_HOST broker.localhost
ENV IMGPROXY_SITE_HOST imgproxy.localhost
ENV DEFAULT_SITE_HOST portal.localhost
ENV PANEL_SITE_HOST panel.localhost
ENV REDIRECT_DOMAINS_MSK msk-wow.ru
ENV DOCS_HTPASSWD artw:$apr1$CVqYHz4M$XbvY0c9uPgrQH7BYv0RYA0
RUN apk add --no-cache esh curl openssl
RUN curl https://get.acme.sh | sh
RUN ln -s  /root/.acme.sh/acme.sh  /usr/local/bin/acme.sh
#RUN rm /etc/nginx/conf.d/default.conf
RUN mkdir /etc/nginx/conf.d
COPY broker_configs/broker_config.esh /etc/nginx/
COPY imgproxy_configs/imgproxy_config.esh /etc/nginx/
COPY portal_configs/portal_backend_config portal_configs/portal_config.esh /etc/nginx/
COPY cabinet_configs/cabinet_admin_config cabinet_configs/cabinet_ws_config cabinet_configs/cabinet_emails_config cabinet_configs/cabinet_backend_config cabinet_configs/cabinet_docs_config cabinet_configs/cabinet_redoc_config cabinet_configs/cabinet_config.esh /etc/nginx/
COPY redirects_map.conf nginx.conf.esh exporters.conf ssl_params ssl_params_broker ssl_params_panel ssl_params_redirect /etc/nginx/
COPY panel_configs/panel_backend_config panel_configs/panel_config.esh /etc/nginx/
COPY docs_configs/docs_config_backend docs_configs/docs_config.esh /etc/nginx/
COPY error502 /etc/nginx/error502 
COPY redirect_domains_config/redirect_domains_config.esh /etc/nginx/

CMD ["/bin/sh", "-c", "echo $LK_HTPASSWD >/etc/nginx/.htpasswd  \
    && esh -o /etc/nginx/imgproxy_config /etc/nginx/imgproxy_config.esh \
    && esh -o /etc/nginx/portal_config /etc/nginx/portal_config.esh \
    && esh -o /etc/nginx/cabinet_config /etc/nginx/cabinet_config.esh \
    && esh -o /etc/nginx/broker_config /etc/nginx/broker_config.esh \
    && esh -o /etc/nginx/conf.d/nginx.conf /etc/nginx/nginx.conf.esh \
    && esh -o /etc/nginx/panel_config /etc/nginx/panel_config.esh \
    && esh -o /etc/nginx/docs_config /etc/nginx/docs_config.esh \
    && esh -o /etc/nginx/redirect_domains_config /etc/nginx/redirect_domains_config.esh \
    && exec nginx -g 'daemon off;'" \
]

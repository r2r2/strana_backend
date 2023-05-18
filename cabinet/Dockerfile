ARG PYTHON_CABINET
FROM ${PYTHON_CABINET} AS PYTHON_CABINET
ENV TZ Europe/Moscow
COPY / /app/
RUN chmod +x entrypoint.* \
    && cat /app/certs-sber/Cert_CA.pem >> /etc/ssl/certs/ca-certificates.crt \
    && cp /app/certs-sber/russian_trusted_sub_ca_pem.crt /usr/share/ca-certificates/mozilla/ \
    && cp /app/certs-sber/russian_trusted_root_ca_pem.crt /usr/share/ca-certificates/mozilla/ \
    && ln -s /usr/share/ca-certificates/mozilla/russian_trusted_sub_ca_pem.crt /etc/ssl/certs/russian_trusted_sub_ca_pem.pem \
    && ln -s /usr/share/ca-certificates/mozilla/russian_trusted_root_ca_pem.crt /etc/ssl/certs/russian_trusted_root_ca_pem.pem

ENTRYPOINT ["sh", "entrypoint.sh"]

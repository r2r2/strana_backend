ARG PYTHON_ADMIN
FROM ${PYTHON_ADMIN} AS PYTHON_ADMIN
COPY / /app/
RUN chmod +x entrypoint.*
ENTRYPOINT ["sh", "entrypoint.sh"]
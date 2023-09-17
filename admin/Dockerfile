ARG PYTHON_ADMIN
FROM ${PYTHON_ADMIN} AS PYTHON_ADMIN
ENV PATH="${PATH}:/root/.local/bin"
COPY / /app/
RUN chmod +x entrypoint.*
ENTRYPOINT ["sh", "entrypoint.sh"]

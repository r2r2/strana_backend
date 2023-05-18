ARG PYTHON_BACKEND
FROM ${PYTHON_BACKEND} AS PYTHON_BACKEND
COPY / /app/
RUN chmod +x entrypoint.*
ENTRYPOINT ["sh", "entrypoint.sh"]
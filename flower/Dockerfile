FROM python:3.8-alpine
RUN apk add --no-cache ca-certificates && update-ca-certificates
RUN pip install --no-cache-dir redis flower celery==4.4.7
ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1
EXPOSE 5555
USER root
ENTRYPOINT ["flower"]

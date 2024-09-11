ARG PYTHON_VERSION=3.12.0-20.12.0-node

FROM nexus.fbsvc.bz/constanta_docker/base-sl-python:${PYTHON_VERSION} as requirements-stage

ARG POETRY_VERSION=1.8.2

ARG POETRY_EXPORT_VERSION=1.7.1
ARG POETRY_SOURCE_EXPORT_VERSION=1.0.0
ARG DOCKER_PYTHON_REG=nexus.fbsvc.bz/repository/constanta_python/simple/

WORKDIR /tmp

RUN pip install \
    --no-cache-dir \
    --no-input \
    poetry==${POETRY_VERSION} \
    poetry-plugin-export==${POETRY_EXPORT_VERSION}

RUN --mount=type=secret,id=netrc,target=/root/.netrc \
    pip install \
    --no-cache-dir \
    --no-input \
    --no-build-isolation \
    --index-url https://${DOCKER_PYTHON_REG} \
    poetry-plugin-source-export==${POETRY_SOURCE_EXPORT_VERSION}

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export-by-source


FROM nexus.fbsvc.bz/constanta_docker/base-sl-python:${PYTHON_VERSION}

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /src/sportlevel-messenger

ARG HTTP_PORT=8080

ARG DOCKER_PYTHON_REG=nexus.fbsvc.bz/repository/constanta_python/simple/

RUN apt update && apt install libmagic1 -y

COPY --from=requirements-stage /tmp/pypi.requirements.txt /src/sportlevel-messenger/pypi.requirements.txt

RUN pip install \
    --no-cache-dir \
    --no-input \
    -r pypi.requirements.txt

RUN pip install \
    --no-cache-dir \
    --no-input \
    poetry-core wheel

COPY --from=requirements-stage /tmp/nexus.requirements.txt /src/sportlevel-messenger/nexus.requirements.txt

RUN --mount=type=secret,id=netrc,target=/root/.netrc \
    pip install \
    --no-cache-dir \
    --no-input \
    --no-build-isolation \
    --index-url https://${DOCKER_PYTHON_REG} \
    -r nexus.requirements.txt

RUN pip uninstall -y poetry-core wheel

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE ${HTTP_PORT}

RUN chmod +x ./scripts/entrypoint.sh

CMD ./scripts/entrypoint.sh

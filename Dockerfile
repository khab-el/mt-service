FROM python:3.8
# build args
ARG repository_id=trade-bot-api
ARG commit_id
ARG tag_name

# build-time env
ENV REPOSITORY_ID ${repository_id}
ENV GIT_COMMIT_ID ${commit_id}
ENV GIT_TAG_NAME ${tag_name}

# Server
WORKDIR /app
COPY src /app/src
COPY pyproject.toml poetry.lock ./

RUN pip3 install poetry && poetry install

COPY migrations /app/migrations

EXPOSE 8000
# TODO mv to entrypoint helm chart
#RUN poetry run migrate

ENTRYPOINT poetry run start

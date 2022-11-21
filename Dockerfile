FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# set the working directory
WORKDIR /app

# install dependencies
RUN pip install --no-cache-dir --upgrade poetry
COPY ./pyproject.toml ./pyproject.toml /app/
RUN poetry install

# copy the scripts to the folder
COPY . /app

# start the server
CMD /bin/bash

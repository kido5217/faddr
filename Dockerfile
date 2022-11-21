FROM python:3.10-slim

# Create nonroot user
ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Install git and other dev tools
RUN apt update && apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    git

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry settings
    POETRY_NO_INTERACTION=1 \
    POETRY_INSTALLER_MAX_WORKERS=10 \
    POETRY_HOME="/poetry" \
    POETRY_VERSION=1.2.2

ENV PATH="$POETRY_HOME/bin:$PATH"

# set the working directory
WORKDIR /app

# install dependencies
RUN curl -sSL https://install.python-poetry.org | python3 -

USER $USERNAME

COPY ./pyproject.toml /app/
COPY ./*poetry.lock /app/
RUN poetry install

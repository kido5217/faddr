FROM python:3.10-slim

# Set the working directory
WORKDIR /workspace

# Install git and other dev tools
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        build-essential \
        gpg \
        curl \
        git \
        sqlite3 \
        openssh-client \
        pinentry-tty \
        pinentry-curses \
        jq \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install fish shell
RUN echo 'deb http://download.opensuse.org/repositories/shells:/fish:/release:/3/Debian_11/ /' | tee /etc/apt/sources.list.d/shells:fish:release:3.list && \
    curl -fsSL https://download.opensuse.org/repositories/shells:fish:release:3/Debian_11/Release.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/shells_fish_release_3.gpg > /dev/null && \
    apt-get update && \
    apt-get install --no-install-recommends -y \
        fish \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install starship
RUN curl -sS https://starship.rs/install.sh | sh -s -- --force

# Config nonroot user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create nonroot user
RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME -s /usr/bin/fish && \
    chown -R $USERNAME /workspace
USER $USERNAME

# Setup shell
RUN mkdir -p ~/.config/fish/functions/ && \
    echo 'starship init fish | source' >> ~/.config/fish/config.fish && \
    echo 'command_timeout = 5000' >> ~/.config/starship.toml && \
    printf '[container]\ndisabled = true' >> ~/.config/starship.toml
COPY --chown=$USER_UID:$USER_GID .devcontainer/configs/*.fish /home/$USERNAME/.config/fish/functions/

# Create folder for vscode extensions volume mount
RUN mkdir -p /home/$USERNAME/.vscode-server/extensions

# Set python-related envs
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
    POETRY_VERSION=1.3.2

# Install and config Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/home/$USERNAME/.local/bin:$PATH"
RUN poetry config virtualenvs.in-project true

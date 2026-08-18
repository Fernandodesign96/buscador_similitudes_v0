FROM python:3.11-slim
RUN useradd -m -u 1000 user
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:/home/user/.bun/bin:$PATH
RUN curl -fsSL https://bun.sh/install | bash
WORKDIR $HOME/app
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
COPY --chown=user . .
RUN cd frontend && bun install && bun run build
EXPOSE 7860
CMD bash -c "gunicorn api:app --bind 127.0.0.1:5001 --timeout 120 & cd frontend && bun run start -- --port 7860 --hostname 0.0.0.0"
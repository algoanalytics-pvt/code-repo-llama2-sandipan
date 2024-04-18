FROM python:3.10-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*\
    python3-pip

COPY requirements.txt .
COPY create_embed.py ./

RUN pip3 install -r requirements.txt
CMD ["python3","create_embed.py"]

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
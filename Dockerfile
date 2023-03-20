FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /litra

COPY ./app/requirements.txt .

RUN pip install -r requirements.txt

COPY . /litra/

CMD ["python3.11", "app/app.py"]
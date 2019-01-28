FROM python:3.6.5

RUN apt-get update                             \
        && apt-get install -y --no-install-recommends \
        ca-certificates curl firefox               \
        && rm -fr /var/lib/apt/lists/*                \
        && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz | tar xz -C /usr/local/bin \
        && apt-get purge -y ca-certificates curl

RUN mkdir /alibaba-crawler
WORKDIR /alibaba-crawler
COPY . ./

RUN pip -r requirements.txt

CMD ["python", "app.py"]

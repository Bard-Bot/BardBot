FROM python:3.8

RUN apt-get update && \
    apt-get install -y \
    opus-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /bot

COPY requirements.txt /bot

RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY cogs /bot/cogs
COPY lib /bot/lib
COPY bard.py /bot
COPY bot.py /bot
COPY .env /bot
COPY bard-bot-firestore.json /bot

CMD ["python", "bard.py"]

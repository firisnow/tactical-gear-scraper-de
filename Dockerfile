FROM python:latest
COPY requirements.txt .
COPY src src
RUN pip install -r requirements.txt
CMD "python" "src/telegram_bot.py"

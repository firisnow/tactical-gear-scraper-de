FROM python:latest
COPY *.py ./
RUN pip install -r requirements.txt
CMD "python" "telegram_bot.py"

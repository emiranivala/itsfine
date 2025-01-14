FROM python:3.10.8-slim-buster
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Use supervisord to manage both processes
RUN apt-get update && apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

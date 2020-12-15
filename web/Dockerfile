FROM python:3.9.1-buster
WORKDIR   /usr/src/app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN ['python', 'app.py']
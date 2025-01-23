FROM python:3.10-slim-buster

COPY apt-sources.list /etc/apt/sources.list
RUN apt-get update && apt-get install -y libpq-dev build-essential
RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . .
EXPOSE 8000
CMD \
    python manage.py migrate && \
    python manage.py runserver --noreload 0.0.0.0:8000

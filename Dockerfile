FROM python:3.12

RUN mkdir /app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --upgrade pip


# Dépendances
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . /app/

EXPOSE 8000

# Ultra simple : migrate puis runserver
CMD sh -c "python manage.py makemigrations --noinput && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"
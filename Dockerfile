FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile

COPY . /app/

WORKDIR /app/autodealer-backend

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
FROM python:3.7.3
WORKDIR /app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

RUN pip install pipenv
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-credentials.json

COPY . .

CMD ["python", "main.py"]

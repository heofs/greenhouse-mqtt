FROM python:3.7.2
WORKDIR /app
COPY Pipfile Pipfile
COPY Pipfile.lock Pipefile.lock
RUN pip install pipenv
RUN pipenv install
COPY . .
CMD ["python", "main.py"]
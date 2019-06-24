FROM python:3.7.2
# WORKDIR /app
RUN pip3 install pipenv
RUN set -ex && mkdir /app

COPY main.py /app/main.py
WORKDIR /app
ONBUILD COPY Pipfile Pipfile
ONBUILD COPY Pipfile.lock Pipfile.lock
ONBUILD RUN set -ex && pipenv install --deploy --system

CMD ["python", "main.py"]

# COPY Pipfile Pipfile
# COPY Pipfile.lock Pipefile.lock
# RUN pipenv install
# COPY . .
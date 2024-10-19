FROM python:3

WORKDIR /src

COPY backend_requirements.txt .

RUN pip install --no-cache-dir -r backend_requirements.txt

COPY ./src /app/src

WORKDIR /app/src

CMD [ "python", "main.py" ]
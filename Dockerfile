FROM python:3

WORKDIR /app

COPY backend_requirements.txt .

RUN pip install --no-cache-dir -r backend_requirements.txt

COPY ./src /app

EXPOSE 5001

VOLUME /app/instance

CMD [ "python", "main.py" ]
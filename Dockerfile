FROM python:3.9

WORKDIR /code
COPY requirements.txt /code
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP ./api/app.py
ENV FLASK_ENV production
ENV FLASK_RUN_PORT 8000
ENV FLASK_RUN_HOST 0.0.0.0

EXPOSE 8000

CMD ["flask", "run"]
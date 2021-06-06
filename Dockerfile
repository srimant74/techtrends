FROM python:2.7

WORKDIR /app

COPY ./techtrends /app

RUN pip install -r /app/requirements.txt

RUN python /app/init_db.py

EXPOSE 3111

CMD [ "python", "app.py" ]

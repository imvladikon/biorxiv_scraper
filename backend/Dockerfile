FROM python:3.8
COPY . /backend
WORKDIR /backend
RUN pip install -r requirements.txt
ENV FILENAME="cars.csv"
CMD python "/backend/app.py" --type='backend' & python "/backend/app.py" --type='scraper'
ENV FLASK_APP app.py
#CMD flask run --host=0.0.0.0

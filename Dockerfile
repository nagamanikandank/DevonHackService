COPY requirements.txt /

WORKDIR /

RUN pip install -r ./requirements.txt --no-cache-dir

ENV FLASK_APP=application.py
CMD flask run -h 0.0.0.0 -p 5000
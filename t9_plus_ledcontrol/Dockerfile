FROM python:3

RUN apt-get update \
    && apt-get install python3 -y \
    #python-setuptools \
    python3-pip \
    && apt-get clean \
    && apt-get autoremove


ADD . /home/App
WORKDIR /home/App
COPY requirements.txt ./
COPY . .

RUN pip install -r requirements.txt

VOLUME ["/data"]
EXPOSE 5090 5090
CMD ["python" ,"app.py"]
FROM python:3.8.2-alpine3.11
WORKDIR /app
RUN apk add git gcc musl-dev libffi-dev libxml2-dev libxslt-dev libressl-dev
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD vsphere_filesd.py /app/
CMD ["python", "/app/vsphere_filesd.py"]

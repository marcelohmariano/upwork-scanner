FROM python:3-alpine

WORKDIR /usr/src/app/

COPY upwork upwork
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh && mkdir -p /scan/

VOLUME /scan/
ENTRYPOINT ["./docker-entrypoint.sh"]

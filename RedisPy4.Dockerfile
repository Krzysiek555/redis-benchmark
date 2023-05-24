FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

RUN mkdir /app
WORKDIR /app
RUN pip install redis==4.5.5 hiredis==2.2.3 numpy==1.23.3
COPY minimal_redis_benchmark.py /app/

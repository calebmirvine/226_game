FROM python:3.12

RUN mkdir /server

COPY *.py /server/

CMD [ "python3.12", "/server/main.py" ]


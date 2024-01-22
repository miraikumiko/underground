FROM python

WORKDIR /opt
COPY . /opt

RUN pip install -U pip
RUN pip install -r requirements/base.txt

CMD alembic upgrade head; python run.py

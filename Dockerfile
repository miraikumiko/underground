FROM alpine

WORKDIR /opt
COPY . /opt

RUN apk add gcc pkgconf libvirt-dev libc-dev python3-dev py3-pip
RUN pip install --break-system-packages -U pip
RUN pip install --break-system-packages -r requirements/base.txt

CMD alembic upgrade head; python run.py

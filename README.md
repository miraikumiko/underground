# underground.pm

Privacy hosting

## Dependencies

* python
* pip
* redis
* nginx
* ssh
* cronie
* openrc/systemd
* Docker (Optional)

## Installing

Clone repository into `/var/www/underground.pm-be`

## Setup

### App

For first edit environment varibles:

`cp .env.example .env`

And install requirements:

```
python -m venv venv
. venv/bin/activate
pip install -U pip
pip install -r requirements/base.txt
```

Or you can build Docker image:

`docker buildx build -t underground.pm-be .`

### Cronie

`*/15 * * * * /var/www/underground.pm-be/venv/bin/python /var/www/underground.pm-be/run.py -X`

### OpenRC

`cp contrib/openrc/underground.pm-be /etc/init.d/underground.pm-be`

### Systemd

`cp contrib/systemd/underground.pm-be.service /etc/systemd/system/underground.pm-be.service`

### Nginx

```
cp contrib/nginx/sites-available/underground.pm-be.conf /etc/nginx/sites-available/underground.pm-be.conf
ln -s /etc/nginx/sites-available/underground.pm-be.conf /etc/nginx/sites-enabled/underground.pm-be.conf
```

## Start

### OpenRC

```
rc-update add postgresql default
rc-update add redis default
rc-update add underground.pm-be default
rc-update add nginx default

rc-service postgresql start
rc-service redis start
rc-service underground.pm-be start
rc-service nginx start
```

### Systemd

`systemctl enable --now postgresql redis underground.pm-be nginx`

## Testing

Install dependencies:
`pip install -r requirements/dev.txt`

And run tests:
`pytest`

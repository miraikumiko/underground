# underground.pm

Privacy hosting

## Dependencies

* python
* pip
* redis
* nginx
* ssh
* cronie
* libvirt
* monero
* openrc/systemd

## Installing

Clone repository into `/var/www/underground.pm`

## Setup

### App

For first edit environment varibles:

`cp .env.example .env`

And install requirements:

```
python -m venv venv
. venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### Cronie

`*/15 * * * * /var/www/underground.pm/venv/bin/python /var/www/underground.pm/run.py`

### OpenRC

`cp contrib/openrc/underground.pm /etc/init.d/underground.pm`

### Systemd

`cp contrib/systemd/underground.pm.service /etc/systemd/system/underground.pm.service`

### Nginx

```
cp contrib/nginx/sites-available/underground.pm.conf /etc/nginx/sites-available/underground.pm.conf
ln -s /etc/nginx/sites-available/underground.pm.conf /etc/nginx/sites-enabled/underground.pm.conf
```

## Start

### OpenRC

```
rc-update add libvirtd default
rc-update add redis default
rc-update add underground.pm default
rc-update add nginx default

rc-service libvirtd start
rc-service redis start
rc-service underground.pm start
rc-service nginx start
```

### Systemd

`systemctl enable --now libvirtd redis underground.pm nginx`

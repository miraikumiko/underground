#!/bin/sh

/var/www/underground.pm/venv/bin/python /var/www/underground.pm/run.py -c "$1"
logger "Transaction with txid $1 has been recived"

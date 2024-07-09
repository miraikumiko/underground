#!/bin/sh

python /var/www/underground.pm/run.py -C "$1"
logger "Transaction with txid $1 has been recived"

#!/bin/sh

monero-wallet-rpc --wallet-file "/var/lib/wallets/underground.pm" --password "password" --rpc-bind-port "20000" --daemon-address "node.sethforprivacy.com:18089" --trusted-daemon --rpc-login "underground:underground" --log-file "/dev/null" --tx-notify "/var/www/underground.pm-be/contrib/monero/tx %s"

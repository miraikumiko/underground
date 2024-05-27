#!/bin/sh

monero-wallet-rpc --wallet-file "/var/lib/wallets/underground.pm" --password "password" --rpc-bind-port "20000" --daemon-address "127.0.0.1:18081" --trusted-daemon --rpc-login "underground:underground" --log-file "/dev/null" --tx-notify "/var/www/underground.pm-be/contrib/monero/tx %s"

#!/bin/sh

monero-wallet-rpc --wallet-file "$MONERO_WALLET_PATH" --password "$MONERO_WALLET_PASSWORD" --daemon-address "$MONERO_DAEMON_ADDRESS" --trusted-daemon --rpc-bind-port "$MONERO_RPC_PORT" --rpc-login "$MONERO_RPC_LOGIN" --log-file "$MONERO_RPC_LOG_PATH" --tx-notify "$MONERO_TX_PATH %s"

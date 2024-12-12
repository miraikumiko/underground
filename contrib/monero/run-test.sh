#!/bin/sh

monero-wallet-rpc --testnet --wallet-file "$MONERO_TEST_WALLET_PATH" --password "$MONERO_TEST_WALLET_PASSWORD" --daemon-address "$MONERO_TEST_DAEMON_ADDRESS" --trusted-daemon --rpc-bind-port "$MONERO_TEST_RPC_PORT" --rpc-login "$MONERO_TEST_RPC_LOGIN" --log-file "$MONERO_TEST_RPC_LOG_PATH" --tx-notify "$MONERO_TEST_TX_PATH %s"

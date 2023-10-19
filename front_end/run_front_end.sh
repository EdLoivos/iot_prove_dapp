#!/bin/bash

# Script to run the fron-end (local)

mkdir -p ./public/ABI

# copy localhost's (hardhat) ABI to public/ABI directory
docker cp iot_prove_dapp-hardhat-1:/opt/cartesi/share/blockchain/localhost.json ./public/ABI/
if [ $? != 0 ]
then
    echo "Error: Must run Back-End first"
    exit 1
fi

# get dapp.address
if [ `grep -c "DAPP_ADDRESS=" .env` == 0 ]
then
    echo -ne "\nDAPP_ADDRESS=\"" >> .env
    cat ../deployments/localhost/dapp.address >> .env
    echo -n "\"" >> .env
fi

# run the web server
USE_LOCAL_ACCOUNT=1 node app.js

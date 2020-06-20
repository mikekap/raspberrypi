#!/bin/bash
set -xeo pipefail

trap "exit" INT TERM
trap "kill 0" EXIT

get_certificate() {
    echo "Getting certificate for domain $1 on behalf of user $2"
    PRODUCTION_URL='https://acme-v02.api.letsencrypt.org/directory'
    STAGING_URL='https://acme-staging-v02.api.letsencrypt.org/directory'

    if [ "${IS_STAGING}" = "1" ]; then
        letsencrypt_url=$STAGING_URL
        echo "Staging ..."
    else
        letsencrypt_url=$PRODUCTION_URL
        echo "Production ..."
    fi

    echo "running certbot ... $letsencrypt_url $1 $2"
    certbot certonly --agree-tos --keep -n --text --email $2 --server \
        $letsencrypt_url -d $1 --http-01-port 1337 \
        --standalone --preferred-challenges http-01 --debug
}

run_certbot() {
get_certificate "home.kaplinskiy.com" "mike.kaplinskiy@gmail.com"
}

if [ ! -f "/etc/letsencrypt/live/home.kaplinskiy.com/privkey.pem" ]; do
cp /etc/ssl/certs/ssl-cert-snakeoil.pem /etc/letsencrypt/live/home.kaplinskiy.com/fullchain.pem
cp /etc/ssl/private/ssl-cert-snakeoil.key /etc/letsencrypt/live/home.kaplinskiy.com/privkey.pem
fi

nginx &
NGINX_PID=$!

while [ true ]; do
    # Make sure we do not run container empty (without nginx process).
    # If nginx quit for whatever reason then stop the container.
    # Leave the restart decision to the container orchestration.
    if ! ps aux | grep --quiet [n]ginx ; then
        exit 1
    fi

    # Run certbot, tell nginx to reload its config
    echo "Run certbot"
    run_certbot || echo "Certbot failed; ignoring"
    kill -HUP $NGINX_PID

    # Sleep for 1 week
    sleep 604810 &
    SLEEP_PID=$!

    # Wait for 1 week sleep or nginx
    wait -n "$SLEEP_PID" "$NGINX_PID"
done

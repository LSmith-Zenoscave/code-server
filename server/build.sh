#! /bin/bash
if [ -f .env ] ; then
    eval "$(sed -E 's/^\s*([^#].*)/export \1/g' .env)"
else
    echo "!!! Running without an environment configuration !!!"
    echo "!!! Make sure you copy .env-sample repo root to server/.env !!!"
fi

for template in $(find . -type f -name '*.template') ; do
    file="$(dirname ${template})/$(basename ${template} .template)"
    rm ${file}
    envsubst < ${template} > ${file}
done
touch acme/acme.json
chmod 0600 acme/acme.json
docker rm -f $(docker ps -aq -f=name=\^code-\*) || true
docker-compose down
find ./route_conf -type f ! -name 'main.toml' -a -name '*.toml' -delete
docker-compose up -d

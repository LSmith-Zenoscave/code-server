#!/usr/bin/env bash

docker-compose exec openldap /bin/bash -c \
    "/usr/bin/ldapadd -c -x -D \
        \"cn=${LDAP_ADMIN},dc=${DOMAIN_NAME_BASE},dc=${DOMAIN_NAME_TLD}\" \
        -w ${LDAP_PASSWORD} \
        -f /tmp/ldap/*.ldif \
        -H ldap://openldap"

ARG ODOO_VERSION=latest
FROM odoo:${ODOO_VERSION}

USER root
WORKDIR /

RUN apt-get update && apt-get install -y procps net-tools vim gnupg

# grab gosu for easy step-down from root
RUN gpg --keyserver pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
        && curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.10/gosu-$(dpkg --print-architecture)" \
        && curl -o /usr/local/bin/gosu.asc -SL "https://github.com/tianon/gosu/releases/download/1.10/gosu-$(dpkg --print-architecture).asc" \
        && gpg --verify /usr/local/bin/gosu.asc \
        && rm /usr/local/bin/gosu.asc \
        && chmod +x /usr/local/bin/gosu

COPY ./entrypoint.* /
COPY ./nginx.conf.sigil /
COPY ./odoo.conf /etc/odoo/

# Copy Odoo addons
COPY ./addons/ /mnt/extra-addons/

EXPOSE 8069 8072

ENTRYPOINT ["/entrypoint.sh"]

CMD ["odoo"]

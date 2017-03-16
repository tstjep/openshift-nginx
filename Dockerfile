from nginx:latest
ADD nice2.conf.template /etc/nginx/conf.d/
ADD nginx.conf /etc/nginx/
RUN chmod -R 777 /var/log/nginx /var/cache/nginx /var/run \
     && chgrp -R 0 /etc/nginx \
     && chmod -R g+rwX /etc/nginx \
     && rm /etc/nginx/conf.d/default.conf
EXPOSE 8080
ENTRYPOINT true ${UPSTREAM_HOST:?environment variable must be set} \\
     && sed s/{{UPSTREAM_HOST}}/$UPSTREAM_HOST/g </etc/nginx/conf.d/nice2.conf.template >/etc/nginx/conf.d/nice2.conf \
     && nginx -g 'daemon off;'

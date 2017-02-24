from nginx:latest
ADD nice2.conf /etc/nginx/conf.d/
RUN chmod -R 777 /var/log/nginx /var/cache/nginx /var/run \
     && chgrp -R 0 /etc/nginx \
     && chmod -R g+rwX /etc/nginx
EXPOSE 8080

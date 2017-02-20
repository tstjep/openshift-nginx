from nginx:latest
ADD nice2.conf /etc/nginx/conf.d/
RUN chmod -R 777 /var/log/nginx /var/cache/nginx/ /var/run/ \
     && chmod 644 /etc/nginx/*
EXPOSE 8080

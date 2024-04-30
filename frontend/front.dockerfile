FROM nginx:1.25.4

WORKDIR /usr/share/nginx/html

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./index.html /usr/share/nginx/html
COPY ./styles.css /usr/share/nginx/html
COPY ./index.js /usr/share/nginx/html

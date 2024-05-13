FROM nginx:1.25.4

WORKDIR /usr/share/nginx/html

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./index.html /usr/share/nginx/html
COPY ./styles.css /usr/share/nginx/html
COPY ./simplewebauthn-browser.4.1.0.umd.min.js /usr/share/nginx/html
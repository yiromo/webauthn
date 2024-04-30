FROM nginx:1.25.4

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY . /usr/share/nginx/html

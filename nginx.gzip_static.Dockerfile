FROM nginx:alpine AS nginx
    EXPOSE 80
    WORKDIR /usr/share/nginx/html

    COPY . .

    RUN sed -i'' -e 's/#gzip  on;/gzip  on;  gzip_static  on;  gzip_types text\/plain text\/css application\/javascript application\/json application\/x-javascript text\/xml application\/xml application\/xml+rss text\/javascript;  gzip_vary on; /g' /etc/nginx/nginx.conf
    RUN find . -type f \
            -iname '*.html' \
        -or -iname '*.css' \
        -or -iname '*.svg' \
        -or -iname '*.js' \
        -or -iname '*.json' \
        -or -iname '*.xml' \
        -or -iname '*.txt' \
        -or -iname '*.md' \
        -exec gzip -9 -k '{}' \;

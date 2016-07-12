# Homemade stupid simple fake dyndns

The purpose of this is to enable knowing what the public IP address is of a
raspberry pi sitting on a home network. It works in two parts. The client
simply sends a PUT request to the server. The server, upon receiving this
PUT request, takes note of the client's IP address and serves this up with GET
requests.

## How to make CentOS happy with this

I'm serving this with centos using uwsgi and nginx. IN order to make this
happen, you need a couple things first

* uwsgi
* uwsgi-plugin-python
* python-pip
* python-devel
* nginx
* gcc(maybe?)

The high level architecture is as such. python files are in /opt/piip. When you
install uwsgi, it installs it in emperor mode. In order to deploy your apps,
you need to add an appropriate .ini file to `/etc/uwsgi.d/`. This file is
included as piip.ini. uwsgi will create a socket in /run/uwsgi called
piip.sock. Nginx will use this socket to communicate with the uwsgi process.
Because uwsgi creates this socket and nginx has to consume it, we need to run
nginx as the uwsgi user. I did this by changing the user line as the top of the
nginx conf file. I also had to disable the default nginx config and adding a
simple config for just the uwsgi server.  Examples below. I also created a
virtual environment with flask. The virtualenv is included in the gitrepo.
Though it probbale shouldn't I followed
[this](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-centos-7)
guide for the most part, though I didn't write my own service file, I used the
uwsgi emperor mode instead.

```
user uwsgi;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    # Load modular configuration files from the /etc/nginx/conf.d directory.
    # See http://nginx.org/en/docs/ngx_core_module.html#include
    # for more information.
    include /etc/nginx/conf.d/*.conf;

    server {
        listen 80;
        server_name test.tehbp.net;

        location / {
            uwsgi_pass unix:/run/uwsgi/piip.sock;
            include uwsgi_params;
        }
    }

#    server {
#        listen       80 default_server;
#        listen       [::]:80 default_server;
#        server_name  _;
#        root         /usr/share/nginx/html;
#
#        # Load configuration files for the default server block.
#        include /etc/nginx/default.d/*.conf;
#
#        location / {
#        }
#
#        error_page 404 /404.html;
#            location = /40x.html {
#        }
#
#        error_page 500 502 503 504 /50x.html;
#            location = /50x.html {
#        }
#    }
}

```



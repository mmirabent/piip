# Homemade stupid simple fake dyndns

The purpose of this is to enable knowing what the public IP address is of a
raspberry pi sitting on a home network. It works in two parts. The client
simply sends a PUT request to the server. The server, upon receiving this
PUT request, takes note of the client's IP address and serves this up on a
control panel that displays all the tracked IP addresses

## Installing on a fresh CentOS or EL system

Prerequisites

* uwsgi
* uwsgi-plugin-python
* python-pip
* python-devel
* nginx
* gcc

If cloning from git, you'll need that too.

### Setting up the virtual environment

These commands are to set up the virtualenv that the app will run with. Thet
should be run within the app folder. I located this folder at /opt/piip.
Wherever you choose to locate the python code, run this there.

```
virtualenv --no-site-packages piipenv
source piipenv/bin/activate
pip install -r requirements.txt
deactivate
```

### Setting up the sqlite db

This should also be run from the same app folder as above

```
sqlite3 piip.db < schema.sql
```

### How to make CentOS happy with this

I'm serving this with centos using uwsgi and nginx. The high level architecture
is as such. python files are in /opt/piip. When you install uwsgi, it installs
it in emperor mode. In order to deploy your apps, you need to add an appropriate
.ini file to `/etc/uwsgi.d/`. This file is included as piip.ini. uwsgi will
create a socket in /run/uwsgi called piip.sock. Nginx will use this socket to
communicate with the uwsgi process.  Because uwsgi creates this socket and nginx
has to consume it, we need to run nginx as the uwsgi user. I did this by
changing the user line as the top of the nginx conf file.

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

```



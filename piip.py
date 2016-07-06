from flask import Flask
from flask import request
app = Flask(__name__)

remote_ip = None

@app.route('/', methods=['GET', 'PUT'])
def hello_world():
    if request.method == 'GET':
        global remote_ip
        if remote_ip == None:
            return ''
        else:
            return remote_ip
    elif request.method == 'PUT':
        global remote_ip 
        remote_ip = request.remote_addr
        return 'Put\'d'


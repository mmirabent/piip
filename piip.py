import os
import base64
import sqlite3
from flask import Flask, request, session,g,redirect,url_for,abort,render_template,flash,make_response
app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'piip.db'),
    SECRET_KEY='development_key',
    USERNAME='admin',
    PASSWORD='default'
))

# This is probably not needed, jussayin
#app.config.from_envvar('PIIP_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the current
       application context
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db();
    return g.sqlite_db


remote_ip = None

@app.route('/')
def show_ips():
    db = get_db()
    cur = db.execute('select title, ip from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_ips.html',entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    secret = base64.b32encode(os.urandom(25))
    db.execute('insert into entries (title, ip, secret) values (?, ?, ?)', [request.form['title'], '0.0.0.0',secret])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_ips'))

@app.route('/<string:title>', methods=['GET', 'PUT'])
def show_ip(title):
    if request.method == 'GET':
        if not session.get('logged_in'):
            abort(401)
        db = get_db()
        cur = db.execute('select title, ip, secret from entries where title = ?',[title])
        entry = cur.fetchone()
        return render_template('show_ip.html',entry=entry)
    
    elif request.method == 'PUT':
        if not request.authorization:
            abort(401)
        db = get_db()
        cur = db.execute('select title, ip, secret from entries where title = ?',[title])
        entry = cur.fetchone()

        if not entry['secret'] == request.authorization.password:
            abort(401)

        ip = request.remote_addr
        db.execute('UPDATE entries SET ip = ? WHERE title = ?', [ip,title])
        db.commit()
        return make_response("%s" % ip)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_ips'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_ips'))


"""
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
        """

@app.teardown_appcontext
def close_db(error):
    """CLoses the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


if __name__ == "__main__":
    application.run(host='0.0.0.0')


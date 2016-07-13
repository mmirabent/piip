import os
import sqlite3
from flask import Flask, request, session,g,redirect,url_for,abort,render_template,flash
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
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html',entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

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
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


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


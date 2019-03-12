from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bcrypt import Bcrypt
from functools import wraps

app = Flask(__name__,instance_relative_config=True)
bcrypt = Bcrypt(app)
app.config.from_pyfile('config.py')

app.secret_key = app.config['SECRET_KEY']

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
def welcome():
    return render_template('welcome_page.html')  

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')  

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        print(pw_hash)
        if request.form['username'] != 'admin' or not(bcrypt.check_password_hash(pw_hash, 'admin')):
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('welcome'))


if __name__ == '__main__':
    app.run(ssl_context='adhoc',debug=True)
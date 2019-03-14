from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bcrypt import Bcrypt
from cassandra.cluster import Cluster
from flask_cassandra import CassandraCluster
from functools import wraps
import requests
from twython import Twython
import pandas as pd

app = Flask(__name__,instance_relative_config=True)
cassandra = CassandraCluster()
bcrypt = Bcrypt(app)
app.config.from_pyfile('config.py')
app.config['CASSANDRA_NODES'] = ['localhost']  # can be a string or list of nodes
app.secret_key = app.config['SECRET_KEY'] #Needed for https
python_tweets = Twython(app.config['TWITTER_CONSUMER_KEY'],app.config['TWITTER_CONSUMER_SECRET'])
tweets={}

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

@app.route('/search_twitter', methods=['GET', 'POST'])
def search_twitter():    
    query = {'q': request.form['keyword'],  
        'result_type': 'popular',
        'count': 10,
        'lang': 'en',
        }
    dict_ = {'user': [], 'date': [], 'text': [], 'favorite_count': []}  
    for status in python_tweets.search(**query)['statuses']:  
        dict_['user'].append(status['user']['screen_name'])
        dict_['date'].append(status['created_at'])
        dict_['text'].append(status['text'])
        dict_['favorite_count'].append(status['favorite_count'])

    df = pd.DataFrame(dict_)  
    df.sort_values(by='favorite_count', inplace=True, ascending=False)  
    tweets = df.head(10).to_json(orient='records')
    flash(tweets)
    return (tweets)

@app.route('/add_todo', methods=['GET', 'POST'])
def add_todo():
    session = cassandra.connect()
    session.set_keyspace("todo")
    task = request.form['task']
    cql = "INSERT INTO todo.todolist(id,details) VALUES(UUID(),'"+task+"')"
    print(cql)
    session.execute(cql)
    return_cql = "SELECT * FROM todolist"
    r = session.execute(return_cql)
    res=""
    for i in r:
        res = res+str(i)+"\n"
    return res
    
@app.route('/delete_todo', methods=['GET', 'POST'])
def delete_todo():
    session = cassandra.connect()
    session.set_keyspace("todo")
    cql = "TRUNCATE TABLE todolist"
    session.execute(cql)
    return "Cleared your To-Do List!"


@app.route("/get_todo")
def get_todo():
    session = cassandra.connect()
    session.set_keyspace("todo")
    cql = "SELECT * FROM todolist"
    r = session.execute(cql)
    res=""
    for i in r:
        res = res+str(i)+"\n"
    print(res)
    return res

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
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('welcome'))

@app.route('/crime')
# @login_required
def getCrimeDate():
    crime_url_template = 'https://data.police.uk/api/crimes-street/all-crime?lat={lat}&lng={lng}&date={data}'
    my_latitude = '51.52369'
    my_longitude = '-0.0395857'
    my_date = '2019-01'
    crime_url = crime_url_template.format(lat = my_latitude,
                lng = my_longitude,
                data = my_date)
    resp = requests.get(crime_url)
    print(crime_url)
    if resp.ok:
        crimes = resp.json()
    else:
        print(resp.reason)

if __name__ == '__main__':
    # app.run(ssl_context='adhoc',debug=True)
    app.run(debug=True)
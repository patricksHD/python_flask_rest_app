from flask import Flask, render_template, redirect, url_for, request, session, flash , jsonify
from flask_hashing import Hashing
import json,uuid
# from flask_bcrypt import Bcrypt
from cassandra.cluster import Cluster
from flask_cassandra import CassandraCluster
from functools import wraps
import requests
from twython import Twython
import pandas as pd
# from werkzeug.serving import make_ssl_devcert

# make_ssl_devcert('cert/securly_SHA-256.crt', host='localhost')

app = Flask(__name__,instance_relative_config=True)
cassandra = CassandraCluster()
# bcrypt = Bcrypt(app)
hashing = Hashing(app)
app.config.from_pyfile('config.py')
app.config['CASSANDRA_NODES'] = ['localhost']  
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
    dict_ = {'text': [], 'favorite_count': [], 'profile_img_url': [], 'name': [],'url':[]}  
    for status in python_tweets.search(**query)['statuses']:  
        if not status['entities']['urls']:
            print("https://twitter.com/")
            dict_['url'].append("https://twitter.com/")
        else:
            print(status['entities']['urls'][0]['url'])
            dict_['url'].append(status['entities']['urls'][0]['url'])
        dict_['profile_img_url'].append(status['user']['profile_image_url'])
        dict_['text'].append(status['text'])
        dict_['name'].append(status['user']['name'])
        dict_['favorite_count'].append(status['favorite_count'])

    df = pd.DataFrame(dict_)  
    df.sort_values(by='favorite_count', inplace=True, ascending=False)  
    tweets = df.head(10).to_json(orient='records')
    dict_data = json.dumps(dict_)
    data = json.loads(dict_data)
    strHTM = "<h1> Top Tweets on : "+ request.form['keyword'].capitalize() +" </h1> <br> <table style = 'border: 1px solid black'>"
    for i in range(0,10):
        strHTM = strHTM + "<tr style ='border: 1px solid black'><td style ='border: 1px solid #dddddd'>"
        strHTM =  strHTM +str(i+1)+"</td><td style ='border: 1px solid #dddddd'>"
        strHTM =  strHTM +"<img src = "+data["profile_img_url"][i]+">"+"</td><td style ='border: 1px solid #dddddd'>"
        strHTM =  strHTM +"<a href = " +data["url"][i]+">"+data["text"][i]+"</a>"+"</td>"+"</tr>"
    strHTM = strHTM + "</table>"
    return strHTM

@app.route('/add_todo', methods=['GET', 'POST'])
def add_todo():
    session = cassandra.connect()
    session.set_keyspace("todo")
    task_name = request.form['task_name']
    task_description = request.form['task_description']
    task_priority = request.form['task_priority']
    task_start = request.form['task_start']
    task_end = request.form['task_end']
    task_difficulty = request.form['task_difficulty']
    task_assignee = request.form['task_assignee']
    subtasks_names = request.form['subtasks_names']
    subtasks_descriptions = request.form['subtasks_descriptions']
    subtasks_difficulties = request.form['subtasks_difficulties']
    subtasks_refs = request.form['subtasks_refs']
    subtasks_assignees = request.form['subtasks_assignees']
    

    # print(str(uuid.uuid4()))
    id = str(uuid.uuid4())
    task_cql = "INSERT INTO todo.tasks(id,name,description,priority,difficulty,start,end,assignee) VALUES("+id+",'"+task_name.replace("'","''")+"','"+task_description.replace("'","''")+"','"+task_priority.replace("'","''")+"','"+task_difficulty.replace("'","''")+"','"+task_start.replace("'","''")+"','"+task_end.replace("'","''")+"','"+task_assignee.replace("'","''")+"');"   
    session.execute(task_cql)
    print(task_cql)
    for i,s in enumerate(subtasks_names.split('|')):
        sub_tasks_cql = "INSERT INTO todo.sub_tasks(id,task_id,name,description,difficulty,ref,assignee) VALUES(UUID()"+",'"+id+"','"+s.replace("'","''")+"','"+subtasks_descriptions.split('|')[i].replace("'","''")+"','"+subtasks_difficulties.split('|')[i].replace("'","''")+"','"+subtasks_refs.split('|')[i].replace("'","''")+"','"+subtasks_assignees.split('|')[i].replace("'","''")+"')"   
        session.execute(sub_tasks_cql)
        print(sub_tasks_cql)
        
    
    
    # print(cql)
    # session.execute(cql)
    # return_cql = "SELECT * FROM tasks"
    # r = session.execute(return_cql)
    res="hi"
    # for i in r:
    #     res = res+str(i)+"\n"
    return res
    
@app.route('/delete_todo', methods=['GET', 'POST'])
def delete_todo():
    session = cassandra.connect()
    session.set_keyspace("todo")
    cql = "TRUNCATE TABLE todolist"
    session.execute(cql)
    return "Cleared your To-Do List!"


@app.route("/get_all_todo")
def get_todo():
    session = cassandra.connect()
    session.set_keyspace("todo")
    cql = "SELECT * FROM tasks"
    r = list (session.execute(cql))
    print(len(r))
    res_htm = "<h1> Tasks to-do : </h1><ol>"
    for i,row in enumerate(r,0): 
        res_htm = res_htm +"<li><a href= /get_task_by_id<"+str(row.id)+">"+str(row.name)+"</a></li>"
    res_htm = res_htm+"</ol>"

    # res=r.one()
#     res = "["
# #     for (Row row : rs):
# #     String json = row.getString(0);
# #     // ... do something with JSON string
# # }
#     # for i,row in enumerate(r,0):              ---HATEOAS
#     #     if((i+1)==len(r)):
#     #         res = res +  "{\"id\": \""+str(row.id)+"\", \"details\": \""+str(row.description)+"\"}"
#     #     else:
#     #         res = res +  "{\"id\": \""+str(row.id)+"\", \"details\": \""+str(row.description)+"\"},"
#     #     res = res + str(row)
#     res = res + "]"


    # print(res)
    # print(type(res_htm))
    return res_htm

@app.route("/get_task_by_id<id>")
def get_task_by_id(id):
    id=id.replace("<","")
    session = cassandra.connect()
    session.set_keyspace("todo")
    cql = "SELECT * FROM sub_tasks"
    r = list (session.execute(cql))
    print(len(r))
    res_htm = "<h1>Task Details</h1><h2> Sub Tasks to perform : </h2><table><tr style ='border: 1px solid black'><th style ='border: 1px solid #dddddd'>Sequence Number</th><th style ='border: 1px solid #dddddd'>Sub-TaskName</th><th style ='border: 1px solid #dddddd'>Assignee</th><th style ='border: 1px solid #dddddd'>Role</th></tr>"
    for i,row in enumerate(r,0): 
        u_cql = "SELECT * FROM users where id = "+str(row.assignee)
        u = list (session.execute(u_cql))
        res_htm = res_htm +"<tr><td style ='border: 1px solid #dddddd'>"+str(i+1)+"</td><td style ='border: 1px solid #dddddd'><a href =/get_sub_task_by_id<"+str(row.id)+">"+str(row.name)+"</a></td><td style ='border: 1px solid #dddddd'>"+str(u[0].name).capitalize()+"</td><td style ='border: 1px solid #dddddd'>"+str(u[0].role).capitalize()+"</td></tr>"
    res_htm = res_htm+"</ol>"
    return res_htm

@app.route("/get_sub_task_by_id<id>")
def get_sub_task_by_id(id):
    id = id.replace("<","")
    session = cassandra.connect()
    session.set_keyspace("todo")
    cql = "SELECT * FROM sub_tasks where id = "+id
    r = list (session.execute(cql))
    res_htm = "<h1> Sub Task Details : </h1><table><tr style ='border: 1px solid black'><th style ='border: 1px solid #dddddd'>Sub-Task ID</th><th style ='border: 1px solid #dddddd'>Name</th><th style ='border: 1px solid #dddddd'>Description</th><th style ='border: 1px solid #dddddd'>Difficulty</th><th style ='border: 1px solid #dddddd'>Assignee</th><th style ='border: 1px solid #dddddd'>Role</th><th style ='border: 1px solid #dddddd'>References</th><th style ='border: 1px solid #dddddd'>Connected to Task</th></tr>"
    for i,row in enumerate(r,0): 
        t_cql = "SELECT * FROM tasks where id = "+str(row.task_id)
        t = list (session.execute(t_cql))        
        u_cql = "SELECT * FROM users where id = "+str(row.assignee)
        u = list (session.execute(u_cql))
        res_htm = res_htm + "<tr><td style ='border: 1px solid #dddddd'>"+str(row.id)+"</td><td style ='border: 1px solid #dddddd'>"+str(row.name).capitalize()+"</td><td style ='border: 1px solid #dddddd'>"+str(row.description)+"</td><td style ='border: 1px solid #dddddd'>"+str(row.difficulty)+"</td><td style ='border: 1px solid #dddddd'>"+str(u[0].name).capitalize()+"</td><td style ='border: 1px solid #dddddd'>"+str(u[0].role).capitalize()+"</td><td style ='border: 1px solid #dddddd'><a href = "+str(row.ref)+">"+str(row.ref)+"</a></td><td style ='border: 1px solid #dddddd'><a href= /get_task_by_id<"+str(row.task_id)+">"+str(t[0].name).capitalize()+"</a></td></tr>"
    res_htm = res_htm+"</table>"
    return res_htm


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')  

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        pw_hash = hashing.hash_value(request.form['password'], salt=app.config['SALT'])
        if request.form['username'] != 'admin' or not(hashing.check_value(pw_hash, app.config['PASS'], salt=app.config['SALT'])):
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


if __name__ == '__main__':
    # app.run(ssl_context='adhoc',debug=True)
    app.run(debug=True, ssl_context=('cert/server.crt', 'cert/server.key'))
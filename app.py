
from datetime import datetime
from tokenize import Name
from unicodedata import name
from flask import Flask, render_template, request, session,redirect
from flask_sqlalchemy import SQLAlchemy
import json
import requests
import math


from flask_mail import Mail
local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'secret-key'
# mail sending -----------
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)
# mail sending over----------------
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['production_uri']

db = SQLAlchemy(app)


def current_price():
    key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

    # requesting data from url
    data = requests.get(key)
    data = data.json()
    price = (f"{data['symbol']} price is {data['price']}")


class Contacts(db.Model):
    '''sno,name,phone_no,message,email,date'''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_no = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(12), nullable=False)
    date = db.Column(db.String(12), nullable=True)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(21), nullable=False)

    slug = db.Column(db.String(21), nullable=False)
    date = db.Column(db.String(12), nullable=True)





@app.route("/")
def Home():
    posts = Posts.query.filter_by().all()
    #[0:params['no_of_posts']]
    last=math.ceil( len(posts)/int(params['no_of_posts']))


    page=request.args.get('page')
    if( not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
    if(page==1):
        prev="#"
        next="/?page="+str(page+1)
    elif(page==last):
         next="#"
         prev="/?page="+str(page-1)
    else:
        next="/?page="+str(page+1)
        prev="/?page="+str(page-1)
        





    
    key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"

    # requesting data from url
    data = requests.get(key)
    data = data.json()
    price = (f"{data['symbol']} price is {data['price']}")
    return render_template('index.html', params=params, price=price, posts=posts,prev=prev,next=next)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)


@app.route("/about")
def about():
    return render_template('about.html', params=params)
   # ------------------------------------------------
@app.route("/posting/<string:post_slug>", methods=['GET'])
def post_rout(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('posting.html', params=params, post=post)
    #2
@app.route("/posting2/<string:post_slug>", methods=['GET'])
def post_rout2(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('posting2.html', params=params, post=post)

@app.route("/types_of_blockchain/<string:post_slug>", methods=['GET'])
def post_rout3(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('types_of_blockchain.html', params=params, post=post)

#-------------------------------------------------------------------


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)
    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if(username == params['admin_user'] and userpass == params['admin_password']):
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
        else:
         return render_template('login.html', params=params)
    return render_template('login.html', params=params)


@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if(request.method == 'POST'):

        '''ADD ENTRY'''
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        phone_no = request.form.get('phone_no')

        entry = Contacts(name=name, phone_no=phone_no,
                         message=message, email=email)
        db.session.add(entry)
        db.session.commit()
        # mail function --------------
        mail.send_message("new message from blog",
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=message+"\n"+phone_no

                          )
    return render_template('contact.html', params=params)


@app.route("/post")
def post():
    return render_template('post.html', params=params, post=post)
@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
     if('user' in session and session['user'] == params['admin_user']):
         if request.method=='POST':
             title=request.form.get('title')
             tline=request.form.get('tline')
             slug=request.form.get('slug')
             content=request.form.get('content')
             name=request.form.get('name')
             date=datetime.now()
             if sno=='0':
              post=Posts(title=title,slug=slug,content=content,tagline=tline,date=date,name=name)
              db.session.add(post)
              db.session.commit()
             else:
                  post=Posts.query.filter_by(sno=sno).first()
                  post.title=title
                  post.slug=slug
                  post.content=content
                  post.tagline=tline
                  post.data=date
                  post.name=name
                  db.session.commit()
                  return redirect('/edit/'+sno)
         post=Posts.query.filter_by(sno=sno).first()
         return render_template('edit.html', params=params,sno=sno,post=post)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')
@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
     if('user' in session and session['user'] == params['admin_user']):
         post=Posts.query.filter_by(sno=sno).first()
         db.session.delete(post)
         db.session.commit()
     return redirect('/dashboard')



app.run(debug=True)
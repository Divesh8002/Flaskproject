from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import math
from flask_mail import Mail
import json
import os
localserver =True
with open('config.json','r') as c:
   params = json.load(c)['params']
app = Flask(__name__)
app.secret_key ="Divesh-jain"
app.config['UPLOAD_FOLDER'] =params['upload_location']
app.config.update(
   MAIL_SERVER ='smtp.gmail.com',
   MAIL_PORT="465",
   MAIL_USE_SSL=True,
   MAIL_USERNAME=params['gmail_user'],
   MAIL_PASSWORD=params['gmail_passd']


)
mail = Mail(app)
if(localserver):
   app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:@localhost/CodingBlackHole'
else:
   app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


class Contacts(db.Model):
   '''srid_contact ,name,email,phine_num,mess,date'''
   srid_contact = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(80),nullable=False)
   email = db.Column(db.String(12),nullable=False)
   phine_num = db.Column(db.String(120),nullable=False)
   mess = db.Column(db.String(120),nullable=False)
   date= db.Column(db.String(20),nullable=True)

class post(db.Model):
   '''srno,title,slug,content,date'''
   srno = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(80),nullable=False)
   slug = db.Column(db.String(30),nullable=False)
   content = db.Column(db.String(120),nullable=False)
   tagline = db.Column(db.String(120),nullable=False)
   date= db.Column(db.String(20),nullable=True)
   img_file = db.Column(db.String(20), nullable=True)


@app.route('/')
def home():
   post2 = post.query.filter_by().all()
   last = math.ceil(len(post2)/int(params['no_of_post']))
   #[0:params['no_of_post']]
   page =request.args.get('page')
   if(not str(page).isnumeric()):
       page=1
   page = int(page)
   post2 = post2[(page-1)*int(params['no_of_post']): (page-1)*int(params['no_of_post']) + int(params['no_of_post'])]

   if(page ==1):
       prev="#"
       next="/?page="+str(page+1)
   elif(page == last):
       next="#"
       prev="/?page"+str(page-1)
   else:
       prev = "/?page" + str(page - 1)
       next = "/?page=" + str(page + 1)
   return render_template('index.html',params=params,posts =post2,prev =prev,next =next)



@app.route('/about')
def aboutform():
    return render_template('about.html',params=params)

@app.route('/dashboard',methods=['GET','POST'])
def dashboardform():
   if ('user' in session and session['user'] == params['admin_user']):
      post3 = post.query.all()
      return render_template('dashboard.html', params=params, posts=post3)

   if request.method =='POST':
      username = request.form.get('uname')
      password = request.form.get('pass')
      if(params['admin_user'] == username and params['admin_passwd']==password):
         session['user'] = username
         post3 =post.query.all()
         return  render_template('dashboard.html',params=params,posts =post3)

   return render_template('login.html',params=params)



@app.route('/post/<string:post_slug>',methods=['GET'])
def postform(post_slug):
   post1 =post.query.filter_by(slug=post_slug).first()
   return render_template('post.html',params=params,post=post1)




@app.route('/contact',methods=['GET','POST'])
def contactform():
   if(request.method=='POST'):
      ''''Add Entry To data Base'''
      name = request.form.get('name')
      email = request.form.get('email')
      phone =request.form.get('phone')
      message = request.form.get('message')
      '''Insering Database where lsh valure are column name and rhs are that we fetch from contact page'''
      entry = Contacts(name=name,email=email,phine_num=phone,mess=message,date = datetime.now())
      db.session.add(entry)
      db.session.commit()
      mail.send_message("New Message From Blog" + name,
                        sender=email,
                        recipients=[params['gmail_user']],
                        body =message +'\n'+phone)
   return render_template('contact.html',params=params)

@app.route('/edit/<string:srno>',methods=['GET','POST'])
def edit(srno):
   if ('user' in session and session['user'] == params['admin_user']):
      if(request.method=='POST'):
         box_title = request.form.get('title')
         tline =request.form.get('tline')
         slug =request.form.get('slug')
         content =request.form.get('content')
         img_file =request.form.get('img_file')
         if srno=='0':
            post4 =post(title=box_title,tagline=tline,slug=slug,content=content,img_file=img_file,date=datetime.now())
            db.session.add(post4)
            db.session.commit()
         else:
            post5 =post.query.filter_by(srno =srno).first();
            post5.title = box_title
            post5.tagline = tline
            post5.slug =slug
            post.content =content
            post5.img_file =img_file
            post5.date =datetime.now()
            db.session.commit()
            return redirect('/edit/'+srno)
      post6 =post.query.filter_by(srno=srno).first()
      return render_template('edit.html',params=params,post =post6,srno=srno)


@app.route('/uploader',methods=['GET','POST'])
def uploader():
   if ('user' in session and session['user'] == params['admin_user']):
      if(request.method=="POST"):
         f = request.files['file1']
         f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
         return "Uploaded Succesfuly"

@app.route("/logout")
def logout():
   session.pop('user')
   return redirect('/dashboard')

@app.route("/delete/<string:srno>",methods=['GET','POST'])
def delete(srno):
   if ('user' in session and session['user'] == params['admin_user']):
      post7=post.query.filter_by(srno=srno).first()
      db.session.delete(post7)
      db.session.commit()
      return redirect('/dashboard')






if __name__ == '__main__':
   app.run(debug=True)

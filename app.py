from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
   name = "Divesh"
   return render_template('index.html',name = "Divesh")

@app.route('/about')
def helloworld():

   return render_template('about.html',name="Divesh")

if __name__ == '__main__':
   app.run(debug =True)

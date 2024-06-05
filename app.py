from flask import Flask, render_template, url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.secret_key = 'your_secret_key'
db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(20),unique= True,nullable=False)
    number=db.Column(db.Integer,unique= True, nullable=False)
    username=db.Column(db.String(20),unique= True, nullable=False)
    password=db.Column(db.String(20),unique= True, nullable=False)
    tasks = relationship('Data', backref='user', lazy=True)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.String(20), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods = ['GET','POST'])
def sign_up():
   if request.method == 'POST':
       name=request.form['name']
       number=request.form['number']
       username=request.form['username']
       password=request.form['password']
       user=User(name=name, number=number, username=username, password=password)
       if user.query.filter_by(name=name).first() is not None:
           return 'Name already exists'
       if user.query.filter_by(number=number).first() is not None:
           return 'number already exists'
       if user.query.filter_by(username=username).first() is not None:
           return 'username already exists'
       if user.query.filter_by(password=password).first() is not None:
           return 'password already exists'
       new_user=User(name=name, number=number, username=username, password=password)
       db.session.add(new_user)
       db.session.commit()
       return render_template('success.html')       
   return render_template('signup.html')
     

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        user=User.query.filter_by(username=username).first()
        if user and user.password==password:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html',error='*Invalid username and password')
    return render_template('login.html')

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        task = request.form['task']
        deadline_date = request.form['deadline']
        deadline = datetime.strptime(deadline_date, '%Y-%m-%d')
        user_id = session['user_id']
        data = Data(task=task, deadline=deadline, user_id=user_id)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('success1'))
    return render_template("dashboard.html")

@app.route("/success1")
def success1():
    return render_template("success1.html")

@app.route("/viewdata")
def viewdata():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    all_data = Data.query.filter_by(user_id=user_id).all()
    return render_template("viewdata.html", data=all_data)

@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    data = Data.query.get_or_404(id)
    if data.user_id != session['user_id']:
        return "Unauthorized access", 403
    if request.method == 'POST':
        task = request.form['task']
        deadline_date = request.form['deadline']
        deadline = datetime.strptime(deadline_date, '%Y-%m-%d')
        if task and deadline:
            data.task = task
            data.deadline = deadline
            db.session.commit()
            return redirect(url_for('viewdata'))
        else:
            return "Form data is missing", 400
    return render_template("edit.html", data=data)


@app.route("/delete/<int:id>")
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    data = Data.query.get_or_404(id)
    if data.user_id != session['user_id']:
        return "Unauthorized access", 403
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('viewdata'))

# if __name__ == '__main__':
#     app.run(debug=True)

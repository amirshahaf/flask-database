from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    passw = db.Column(db.String(120), unique=False, nullable=False)

    def __init__(self, username, passw):
        self.username = username
        self.passw = passw

    def __repr__(self):
        return '<Username %r>' % self.username


@app.route('/', methods=['post', 'get'])
def home():
    if request.form:
        try:
            user = Users(username=request.form.get('username'), passw=request.form.get('password'))
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print('Something went wrong!')
            print(e)
    return render_template('index.html', users=Users.query.all())


@app.route('/update', methods=['post', 'get'])
def update():
    if request.form:
        try:
            user = Users.query.filter_by(username=request.form.get('old-username')).first()
            user.username = request.form.get('new-username')
            db.session.commit()
        except Exception as e:
            print('Something went wrong!')
            print(e)
    return redirect('/')


@app.route('/delete', methods=['post', 'get'])
def delete():
    if request.form:
        try:
            user = Users.query.filter_by(username=request.form.get('delete-username')).first()
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            print('Something went wrong!')
            print(e)
    return redirect('/')

if __name__ == '__main__':
	app.run(debug=True) 

from flask import Flask, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.secret_key = '8a7f43415792dadc4d9e41fef6f45307'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'


@login_manager.user_loader
def load_user(username):
    return Users.query.get(username)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    passw = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, username, passw):
        self.username = username
        self.passw = passw

    def __repr__(self):
        return '<Username %r>' % self.username


@app.route('/', methods=['post', 'get'])
def index():
    if current_user:
        return redirect('/home')
    return redirect('/login')


@app.route('/login', methods=['post', 'get'])
def login():
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if user is None:
            flash('Invalid Username or password, please try again.')
            return redirect('/login')
        if check_password_hash(user.passw, password):
            flash('Invalid Username or password, please try again.')
            return redirect('/login')
        login_user(user)
        flash(f'{username} Successfully logged in!')
        return redirect('/home')
    return render_template('login.html')


@app.route('/register', methods=['post', 'get'])
def register():
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        if Users.query.filter_by(username=username).first():
            flash('Username already registered!')
            return redirect('/register')
        user = Users(username=username, passw=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash(f'{username} Successfully registered!')
        return redirect('/login')
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out!')
    return redirect('/login')


@app.route('/home', methods=['post', 'get'])
@login_required
def home():
    name = current_user.username
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users(username=username, passw=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash(f'{request.form.get("username")} Successfully registered!')
    return render_template('home.html', users=Users.query.all(), username=name)


@app.route('/update', methods=['post', 'get'])
def update():
    if request.form:
        user = Users.query.filter_by(username=request.form.get('old-username')).first()
        user.username = request.form.get('new-username')
        db.session.commit()
        flash(f'{request.form.get("new-username")} Successfully updated!')
    return redirect('/home')


@app.route('/delete', methods=['post', 'get'])
def delete():
    if request.form:
        user = Users.query.filter_by(username=request.form.get('delete-username')).first()
        db.session.delete(user)
        db.session.commit()
        flash(f'Successfully deleted {request.form.get("delete-username")}')
    return redirect('/home')


if __name__ == '__main__':
    app.run(debug=True)

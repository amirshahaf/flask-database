import os
from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename

# Image upload parameters
MYDIR = os.path.dirname(__file__)
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Flask parameters
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.secret_key = '8a7f43415792dadc4d9e41fef6f45307'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/login'


@login_manager.user_loader
def load_user(username):
    return Users.query.get(username)


# Database class init
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    passw = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.passw = generate_password_hash(password)

    def __repr__(self):
        return '<Username %r>' % self.username


class Images(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    size = db.Column(db.String, nullable=False)
    comments = db.Column(db.String, nullable=False)
    link = db.Column(db.String, unique=True, nullable=False)

    def __init__(self, name, size, comments, link):
        self.name = name
        self.size = size
        self.comments = comments
        self.link = link


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['post', 'get'])
def index():
    if current_user.is_authenticated:
        return render_template('index.html', images=Images.query.all(), logged=True)
    return render_template('index.html', images=Images.query.all(), logged=False)


@app.route('/login', methods=['post', 'get'])
def login():
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        if user is None:
            flash('Invalid Username or password, please try again.')
            return redirect('/')
        if not check_password_hash(user.passw, password):
            flash('Invalid Username or password, please try again.')
            return redirect('/')
        login_user(user)
        flash(f'{username} Successfully logged in!')
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out!')
    return redirect('/login')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['image']
        name = request.form.get('name')
        size = request.form.get('size')
        comments = request.form.get('comments')
        link = file.filename
        if Images.query.filter_by(name=name).first():
            flash('נמצא פריט קיים')
            return redirect('/')
        image = Images(name=name, size=size, comments=comments, link=link)
        db.session.add(image)
        db.session.commit()
        flash(f' {name}נוסף בהצלחה ')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(MYDIR + "/" + app.config['UPLOAD_FOLDER'], filename))
            return redirect('/')
    return 'hello'


@app.route('/delete', methods=['post', 'get'])
def delete():
    if request.form:
        image = Images.query.filter_by(name=request.form.get('delete-name')).first()
        db.session.delete(image)
        db.session.commit()
        flash(f'הפריט נמחק בהצלחה')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

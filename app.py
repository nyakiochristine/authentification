import crypt
from enum import unique
from operator import ifloordiv
from flask import Flask,render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user, login_required,LoginManager,logout_user
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired,Length,ValidationError
from flask_bcrypt import Bcrypt 

app = Flask(__name__, template_folder='../Templates')
db= SQLAlchemy(app)
bycrypt = Bcrypt(app)
app.config['SQLAlchemy_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=4, max=20)],render_kw={"placeholder": "username"})
    
    password = PasswordField(validators=[InputRequired(),Length(min=4, max=20)],render_kw={"placeholder": "password"})
    
    submit = SubmitField("signup")
    
    def validate_username(self,username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("The username already exists. Choose a different username")
        
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=4, max=20)],render_kw={"placeholder": "username"})
    
    password = PasswordField(validators=[InputRequired(),Length(min=4, max=20)],render_kw={"placeholder": "password"})
    
    submit = SubmitField("login")



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return  redirect(url_for('login'))


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(username=form.username.data).first()
        if user:
            if bycrypt.check_password_hash(user.password,form.password.data):
                login_user(user)
                return redirect(url_for('dasboard'))
    

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET','POST'])
def signup():
    form= RegisterForm()
    
    
    if form.validate_on_submit():
        hashed_password = bycrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html',form=form)

if __name__ == '__main__':
    app.run(debug=True)
    

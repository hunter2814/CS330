from os.path import abspath, dirname, join

from flask import flash, Flask, Markup, redirect, render_template, url_for, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import fields, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
import random


_cwd = dirname(abspath(__file__))

SECRET_KEY = 'flask-session-insecure-secret-key'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(_cwd, 'contacts.db')
WTF_CSRF_SECRET_KEY = 'random'


app = Flask(__name__)
app.config.from_object(__name__)

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String)

    def __repr__(self):
        return self.user_name
    def __str__(self):
        return self.user_name

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    distance = db.Column(db.String)
    time = db.Column(db.String)
    
    def __repr__(self):
        return '{0}, {1}, {2}'.format(name, distance, time)
    

class GenForm(Form):
    user = QuerySelectField(query_factory=User.query.all)
    distance = fields.StringField('distance', validators=[validators.required()])
    time = fields.StringField('time', validators=[validators.required()])
    
        
class UserForm(Form):
    user_name = fields.StringField()
    

    
@app.route("/")
def index():
    user_form = UserForm()
    gen_form = GenForm()
    return render_template("index.html",
                           user_form=user_form,
                           gen_form=gen_form)


@app.route("/user", methods=("POST", "GET"))
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        flash("Added user")
        return redirect(url_for("index"))
    return render_template("errors.html", form=form)


@app.route("/add", methods=("POST", "GET"))
def add_time():
    form = GenForm()
    if form.validate_on_submit():
        contact = Contact()
        form.populate_obj(contact)
        db.session.add(contact)
        db.session.commit()
        flash("Added time for " + form.user.data.user_name)
        return redirect(url_for("index"))
    return render_template("errors.html", form=form)


@app.route("/users")
def view_users():  
    query = User.query.filter(User.id >= 0)
    data = query_to_list(query)
    data = [next(data)] + [[_make_link(cell) if i == 0 else cell for i, cell in enumerate(row)] for row in data]
    return render_template("contacts.html", data=data, type="Users")



_LINK = Markup('<a href="{url}">{name}</a>')


def _make_link(user_id):
    url = url_for("view_user_time", user_id=user_id)
    return _LINK.format(url=url, name=user_id)

def _make_rm(user_id):
    url = url_for("rm_user", user_id=user_id)
    return _LINK.format(url=url, name=user_id)


#not completely finished yet
@app.route("/user/<int:user_id>")
def view_user_time(user_id): 
    user = User.query.get_or_404(user_id)
    data = query_to_list(query)
    title = "Times for " + user.user_name
    
    return render_template("contacts.html", data=data, type=title)

def query_to_list(query, include_field_names=True): 
    column_names = []
    for i, obj in enumerate(query.all()):
        if i == 0:
            column_names = [c.name for c in obj.__table__.columns]
            if include_field_names:
                yield column_names
        yield obj_to_list(obj, column_names)


def obj_to_list(sa_obj, field_order): 
    return [getattr(sa_obj, field_name, None) for field_name in field_order]
    

if __name__ == "__main__":
    app.debug = True
    db.create_all()
    app.run()

from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title =  db.Column(db.String(120))
    body = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.before_request
def require_login():
    routes_allowed = ['show_posts', 'login', 'index', 'register']
    if request.endpoint not in routes_allowed and 'username' not in session:
        return redirect('/login')


@app.route('/blog', methods=['POST', 'GET'])
def show_posts():

    entry_id = request.args.get('id')
    user_id = request.args.get('user')

    if user_id:
        blog_posts = Blog.query.filter_by(owner_id=user_id)
        return render_template('singleUser.html', blog_posts=blog_posts)

    if entry_id:
        post = Blog.query.filter_by(id=entry_id).first()
        return render_template('post.html', post=post)

    else:
        post=""
        all_posts = Blog.query.all()
        return render_template('blog.html', post=post, all_posts=all_posts)

    # if request.args:
    #     id = request.args.get('id')
    #     post = Blog.query.get(id)
    #     return render_template('post.html', page_title='Build a Blog!', post=post)
    #     blog_posts = Blog.query.all()
    #     return render_template('blog.html', blog_posts=blog_posts)
    # else:
    #     blog_posts = Blog.query.all()
    # return render_template('blog.html', page_title='Posts', blog_posts=blog_posts)       



@app.route('/newpost', methods=['POST', 'GET'])
def add_new():

    if request.method == 'GET':
        return render_template('newpost.html', page_title='Add a new post')

    if request.method == 'POST':
        title=request.form['title']
        body=request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        title_error = False
        body_error = False

        if len(title)==0:
            flash('Please enter a Title!', 'error')
            title_error = True
        if len(body)==0:
            flash('Please give us something to read!', 'error')
            body_error = True

        if title_error or body_error:
            return render_template('newpost.html', page_title="New Entry", title=title, body=body)
        
        else:
            if len(title) and len(body) > 0:
                new_post = Blog(title, body, owner)
                db.session.add(new_post)
                db.session.commit()
                return redirect("/blog?id=" + str(new_post.id))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('User does not exist.', 'error')
            return redirect('/signup')
        if username and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('Bad Password', 'error')
            return render_template('login.html')
        if password == "":
            flash('Please enter a password', 'error')
            return render_template('login.html')
        else:
            return redirect('signup.html')

    return redirect("/login")
    
@app.route("/signup", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        verify_pwd  = request.form['verify_pwd']

        if username == '' or password == '':
            flash('Please make sure all fields are filled out.', 'error')
            return redirect('/signup')
        
        else:
            if len(username) < 3 or len(password) < 3 or len(username) > 20 or len(password) > 20:
                flash('Length is 3-20 characters sorry!', 'error')
                username = ''
                return redirect('/signup')

        if password != verify_pwd:
            flash('Passwords do not match')
            return redirect('/signup')

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Username taken.', 'error')
            return render_template('signup.html')
        
    return render_template('signup.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    usernames = User.query.all()
    return render_template('index.html', usernames=usernames)



if __name__ == '__main__':
    app.run()
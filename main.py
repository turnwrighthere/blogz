from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title =  db.Column(db.String(120))
    body = db.Column(db.String(250))

    def __init__(self, title, body):
        self.title = title
        self.body = body



@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('blog')

@app.route('/blog', methods=['POST', 'GET'])
def show_posts():


    if request.args:
        id = request.args.get('id')
        post = Blog.query.get(id)
        return render_template('post.html', page_title='Build a Blog!', post=post)

        blog_posts = Blog.query.all()
        return render_template('blog.html', blog_posts=blog_posts)

    else:
        blog_posts = Blog.query.all()

    return render_template('blog.html', page_title='Posts', blog_posts=blog_posts)       



@app.route('/newpost', methods=['POST', 'GET'])
def add_new():

    if request.method == 'GET':
        return render_template('newpost.html', page_title='Add a new post')

    if request.method == 'POST':
        title=request.form['title']
        body=request.form['body']

        title_error = ''
        body_error = ''

        if len(title)==0:
            title_error='Please enter a Title!'
        if len(body)==0:
            body_error = 'Please give us something to read!'

        if title_error or body_error:
            return render_template('newpost.html', page_title="New Entry", title_error=title_error, body_error=body_error, title=title, body=body)
        
        else:
            if len(title) and len(body) > 0:
                new_post = Blog(title, body)
                db.session.add(new_post)
                db.session.commit()
                return redirect("/blog?id=" + str(new_post.id))



if __name__ == '__main__':
    app.run()
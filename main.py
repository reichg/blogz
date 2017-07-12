from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpassword@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'edf898ddlodf9'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        
        self.email = email
        self.password = password
        
    
@app.before_request
def require_login():
    #pass
        
    allowed_routes = ['login', 'register', 'allblogs', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')
    else:
        pass


    
@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Logged In')
            print(session)
            return redirect('/newpost')
        elif not user:
            user_error = 'User does not exist'
            return render_template('login.html', user_error=user_error)
        elif user.password != password:
            password_error = 'Incorrect password'
            return render_template('login.html', password_error=password_error)
    
    else:
        return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            if password == "":
                blank_error = "Must create a password!"
                return render_template('register.html', blank_error=blank_error)
            elif len(password) <= 3:
                len_error = "Password must be longer than 3 characters"
                return render_template('register.html', len_error=len_error)
            elif password == verify:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/newpost')
            elif password != verify:
                password_v_error = 'Your passwords do not match, try again.'
                return render_template('register.html', password_v_error=password_v_error)
                
        else:
            duplicate_error = "User Exists"
            return render_template('register.html', duplicate_error=duplicate_error)
    else:         
        return render_template('register.html')


@app.route('/logout')
def logout():
    if 'email' in session:
        del session['email']
        logout_success = "You have logged out"
    return redirect('/allblogs')
    


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        blog_title = request.form['blogtitle']
        blog_body = request.form['blogbody']
        if blog_title == "" and blog_body == "":
            title_error = 'Your blog needs a title silly!'
            body_error = 'Your blog needs a body bruh!'
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
        elif blog_title == "":
            title_error = 'Your blog needs a title silly!'
            return render_template('newpost.html', title_error=title_error)
        elif blog_body == "":
            body_error = 'Your blog needs a body bruh!'
            return render_template('newpost.html', body_error=body_error)      
        else:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            newID = new_blog.id
            redirect_str = "?"+ "id=" + str(newID)
            #?id=number&title
            
            return redirect('/myblog' + redirect_str)
             
    return render_template('newpost.html')
   

      
@app.route('/myblog', methods=['POST', 'GET'])
def myblog():
    if request.args:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        return render_template('singleblog.html', blog=blog)
    else:   
        owner = User.query.filter_by(email=session['email']).first()
        blogs = Blog.query.filter_by(owner=owner).all()
        return render_template('myblog.html', owner=owner, blogs=blogs)
#get the args from the URL (ID)
#Blog.query.filter_by(id=whatevertheGETidwas)

    
@app.route('/allblogs', methods=['POST', 'GET'])
def allblogs():
    blogs = Blog.query.all()
    return render_template('allblogs.html', blogs=blogs)


@app.route('/', methods=['POST', 'GET'])
def index(): 
    
    users = User.query.all()
    return render_template('index.html', users=users)
    

    
if __name__ == '__main__':
    app.run()


from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime 
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import UserForm, LoginForm, PostForm, SearchForm, NamerForm, PasswordForm
from flask_ckeditor import CKEditor


#create a Flask instance
app = Flask(__name__)
#Add CKEditor
ckeditor = CKEditor(app)
#Old SQLite Database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#New MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/our_users'

#Secret Key
app.config['SECRET_KEY'] = "@45665Fdsdss456kl"
#Initialize the Database
db = SQLAlchemy(app)
migrate=Migrate(app,db)

# Flask Login configurations
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view= 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Pass stuff to Navbar
@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

# Create a route decorator
@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)  

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #Hash the Password!!
            hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2:sha256")
            user = Users(name=form.name.data, username=form.username.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data=''
        form.password_hash.data=''
        flash("user Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', 
                           form=form,
                           name=name,
                           our_users=our_users)  


#Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form=UserForm()
    user_to_update=Users.query.get_or_404(id)
    if request.method == 'POST':
        user_to_update.name =  request.form['name']
        user_to_update.username =  request.form['username']
        user_to_update.email =  request.form['email']
        user_to_update.favorite_color =  request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", 
                                    form=form,
                                    user_to_update=user_to_update)

        except:
            flash("Looks like there was a problem....try again!")
            return render_template("update.html", 
                                    form=form,
                                    user_to_update=user_to_update)
    else:
        return render_template("update.html", 
                                    form=form,
                                    user_to_update=user_to_update)

#Delete Database Record
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    name = None
    form = UserForm()
    user_to_delete=Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")

        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', 
                                form=form,
                                name=name,
                                our_users=our_users) 
    except:
        flash("Whoops! There was a problem deleting user, try again.... ")
        return render_template('add_user.html', 
                                form=form,
                                name=name,
                                our_users=our_users)


#Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again")


    return render_template('login.html', form=form)

#Create Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out! Thanks")
    return redirect(url_for('login'))


#Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form=UserForm()
    id = current_user.id
    user_to_update=Users.query.get_or_404(id)
    if request.method == 'POST':
        user_to_update.name =  request.form['name']
        user_to_update.username =  request.form['username']
        user_to_update.email =  request.form['email']
        user_to_update.favorite_color =  request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html", 
                                    form=form,
                                    user_to_update=user_to_update)

        except:
            flash("Looks like there was a problem....try again!")
            return render_template("dashboard.html", 
                                    form=form,
                                    user_to_update=user_to_update)
    else:
        return render_template("dashboard.html", 
                                    form=form,
                                    user_to_update=user_to_update)
    return render_template('dashboard.html')


#Create custome error pages
#Invalid URL 
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

#Internal Server Error 
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
#@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        #form.author.data = ''
        form.slug.data = ''

        #Add post data to database 
        db.session.add(post)
        db.session.commit()

        #Return a message
        flash("Blog Post Submitted Successfully!")

    #Redirect to the webpage 
    return render_template('add_post.html', form=form)  

# Add Post Page
@app.route('/posts')
def posts():
    #Grab all the posts from the database
    posts=Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html',posts=posts)

# Add Post Page
@app.route('/posts/<int:id>')
def post(id):
    post=Posts.query.get_or_404(id)
    return render_template('post.html',post=post)

# Edit Post Page
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostForm()
    post_to_update=Posts.query.get_or_404(id)
    if form.validate_on_submit():
        post_to_update.title=form.title.data
        #post_to_update.author=form.author.data
        post_to_update.slug=form.slug.data
        post_to_update.content=form.content.data
        #Update Database
        db.session.add(post_to_update)
        db.session.commit()
        flash("Psot Has Been Updaed!")
        return redirect(url_for('post', id=post_to_update.id))

    if current_user.id == post_to_update.poster_id:        
        form.title.data=post_to_update.title
        #form.author.data=post_to_update.author
        form.slug.data=post_to_update.slug
        form.content.data=post_to_update.content
        return render_template('edit_post.html', form=form)
    else:
         #Return a message
        flash("You Are Not Authorized To Edit That Post!")

        #Grab all the posts from the database
        posts=Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html',posts=posts)

#Delete Post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id=current_user.id
    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            #Return a message
            flash("Blog Post was Deleted!")
            
            #Grab all the posts from the database
            posts=Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html',posts=posts)
        
        except:  
            #Return an error message      
            flash("There was a problem deleting post, try again... ")

    else:
        #Return a message
        flash("You Are Not Authorized To Delete That Post!")
        
        #Grab all the posts from the database
        posts=Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html',posts=posts)
    
#Create Search Function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query 
    if form.validate_on_submit(): 
        # Get data from submitted form 
        post.searched=form.searched.data
        # Query the database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()

        return render_template('search.html',
                                form=form,
                                searched=post.searched,
                                posts=posts)

# Create Admin
@app.route('/admin')
@login_required
def admin():
    id = current_user.id 
    if id == 21:
        return render_template('admin.html')  
    else:
        flash("Sorry you must be the Admin to access the admin page...")
        return redirect(url_for('dashboard'))

################################################################ DB Models ################################################################################


# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    #Do some password stuff
    password_hash = db.Column(db.String(128))
    #User Can Have Many Posts
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

#Create a Blog Post Model 
class Posts(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    #Foreign Key To Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


################################################################ TEST ################################################################################
#Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully")
    return render_template('name.html', 
                           name=name,
                           form=form)  

#Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None

    form = PasswordForm()
    #Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # CLear the form
        form.email.data = ''
        form.password_hash.data=''

        #Lookup User by Email Address
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check Hased Password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html', 
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form) 



#Json API
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "Anindita": "Margherita",
        "Oni": "Hawaiian",
        "Podder": "Mushroom"
    }
    #return{ "Date": date.today()}
    return favorite_pizza

if __name__ == '__main__':
    app.run(debug=True)




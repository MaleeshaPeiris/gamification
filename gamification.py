from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime 
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exists, select
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import UserForm, LoginForm, PostForm, SearchForm, NamerForm, PasswordForm
from flask_ckeditor import CKEditor
import numpy as np

#export FLASK_ENV=development
#export FLASK_APP=gamification.py


#create a Flask instance
app = Flask(__name__)
#Add CKEditor
ckeditor = CKEditor(app)
#Old SQLite Database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#New MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/gamification'

#Secret Key
app.config['SECRET_KEY'] = "@45665Fdsdss456kl"
#Initialize the Database
db = SQLAlchemy(app)
migrate=Migrate(app,db)
app.app_context().push()

# Flask Login configurations
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view= 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Pass stuff to Navbar
@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

# Create a route decorator
@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            #Hash the Password!!
            hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2:sha256")
            user = User(first_name=form.first_name.data, last_name=form.last_name.data, username=form.username.data, email=form.email.data, role= 'student', password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.username.data                               #change: name to username and also in the template
        form.first_name.data = ''
        form.last_name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data=''
        flash("Registration has been completed successfully. Please log in!")
        return redirect(url_for('login'))

    our_users = User.query.order_by(User.date_added)
    return render_template('add_user.html', 
                           form=form,
                           name=name,
                           our_users=our_users)         #change: need to redirect to the login page                


#Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form=UserForm()
    user_to_update=User.query.get_or_404(id)
    if request.method == 'POST':
        user_to_update.first_name =  request.form['first_name']
        user_to_update.last_name =  request.form['last_name']
        user_to_update.username =  request.form['username']
        user_to_update.email =  request.form['email']
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
@login_required
def delete(id):
    name = None
    form = UserForm()
    user_to_delete=User.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")

        our_users = User.query.order_by(User.date_added)
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
        user = User.query.filter_by(username=form.username.data).first()
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
    enrolled_courses = get_enrolled_courses(id)
    user_to_update=User.query.get_or_404(id)
    if request.method == 'POST':
        user_to_update.first_name =  request.form['first_name']
        user_to_update.last_name =  request.form['last_name']
        user_to_update.username =  request.form['username']
        user_to_update.email =  request.form['email']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html", 
                                    form=form,
                                    user_to_update=user_to_update, enrolled_courses=enrolled_courses)

        except:
            flash("Looks like there was a problem....try again!")
            return render_template("dashboard.html", 
                                    form=form,
                                    user_to_update=user_to_update, enrolled_courses=enrolled_courses)
    else:
        return render_template("dashboard.html", 
                                    form=form,
                                    user_to_update=user_to_update, enrolled_courses=enrolled_courses)
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

# Quiz Page
@login_required
@app.route('/quiz')
def quiz():
    #id=current_user.id
    enrolled_courses = Course.query.all()

    return render_template('quiz.html', 
                            enrolled_courses=enrolled_courses )


# Forum Selection Page
@login_required
@app.route('/forum' , methods=['GET', 'POST'])
def forum_list():
    id=current_user.id
    enrolled_courses = get_courses_to_enroll(id)

    return render_template('forum_list.html', 
                            enrolled_courses=enrolled_courses )

# Selected Forum Page
@login_required
@app.route('/forum/<int:id>', methods=['GET', 'POST'])
def forum_page(id):
    #id=current_user.id
    #enrolled_courses = Course.query.all()

    return render_template('forum.html', )

@app.route('/enrol/<int:id>', methods=['GET', 'POST'])
@login_required
def enroll(id):
    if request.method == 'POST':
        user_id = current_user.id 
        course_id = request.form.get('course_id')

        course = Course.query.get(course_id)
        

        if current_user and course:
            enrollment = Enrollment(
                user_id=user_id,
                course_id=course_id,
                enrollmentDate=datetime.now(),
            )

            db.session.add(enrollment)
            db.session.commit()

            return redirect(url_for('dashboard'))

        else:
            return "Student or COurse not found"
    courses = Course.query.all()
    enrolled_courses = get_courses_to_enroll(id)
    return render_template('enrolment.html', 
                            courses=courses , enrolled_courses=enrolled_courses)

# Quiz Selection Page
@login_required
@app.route('/quiz-selection/<int:course_id>')
def quiz_selection(course_id):
    #quiz_sets = QuizSet.query.filter_by(course_id=course_id)
    #results = QuizSet.query.filter_by(course_id=course_id).with_entities(QuizSet.id, QuizSet.name, QuizSet.attribute1).add_columns("value_for_attribute2").all()

    from sqlalchemy import exists



    # Define a subquery to check if the quiz_set_id exists in the quiz_submission table
    subquery = exists().where(QuizSubmission.quiz_set_id == QuizSet.id)

    # Filter QuizSet records by course_id and add a new attribute indicating if the quiz_set_id exists in the quiz_submission table
    quiz_sets = (
        QuizSet.query
        .filter_by(course_id=course_id)
        .add_columns(subquery.label('is_quiz_taken'))
        .all()
    )
    

    return render_template('quiz_selection.html', 
                            quiz_sets=quiz_sets
                            )   

# Quiz Questions
@login_required  
@app.route('/quiz-exam/<int:quiz_set_id>', methods=['GET', 'POST'])                    
def quiz_exam(quiz_set_id):
    quiz_questions=QuizQuestion.query.filter_by(quiz_set_id=quiz_set_id)
    quiz_question_count = quiz_questions.count()
    current_user_id = current_user.id
    total_correct_answer = 0
    if request.method == 'POST':
        for quiz_question in quiz_questions:
            given_answer = int(request.form[f'question-{quiz_question.id}'])
            if given_answer ==  quiz_question.correct_answer:
                is_correct_answer = True
                total_correct_answer=total_correct_answer+1
            else:
                is_correct_answer = False
            quiz_submission = QuizSubmission(user_id=current_user_id, quiz_set_id=quiz_set_id, quiz_question_id=quiz_question.id,given_answer=given_answer, is_correct_answer=is_correct_answer)
            db.session.add(quiz_submission)
        try:   
            db.session.commit()
            flash("Yor Quiz Exam is Over! Thank You.") 
            return render_template('quiz_exam.html',
                            quiz_set_id=quiz_set_id,
                            quiz_questions=quiz_questions,
                            quiz_question_count = quiz_question_count,
                            total_correct_answer=total_correct_answer)
        except:
            flash("Looks like there was a problem submitting your exam....try again!") 
            return render_template('quiz_exam.html',
                            quiz_set_id=quiz_set_id,
                            quiz_questions=quiz_questions,
                            quiz_question_count = quiz_question_count,
                            total_correct_answer=total_correct_answer)

    return render_template('quiz_exam.html',
                            quiz_set_id=quiz_set_id,
                            quiz_questions=quiz_questions,
                            quiz_question_count = quiz_question_count,
                            total_correct_answer=total_correct_answer)




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

user_course = db.Table('user_course',
                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
                    )

# Create Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)
    enrolments = db.relationship('Enrollment', backref='enroller')
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    #Do some password stuff
    password_hash = db.Column(db.String(128))
    #User Can Have Many Courses
    courses = db.relationship('Course', secondary=user_course, backref='users') #user.courses + course.users (backref comes into play)
    #User Can Have Many QuizSubmission
    quiz_submissions = db.relationship('QuizSubmission', backref='quiz_taker')

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


# Create Course Model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    enrollments = db.relationship('Enrollment', backref='course')
    quiz_sets = db.relationship('QuizSet', backref='course')

# Create quiz_set Model
class QuizSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    quiz_questions = db.relationship('QuizQuestion', backref='quiz_set')
    quiz_submissions = db.relationship('QuizSubmission', backref='quiz_set')

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.Integer, nullable=False)
    quiz_set_id = db.Column(db.Integer, db.ForeignKey('quiz_set.id'))
    quiz_submissions = db.relationship('QuizSubmission', backref='quiz_question')


class QuizSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_set_id = db.Column(db.Integer, db.ForeignKey('quiz_set.id'))
    quiz_question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id')) 
    given_answer =  db.Column(db.Integer, nullable=False)
    is_correct_answer = db.Column(db.Boolean, default=False, nullable=False)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    enrollmentDate = db.Column(db.DateTime, default=datetime.utcnow)

def get_enrolled_courses(user_id):
    user = User.query.get(user_id)
    if user:
        return [enrollment.course.name for enrollment in user.enrolments]
    else:
        return []
    
def get_courses_to_enroll(user_id):
    user = User.query.get(user_id)
    courses = Course.query.all()
    enrolled_courses = [enrollment.course for enrollment in user.enrolments]
    if user:
        return enrolled_courses 
    else:
        return []

if __name__ == '__main__':
    app.run(debug=True)




from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from datetime import datetime 

db = SQLAlchemy()

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

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    enrollmentDate = db.Column(db.DateTime, default=datetime.utcnow)

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



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discussion_forum_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text)
    course = db.relationship('Course', backref='posts')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text)
    commented_date = db.Column(db.DateTime, default=datetime.utcnow)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, SelectField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

# Create a Form Class
class UserForm(FlaskForm):
     first_name = StringField("First Name", validators=[DataRequired()])
     last_name = StringField("Last Name", validators=[DataRequired()])
     username = StringField("Username", validators=[DataRequired()])
     email = StringField("Email", validators=[DataRequired()])
     role  = StringField("Role")
     password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
     password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
     submit = SubmitField("Submit")    

#create Enrollment form
class Enrollment(FlaskForm):
    submit = SubmitField("Submit")


#Create Login Form   
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")     


# Create a Posts Form       
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    #content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content=CKEditorField('Content',validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")   
         
# Create a Search Form       
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit") 
################################################################ TEST ################################################################################

 # Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a Form Class
class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")    
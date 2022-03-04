"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

import werkzeug
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, SignUpForm
from app.models import UserProfile

from werkzeug.security import check_password_hash


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('User Logged Out', 'success')
    return redirect(url_for('home'))
    


@app.route('/secure-page')
@login_required
def secure_page():
    return render_template('secure_page.html')


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    form = SignUpForm()
    if request.method == 'POST':
        if (form.validate_on_submit()):
            if (form.password.data != form.confirmPassword.data):
                flash('Passwords doesn\'t match', 'error')
                return render_template('signUp.html', form=form)
            user = UserProfile(
                form.firstName.data,
                form.lastName.data,
                form.username.data,
                form.password.data
            )
            db.session.add(user)
            db.session.commit()
            flash('New User Registered', 'success')
            return redirect(url_for("home"))
        flash('Something went wrong check your credentials', 'error')
        return render_template('signUp.html', form=form) 
    return render_template('signUp.html', form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
           
            username = form.username.data
            password = form.password.data
            
            user = UserProfile.query.filter_by(username=username).first()
            
            if not user:
                flash('User not Found', 'error')
                return render_template("login.html", form=form)
            
            if not check_password_hash(user.password, password):
                flash('Incorrect Password', 'error')
                return render_template("login.html", form=form)
            
            
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for("secure_page"))
            
    return render_template("login.html", form=form)


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")

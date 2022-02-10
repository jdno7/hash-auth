from sqlite3 import IntegrityError
from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hashing_login"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def homepage():
    """Show Homepage or re-direct to register"""

    return redirect('/register')

@app.route('/register', methods=['GET','POST'])
def register_form():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
        email = form.email.data
        fname = form.first_name.data
        lname = form.last_name.data

        user = User.register(username, pwd, email, fname, lname)
        
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            
            form.username.errors.append('Username is already taken, try again')
            return render_template('register.html', form=form)
        session['username'] = user.username

        return redirect(f"/users/{user.username}")

    else:
        return render_template('register.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(username, pwd)

        if user:
            session["username"] = user.username  # keep logged in
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Bad name/password"]
            return redirect ("/login.html")
           
    return render_template("login.html", form=form)       

@app.route("/users/<username>")
def user_info(username):
    """Page for logged in User about themself"""
 
    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")

    else:
        user = User.query.filter_by(username=username).first()
        return render_template("users.html", user=user)

@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("username")

    return redirect("/")

@app.route("/users/<username>/feedback/add", methods=['GET','POST'])
def feedback_form(username):
    if 'username' in session:
        form = FeedbackForm()
        user = User.query.filter_by(username=username).first()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            f = Feedback(title=title, content=content, username=user.username)
            db.session.add(f)
            db.session.commit()
            return redirect(f"/users/{username}")
        else:
            return render_template("add_feedback.html", form=form, user=user)
    else:
        flash("You must be logged in to view!")
        return redirect ('/')

@app.route("/feedback/<int:feedback_id>/update", methods=['Get','POST'])
def edit_feedback(feedback_id):
    
    feedback = Feedback.query.get_or_404(feedback_id)
    if session['username'] == feedback.user.username:
        
        form = FeedbackForm(obj=feedback)

        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            flash('Feedback Updated!!')
            return redirect(f"/users/{feedback.user.username}")
        else:
            return render_template('/edit_feedback.html', form=form, user=feedback.user)
    else:
        flash("You cant do that Bitch!!")
        return redirect('/')


@app.route('/feedback/<int:feedback_id>/delete', methods=['Get','POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if session['username'] == feedback.user.username:
        db.session.delete(feedback)
        db.session.commit()
        flash(f'Feedback - {feedback.title} - deleted!')
        return redirect(f"/users/{feedback.user.username}")
    else:
        flash("You cant do that Bitch!!")
        return redirect('/')
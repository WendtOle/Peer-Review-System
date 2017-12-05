from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import models
import dbSeed
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PeerReviewSystem.db'
db = SQLAlchemy(app)


@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', user=session['user'])
    else:
        return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    currentUser = db.session().query(models.User).filter_by(email=email).first()

    if bcrypt.check_password_hash(currentUser.password, password):
        session['user'] = currentUser.email
        session['isConferenceChair'] = currentUser.isConferenceChair
    return redirect("/")


@app.route('/logout')
def logout():
    session.pop('user')
    session.pop('isConferenceChair')
    return redirect('/')


@app.route('/user/<user_id>')
def showUser(user_id):
    session = db.session()
    papersOfUser = session.query(models.Paper).filter(models.Paper.authors.any(id=user_id))
    currentUser = session.query(models.User).get(user_id)
    return render_template('userShowPage.html', user=currentUser, papers=papersOfUser)


@app.route('/paper/<paper_id>')
def showPaper(paper_id):
    session = db.session()
    currentPaper = session.query(models.Paper).get(paper_id)
    return render_template('paperShowPage.html', paper=currentPaper)


@app.route('/register')
def showRegisterPage():
    return render_template('register.html', users=models.User.query.all())


# TODO: check if email already exists
# TODO: check if email or password are empty
@app.route('/register', methods=['POST'])
def nothing():
    email = request.form['email']
    password = request.form['password']
    password_hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    db.session.add(models.User(email=email, password=password_hashed, isConferenceChair=False))
    db.session.commit()
    return redirect("/", code=302)


@app.route('/submitpaper/<author_id>', methods=['POST'])
def submitPaper(author_id):
    title = request.form['title']
    abstract = request.form['abstract']
    paper = models.Paper(title=title, abstract=abstract)

    session = db.session()
    author = session.query(models.User).get(author_id)
    paper.authors.append(author)

    session.add(paper)
    session.commit()
    return redirect("/user/" + author_id, code=302)


@app.route('/addAuthorToPaper/<paper_id>', methods=['POST'])
def addAuthorToPaper(paper_id):
    email = request.form['email']
    session = db.session()

    userToAdd = session.query(models.User).filter(models.User.email == email).first()
    paper = session.query(models.Paper).get(paper_id)
    paper.authors.append(userToAdd)
    session.commit()

    return redirect("/paper/" + paper_id, code=302)


def len(list):
    counter = 0
    for item in list:
        counter += 1
    return counter


@app.route('/addReviewerToPaper/<paper_id>', methods=['POST'])
def addReviewerToPaper(paper_id):
    email = request.form['email']
    session = db.session()

    reviewerToAdd = session.query(models.User).filter(models.User.email == email).first()
    paper = session.query(models.Paper).get(paper_id)
    authors = paper.authors
    if not reviewerToAdd in authors and len(paper.reviewersOfTable) < 3:
        paper.reviewersOfTable.append(reviewerToAdd)
    session.commit()

    return redirect("/paper/" + paper_id, code=302)


if __name__ == '__main__':
    dbSeed.init()
    app.run(debug=True)

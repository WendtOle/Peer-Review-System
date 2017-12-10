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
    print(session)
    if 'user' in session:
        return render_template('index.html')
    else:
        return render_template('login.html', users=models.User.query.all())


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    currentUser = db.session().query(models.User).filter_by(email=email).first_or_404()
    if bcrypt.check_password_hash(currentUser.password, password):
        session['logged_in'] = True
        session['user'] = currentUser.email
        session['isConferenceChair'] = currentUser.isConferenceChair
        session['user_id'] = currentUser.id
    return redirect("/user")


@app.route('/logout')
def logout():
    session.pop('logged_in')
    session.pop('user')
    session.pop('isConferenceChair')
    session.pop('user_id')
    return redirect('/')


@app.route('/user')
def showUser():
    if 'user' in session:
        if session['isConferenceChair']:
            return redirect("/admin",code=302)
        dbSession = db.session()
        papersOfUser = dbSession.query(models.Paper).filter(models.Paper.authors.any(id=session['user_id']))
        currentUser = dbSession.query(models.User).get(session['user_id'])
        papersToReview = dbSession.query(models.Paper).filter(models.Paper.reviewersOfTable.any(id = session['user_id']))
        return render_template('userShowPage.html', user=currentUser, papers=papersOfUser, papersToReview = papersToReview)
    else:
        return redirect("/", code=302)

@app.route('/admin')
def showAdminPage():
    if 'user' in session and session['isConferenceChair']:
        return render_template('admin.html',papers = models.Paper.query.all())
    else:
        return redirect("/", code=302)


@app.route('/paper/<paper_id>')
def showPaper(paper_id):
    if 'user' in session:
        dbSession = db.session()
        currentPaper = dbSession.query(models.Paper).get(paper_id)
        authors = currentPaper.authors
        userAboutToAccess = dbSession.query(models.User).filter(models.User.email == session['user']).first()
        if session['isConferenceChair'] or userAboutToAccess in authors:
            return render_template('paperShowPage.html', paper=currentPaper)

    else:
        return redirect("/", code=302)


@app.route('/register')
def showRegisterPage():
    return render_template('register.html')


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

@app.route('/submitScore', methods=['POST'])
def submitPaperScore():
    score = request.form['score']
    paper_id = request.form['paper_id']
    user_id = request.form['user_id']

    session = db.session()

    #queryAnswer = session.query(models.user_paper_review).filter(models.user_paper_review.user_id == user_id).first

    #print(queryAnswer)

    return redirect("/user", code=302)

@app.route('/paperSubmission')
def paperSubmissionPage():
    if 'user' not in session:
        return redirect("/")

    return render_template('paperSubmission.html')

@app.route('/reviewSubmission')
def reviewSubmissionPage():
    if 'user' not in session:
        return redirect("/")

    dbSession = db.session()
    currentUser = dbSession.query(models.User).get(session['user_id'])
    papersToReview = dbSession.query(models.Paper).filter(models.Paper.reviewersOfTable.any(id=session['user_id']))
    return render_template('reviewSubmission.html', user=currentUser, papersToReview=papersToReview)

if __name__ == '__main__':
    dbSeed.init()
    app.run(debug=True)

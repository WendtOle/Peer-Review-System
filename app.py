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
        if session['isConferenceChair']:
            return redirect("/admin", code=302)
        papersOfUser = db.session.query(models.Paper).filter(models.Paper.authors.any(id=session['user_id']))
        currentUser = db.session.query(models.User).get(session['user_id'])
        papersToReview = db.session.query(models.Paper).filter(models.Paper.reviewersOfTable.any(id=session['user_id']))
        return render_template('index.html', user=currentUser, papers=papersOfUser, papersToReview=papersToReview)
    else:
        return render_template('login.html', users=models.User.query.all())


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    currentUser = db.session.query(models.User).filter_by(email=email).first_or_404()
    if bcrypt.check_password_hash(currentUser.password, password):
        session['logged_in'] = True
        session['user'] = currentUser.email
        session['isConferenceChair'] = currentUser.isConferenceChair
        session['user_id'] = currentUser.id
    return redirect("/")


@app.route('/logout')
def logout():
    session.pop('logged_in')
    session.pop('user')
    session.pop('isConferenceChair')
    session.pop('user_id')
    return redirect('/')


@app.route('/admin')
def showAdminPage():
    if 'user' in session and session['isConferenceChair']:
        return render_template('admin.html', papers=models.Paper.query.all())
    else:
        return redirect("/", code=302)


@app.route('/paper/<paper_id>')
def showPaper(paper_id):
    if 'user' in session:
        currentPaper = db.session.query(models.Paper).get(paper_id)
        authors = currentPaper.authors
        reviewers = currentPaper.reviewersOfTable
        userAboutToAccess = db.session.query(models.User).filter(models.User.email == session['user']).first()
        if session['isConferenceChair']:
            scores = getScoreRowsQuery2(paper_id).all()
            finalScore = 0
            for score in scores:
                finalScore += score.score
            finalScore /= len(scores)

            return render_template('paper.html', paper=currentPaper, scores=scores, finalScore=finalScore)
        else:
            if userAboutToAccess in authors or userAboutToAccess in reviewers:
                return render_template('paper.html', paper=currentPaper)
            else:
                return redirect("/", code=307)
    return redirect("/", code=303)

def getScoreRowsQuery2(paperId):
    return db.session.query(models.PaperScores).filter(models.PaperScores.paperId == paperId)

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


@app.route('/paper/', methods=['POST'])
def submitPaper():
    title = request.form['title']
    abstract = request.form['abstract']
    authors = request.form.getlist('authors')
    authors.append(session['user'])

    paper = models.Paper(title=title, abstract=abstract)

    db.session.add(paper)
    db.session.commit()

    for author in authors:
        userToAdd = db.session.query(models.User).filter(models.User.email == author).first()
        paper = db.session.query(models.Paper).get(paper.id)
        paper.authors.append(userToAdd)
    db.session.commit()

    return redirect("/paper/" + str(paper.id), code=302)


def len(list):
    counter = 0
    for item in list:
        counter += 1
    return counter


@app.route('/addReviewerToPaper/<paper_id>', methods=['POST'])
def addReviewerToPaper(paper_id):
    email = request.form['email']
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

    scoreRow = getScoreRowsQuery(paper_id,user_id).first()
    if(scoreRow != None):
        scoreRow.score = score
    else:
        db.session.add(models.PaperScores(paperId=paper_id, userId=user_id, score=score))
    db.session.commit()
    return redirect("/", code=302)

def getScoreRowsQuery(paperId, userId):
    scoreRows = db.session.query(models.PaperScores).filter(
        models.PaperScores.userId == userId and models.PaperScores.paperId == paperId)
    return scoreRows

@app.route('/paperSubmission')
def paperSubmissionPage():
    if 'user' not in session:
        return redirect("/")
    allUsers = db.session.query(models.User).filter(models.User.id != session['user_id'])
    return render_template('paperSubmission.html', allUsers=allUsers)


@app.route('/reviewSubmission')
def reviewSubmissionPage():
    if 'user' not in session:
        return redirect("/")

    currentUser = db.session.query(models.User).get(session['user_id'])
    papersToReview = db.session.query(models.Paper).filter(models.Paper.reviewersOfTable.any(id=session['user_id']))
    return render_template('reviewSubmission.html', user=currentUser, papersToReview=papersToReview)


if __name__ == '__main__':
    dbSeed.init()
    app.run(debug=True)

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
    if isLoggedIn():
        if (isAdmin()):
            return adminDashboard()
        else:
            return userDashboard()
    else:
        return render_template('login.html', users=models.User.query.all())

def adminDashboard():
    papers = db.session.query(models.Paper).all()
    return render_template('adminDashboard.html', papers=papers)

def userDashboard():
    papersOfUser = db.session.query(models.Paper).filter(models.Paper.authors.any(id=session['user_id']))
    currentUser = db.session.query(models.User).get(session['user_id'])
    papersToReview = db.session.query(models.Paper).filter(models.Paper.reviewers.any(id=session['user_id']))
    return render_template('userDashboard.html', user=currentUser, papers=papersOfUser, papersToReview=papersToReview)

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


@app.route('/paper/<paper_id>')
def showPaper(paper_id):
    if isLoggedIn():
        currentPaper = db.session.query(models.Paper).get(paper_id)
        if isAdmin():
            scores = getScoreRowsQuery2(paper_id).all()
            finalScore = 0
            for score in scores:
                finalScore += score.score
            if (len(scores) > 0):
                finalScore /= len(scores)
            return render_template('paper.html', paper=currentPaper, scores=scores, finalScore=finalScore)
        else:
            if isUserAutorOrReviewer(currentPaper):
                return render_template('paper.html', paper=currentPaper)
            else:
                return abortBecauseNotAuthorOrReviewer()
    return abortBecauseNotLoggedIn()

# TODO: Better Name
def getScoreRowsQuery2(paperId):
    return db.session.query(models.PaperScores).filter(models.PaperScores.paperId == paperId)


@app.route('/register')
def showRegisterPage():
    return render_template('register.html')


# TODO: check if email already exists
# TODO: check if email or password are empty
# TODO: better method name
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
    reviewers = request.form.getlist('reviewers')

    paper = db.session.query(models.Paper).get(paper_id)
    amountOfReviewersToAdd = len(reviewers)
    amountOfPossibleReviewersToAdd = 3 - len(paper.reviewers)

    if amountOfPossibleReviewersToAdd >= amountOfReviewersToAdd:
        for user in reviewers:
            reviewerToAdd = db.session.query(models.User).filter(models.User.email == user).first()
            paper.reviewers.append(reviewerToAdd)
        db.session.commit()
    return redirect("/reviewer", code=302)

@app.route('/submitScore', methods=['POST'])
def submitPaperScore():
    score = request.form['score']
    paper_id = request.form['paper_id']
    user_id = request.form['user_id']

    scoreRow = getScoreRowsQuery(paper_id, user_id).first()
    if (scoreRow != None):
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
    if not isLoggedIn() or isAdmin():
        return redirect("/")
    userThatCouldBeCoAuthors = []
    allUsers = db.session.query(models.User).all()
    for user in allUsers:
        if user.id != session['user_id'] and not user.isConferenceChair:
            userThatCouldBeCoAuthors.append(user)
    return render_template('paperSubmission.html', allUsers=userThatCouldBeCoAuthors)


@app.route('/reviewSubmission')
def reviewSubmissionPage():
    if not isLoggedIn() or isAdmin():
        return redirect("/")

    currentUser = db.session.query(models.User).get(session['user_id'])
    papersToReview = db.session.query(models.Paper).filter(models.Paper.reviewers.any(id=session['user_id']))
    return render_template('reviewSubmission.html', user=currentUser, papersToReview=papersToReview)


@app.route('/reviewer', methods=['GET'])
def showAssignmentOfReviewers():
    if isLoggedIn() and isAdmin():
        papers = db.session.query(models.Paper).all()
        allUsers = db.session.query(models.User).all()
        paperWithPossibleReviewers = []
        for paper in papers:
            possibleReviewers = []
            for user in allUsers:
                if not user.isConferenceChair and user not in paper.reviewers and user not in paper.authors:
                    possibleReviewers.append(user)
            amountOfPossibleReviewers = 3 - len(paper.reviewers)
            paperWithPossibleReviewers.append({'paper':paper, 'possibleReviewers': possibleReviewers, 'amountOfPossibleReviewers':amountOfPossibleReviewers})
        return render_template('assignmentOfReviewers.html', paperWithPossibleReviewers= paperWithPossibleReviewers)
    return redirect("/")

@app.route('/paperDecision', methods=['GET'])
def finalDecision():
    if isLoggedIn() and isAdmin():
        papers = db.session.query(models.Paper).all()
        paperWithScores = []
        for paper in papers:
            scores = getScoreRowsQuery2(paper.id).all()
            finalScore = 0
            for score in scores:
                finalScore += score.score
            if (len(scores) > 0):
                finalScore /= len(scores)
            paperWithScores.append({'paper':paper,'scores':scores,'finalScore':finalScore})
        return render_template('finalDecisionPage.html', paperWithScores = paperWithScores)
    return redirect("/")

@app.route('/submitDecision', methods=['POST'])
def submitDecision():
    status = request.form['status']
    paper_id = request.form['paper_id']
    paper = db.session.query(models.Paper).filter(models.Paper.id == paper_id).first()

    if status == "accepted":
        paper.status = models.PaperStatus.ACCEPTED
    else:
        if status == "rejected":
            paper.status = models.PaperStatus.REJECTED
        else:
            paper.status = models.PaperStatus.UNDER_REVIEW
    db.session.commit()
    return redirect("/paperDecision", code=302)

def isLoggedIn():
    return 'user' in session

def isAdmin():
    return session['isConferenceChair']

def isUserAutorOrReviewer(paper):
    authors = paper.authors
    reviewers = paper.reviewers
    actualUser = db.session.query(models.User).filter(models.User.email == session['user']).first()
    return actualUser in authors or actualUser in reviewers

def abortBecauseNotAuthorOrReviewer():
    return redirect("/", code=307)


def abortBecauseNotLoggedIn():
    return redirect("/", code=303)


if __name__ == '__main__':
    dbSeed.init()
    app.run(debug=True)
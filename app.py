from flask import Flask, render_template, request, redirect, session, flash
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
        if isAdmin():
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
    papersToReview = getPapersToReviewForUser(currentUser.id)
    return render_template('userDashboard.html', user=currentUser, papers=papersOfUser, papersToReview=papersToReview)


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    currentUser = db.session.query(models.User).filter_by(email=email).first()
    if currentUser is not None:
        if bcrypt.check_password_hash(currentUser.password, password):
            session['user'] = currentUser.email
            session['isConferenceChair'] = (currentUser.role == models.UserRole.CONFERENCE_CHAIR)
            session['user_id'] = currentUser.id
        else:
            flash('Wrong Password!')
    else:
        flash('The user does not exist!')
    return redirect("/")


@app.route('/logout')
def logout():
    session.pop('user')
    session.pop('isConferenceChair')
    session.pop('user_id')
    return redirect('/')


@app.route('/paper/<paper_id>')
def showPaper(paper_id):
    if isLoggedIn():
        currentPaper = db.session.query(models.Paper).get(paper_id)
        if isAdmin():
            scores = getScoreRowsQuery(paper_id).all()
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


def getScoreRowsQuery(paperId):
    return db.session.query(models.PaperScores).filter(models.PaperScores.paperId == paperId)


@app.route('/register')
def showRegisterPage():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def registerUser():
    email = request.form['email']
    password = request.form['password']
    if email is '' or password is '':
        flash('Fields cannot be empty!')
        return redirect("/register")
    user = db.session.query(models.User).filter_by(email=email).first()
    if user is None:
        password_hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.add(models.User(email=email, password=password_hashed))
        db.session.commit()
    else:
        flash('This Email is already registered!')
    return redirect("/register")


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

    db.session.add(models.PaperScores(paperId=paper_id, userId=user_id, score=score))
    db.session.commit()
    return redirect("/reviewSubmission", code=302)


@app.route('/paperSubmission')
def paperSubmissionPage():
    if not isLoggedIn() or isAdmin():
        return redirect("/")
    userThatCouldBeCoAuthors = []
    allUsers = db.session.query(models.User).all()
    for user in allUsers:
        if user.id != session['user_id'] and user.role != models.UserRole.CONFERENCE_CHAIR:
            userThatCouldBeCoAuthors.append(user)
    return render_template('paperSubmission.html', allUsers=userThatCouldBeCoAuthors)


def getPapersToReviewForUser(userId):
    papersAssignedToUser = db.session.query(models.Paper).filter(models.Paper.reviewers.any(id=userId))
    papersToReview = []
    for paper in papersAssignedToUser:
        paperScored = db.session.query(models.PaperScores).filter(models.PaperScores.userId == userId).filter(
            models.PaperScores.paperId == paper.id)
        if len(paperScored) == 0:
            papersToReview.append(paper)
    return papersToReview


@app.route('/reviewSubmission')
def reviewSubmissionPage():
    if not isLoggedIn() or isAdmin():
        return redirect("/")
    currentUser = db.session.query(models.User).get(session['user_id'])
    papersToReview = getPapersToReviewForUser(currentUser.id)
    return render_template('reviewSubmission.html', user=currentUser, papersToReview=papersToReview)


@app.route('/reviewer', methods=['GET'])
def showAssignReviewer():
    if isLoggedIn() and isAdmin():
        papers = db.session.query(models.Paper).all()
        allUsers = db.session.query(models.User).filter(models.User.role == models.UserRole.REVIEWER)

        paperWithPossibleReviewers = []
        for paper in papers:
            possibleReviewers = []
            for user in allUsers:
                if user not in paper.reviewers and user not in paper.authors:
                    possibleReviewers.append(user)
            amountOfPossibleReviewers = 3 - len(paper.reviewers)
            paperWithPossibleReviewers.append({'paper': paper, 'possibleReviewers': possibleReviewers,
                                               'amountOfPossibleReviewers': amountOfPossibleReviewers,
                                               'amountOfAvailableReviewers': len(possibleReviewers)})
        return render_template('assignReviewer.html', paperWithPossibleReviewers=paperWithPossibleReviewers)
    return redirect("/")


@app.route('/assignUser', methods=['GET'])
def showAssignUser():
    if isLoggedIn() and isAdmin():
        users = db.session.query(models.User).filter(models.User.role == models.UserRole.USER)
        reviewers = db.session.query(models.User).filter(models.User.role == models.UserRole.REVIEWER)
        return render_template('assignUser.html', users=users, reviewers=reviewers)


@app.route('/setUserRole', methods=['POST'])
def setUserRole():
    if isLoggedIn() and isAdmin():
        users = request.form.getlist('users')
        for user in users:
            currentUser = db.session.query(models.User).filter(models.User.email == user).first()
            currentUser.role = models.UserRole.REVIEWER
            db.session.commit()
        return redirect('/assignUser')


@app.route('/scoreOverview', methods=['GET'])
def finalDecision():
    if isLoggedIn() and isAdmin():
        papers = db.session.query(models.Paper).all()
        paperWithScores = []
        for paper in papers:
            scores = getScoreRowsQuery(paper.id).all()
            finalScore = 0
            for score in scores:
                finalScore += score.score
            if (len(scores) > 0):
                finalScore /= len(scores)
            paperWithScores.append({'paper': paper, 'scores': scores, 'finalScore': finalScore})
        return render_template('scoreOverview.html', paperWithScores=paperWithScores)
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
    return redirect("/scoreOverview", code=302)


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

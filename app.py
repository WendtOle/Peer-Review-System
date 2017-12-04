from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import models
import dbSeed

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PeerReviewSystem.db'

db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html', users=models.User.query.all())

@app.route('/user/<user_id>')
def showUser(user_id):
    session = db.session()
    print(user_id)
    papersOfUser = session.query(models.Paper).filter(models.Paper.authors.any(id = user_id))
    currentUser = session.query(models.User).get(user_id)
    return render_template('userShowPage.html', user=currentUser, papers=papersOfUser)

@app.route('/register', methods=['POST'])
def nothing():
    email = request.form['email']
    password = request.form['password']
    db.session.add(models.User(email=email, password=password, isConferenceChair=False))
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
    print(models.Paper.query.all())
    return redirect("/user/" + author_id, code=302)

if __name__ == '__main__':
    dbSeed.init()
    app.run(debug=True)
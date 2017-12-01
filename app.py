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

@app.route('/papers')
def papers():
    return render_template('papers.html', papers=models.Paper.query.all())

@app.route('/register', methods=['POST'])
def nothing():
    email = request.form['email']
    password = request.form['password']
    db.session.add(models.User(email=email, password=password, isConferenceChair=False))
    db.session.commit()
    return redirect("/", code=302)

@app.route('/submitpaper', methods=['POST'])
def submitPaper():
    title = request.form['title']
    abstract = request.form['abstract']
    db.session.add(models.Paper(title=title, abstract=abstract))
    db.session.commit()
    return redirect("/papers", code=302)


if __name__ == '__main__':
    dbSeed.init()

    app.run(debug=True)

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PeerReviewSystem.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    isConferenceChair = db.Column(db.BOOLEAN)

@app.route('/')
def index():
    return render_template('index.html', users=User.query.all())

@app.route('/register', methods=['POST'])
def nothing():
    email = request.form['email']
    password = request.form['password']
    db.session.add(User(email=email,password=password,isConferenceChair=False))
    db.session.commit()
    return redirect("/", code=302)

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    db.session.add(User(email='superChairman@mail.com', password='12345',isConferenceChair = True))
    db.session.add(User(email='ole-wendt@freenet.de', password='forget', isConferenceChair=False))
    db.session.commit()

    print('all users: ', User.query.all())

    app.run(debug=True)

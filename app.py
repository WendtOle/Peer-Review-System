from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PeerReviewSystem.db'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


@app.route('/')
def index():
    return render_template('index.html', users=User.query.all())


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    db.session.add(User(email='superChairman@mail.com', password='12345'))
    db.session.commit()

    print('all users: ', User.query.all())

    app.run(debug=True)

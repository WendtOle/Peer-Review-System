from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PeerReviewSystem.sqlite3'

db = SQLAlchemy(app)
class User(db.Model):
   id = db.Column('user_id', db.Integer, primary_key=True)
   email = db.Column(db.String(100), unique=True)
   password = db.Column(db.String(100))

@app.route('/')
def index():
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
 
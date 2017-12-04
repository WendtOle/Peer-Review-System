from app import db


association_table = db.Table('association', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('paper_id', db.Integer, db.ForeignKey('papers.id'))
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    isConferenceChair = db.Column(db.BOOLEAN)
    papers = db.relationship("Paper", secondary=association_table)

class Paper(db.Model):
    __tablename__ = 'papers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    abstract = db.Column(db.String)
    authors = db.relationship("User", secondary=association_table)
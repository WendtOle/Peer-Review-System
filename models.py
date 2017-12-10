from app import db
import enum

user_paper_relation_table = db.Table('user_paper', db.Model.metadata,
                                     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                                     db.Column('paper_id', db.Integer, db.ForeignKey('papers.id'))
                                     )

user_paper_review_relation_table = db.Table('user_paper_review', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('paper_id', db.Integer, db.ForeignKey('papers.id')),
    db.Column('score',db.Integer)
)

class PaperStatus(enum.Enum):
    UNDER_REVIEW = "under review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    isConferenceChair = db.Column(db.BOOLEAN)
    papers = db.relationship("Paper", secondary=user_paper_relation_table)
    papersToReview = db.relationship("Paper", secondary=user_paper_review_relation_table)


class Paper(db.Model):
    __tablename__ = 'papers'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    status = db.Column(db.Enum(PaperStatus), default=PaperStatus.UNDER_REVIEW)
    abstract = db.Column(db.String)
    reviewScore = db.Column(db.Integer)
    authors = db.relationship("User", secondary=user_paper_relation_table)
    reviewersOfTable = db.relationship("User", secondary=user_paper_review_relation_table)

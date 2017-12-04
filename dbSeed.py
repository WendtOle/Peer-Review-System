import app
import models


def init():
    app.db.drop_all()
    app.db.create_all()
    session = app.db.session()
    session.add(models.User(email='superChairman@mail.com', password='12345', isConferenceChair=True))
    session.add(models.User(email='ole-wendt@freenet.de', password='forget', isConferenceChair=False))
    session.commit()

    print('all users: ', models.User.query.all())

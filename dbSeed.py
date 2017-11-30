import app
import models


def init():
    app.db.drop_all()
    app.db.create_all()
    app.db.session.add(models.User(email='superChairman@mail.com', password='12345', isConferenceChair=True))
    app.db.session.add(models.User(email='ole-wendt@freenet.de', password='forget', isConferenceChair=False))
    app.db.session.commit()

    print('all users: ', models.User.query.all())

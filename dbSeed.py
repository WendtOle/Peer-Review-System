import app
import models


def init():
    app.db.drop_all()
    app.db.create_all()
    session = app.db.session()
    user01 = models.User(email='superChairman@mail.com', password='12345', isConferenceChair=True)
    session.add(user01)
    session.add(models.User(email='ole-wendt@freenet.de', password='forget', isConferenceChair=False))
    session.add(models.Paper(title="Fantastic Paper over 9000", abstract="Abstract about this Paper", authors=[user01]))
    session.commit()

    print('all users: ', models.User.query.all())

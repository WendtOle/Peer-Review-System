import app
import models


def init():
    app.db.drop_all()
    app.db.create_all()
    session = app.db.session()

    user01 = models.User(email='conferenceChairMen@mail.com', password='12345', isConferenceChair=True)
    user02 = models.User(email='ole-wendt@freenet.de', password='shadowNinja', isConferenceChair=False)
    user03 = models.User(email='timurOezer@web.de', password='forgetPassword', isConferenceChair=False)
    session.add(user01)
    session.add(user02)
    session.add(user03)

    session.add(models.Paper(title="Das Leben und die Aufzucht von wilden Schildkröten in der Antarktis", abstract="Fuchunkulus", authors=[user01,user02]))
    session.add(models.Paper(title="33 gute Gründe Kalender an die Wand zu hängen und sie nicht auf den Boden zu legen", abstract="Fuchunkulus", authors=[user01]))
    session.add(models.Paper(title="Die verblüffende und zugleich erschreckende Wahrheit hinter der Herstellung traditioneller Weidenkörbe im alten Polen", abstract="Fuchunkulus", authors=[user02]))
    session.commit()

    print('all users: ', models.User.query.all())

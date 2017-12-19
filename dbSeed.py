import app
import models


def init():
    app.db.drop_all()
    app.db.create_all()
    session = app.db.session()

    user01 = models.User(email='conferenceChairMen@mail.com',
                         password=app.bcrypt.generate_password_hash('conferenceChairMen').decode('utf-8'),
                         role=models.UserRole.CONFERENCE_CHAIR)
    user02 = models.User(email='ole-wendt@freenet.de',
                         password=app.bcrypt.generate_password_hash('ole-wendt').decode('utf-8'),
                         role=models.UserRole.REVIEWER)
    user03 = models.User(email='timurOezer@web.de',
                         password=app.bcrypt.generate_password_hash('timurOezer').decode('utf-8'),
                         role=models.UserRole.REVIEWER)
    user04 = models.User(email='tino@schulz.de', password=app.bcrypt.generate_password_hash('tino').decode('utf-8'))
    user05 = models.User(email='spino@mulz.de', password=app.bcrypt.generate_password_hash('spino').decode('utf-8'))

    session.add(user01)
    session.add(user02)
    session.add(user03)
    session.add(user04)
    session.add(user05)

    paper01 = models.Paper(title="Das Leben und die Aufzucht von wilden Schildkröten in der Antarktis",
                           abstract="Fuchunkulus", authors=[user01, user02])
    session.add(paper01)

    paper02 = models.Paper(title="33 gute Gründe Kalender an die Wand zu hängen und sie nicht auf den Boden zu legen",
                           abstract="Fuchunkulus", authors=[user01])
    session.add(paper02)

    paper02.reviewers.append(user02)
    paper02.reviewers.append(user03)
    paper02.reviewers.append(user02)

    session.add(models.Paper(
        title="Die verblüffende und zugleich erschreckende Wahrheit hinter der Herstellung traditioneller Weidenkörbe im alten Polen",
        abstract="Fuchunkulus", authors=[user02]))

    session.commit()

    session.add(models.PaperScores(paperId=paper02.id, userId=user02.id, score=-2))
    session.add(models.PaperScores(paperId=paper02.id, userId=user03.id, score=1))
    session.add(models.PaperScores(paperId=paper02.id, userId=user01.id, score=2))

    session = app.db.session()

    session.commit()

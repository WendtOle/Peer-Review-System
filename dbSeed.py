import app
import models


def init():
    app.db.drop_all()
    app.db.create_all()
    session = app.db.session()

    user01 = models.User(email='conferenceChairMen@admin.de',
                         password=app.bcrypt.generate_password_hash('conferenceChairMen').decode('utf-8'),
                         role=models.UserRole.CONFERENCE_CHAIR)
    user02 = models.User(email='olewendt@htwberlin.de',
                         password=app.bcrypt.generate_password_hash('olewendt').decode('utf-8'),
                         role=models.UserRole.REVIEWER)
    user03 = models.User(email='timuroezer@htwberlin.de',
                         password=app.bcrypt.generate_password_hash('timuroezer').decode('utf-8'),
                         role=models.UserRole.REVIEWER)
    user04 = models.User(email='carriefisher@starwars.com',
                         password=app.bcrypt.generate_password_hash('carriefisher').decode('utf-8'))
    user05 = models.User(email='oscarisaac@starwars.com',
                         password=app.bcrypt.generate_password_hash('oscarisaac').decode('utf-8'))
    user06 = models.User(email='johnboyega@starwars.com',
                         password=app.bcrypt.generate_password_hash('johnboyega').decode('utf-8'))
    user07 = models.User(email='daisyridley@starwars.com',
                         password=app.bcrypt.generate_password_hash('daisyridley').decode('utf-8'))



    session.add(user01)
    session.add(user02)
    session.add(user03)
    session.add(user04)
    session.add(user05)
    session.add(user06)
    session.add(user07)

    placeholderText = "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?"

    paper01 = models.Paper(title="Das Leben und die Aufzucht von wilden Schildkröten in der Antarktis",
                           abstract=placeholderText, authors=[user02])
    session.add(paper01)

    paper02 = models.Paper(title="33 gute Gründe Kalender an die Wand zu hängen und sie nicht auf den Boden zu legen",
                           abstract=placeholderText, authors=[user03])
    session.add(paper02)

    paper02.reviewers.append(user02)
    paper02.reviewers.append(user03)
    paper02.reviewers.append(user02)

    session.add(models.Paper(
        title="Die verblüffende und zugleich erschreckende Wahrheit hinter der Herstellung traditioneller Weidenkörbe im alten Polen",
        abstract=placeholderText, authors=[user02]))

    session.commit()

    session.add(models.PaperScores(paperId=paper02.id, userId=user02.id, score=-2))
    session.add(models.PaperScores(paperId=paper02.id, userId=user03.id, score=1))
    session.add(models.PaperScores(paperId=paper02.id, userId=user01.id, score=2))

    session = app.db.session()

    session.commit()

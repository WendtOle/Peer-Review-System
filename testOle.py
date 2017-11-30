from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hallo Welt"

@app.route("/lurch")
def lurchMethode():
    print('Hello world!')
    return "Timur ist ein Lurch"

@app.route("/template/<user>")
def renderTemplate(user):
    return render_template('testHello.html',name = user)

if __name__ == "__main__":
    app.run(debug=True)
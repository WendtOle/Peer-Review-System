from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hallo Welt"

@app.route("/lurch")
def lurchMethode():
    print('Hello world!')
    return "Timur ist ein Lurch"

if __name__ == "__main__":
    app.run(debug=True)

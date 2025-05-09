from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Bem-vindo ao Sistema do Ministério Maná!</h1><p>Glória a DEUS!</p>"

if __name__ == "__main__":
    app.run(debug=True)
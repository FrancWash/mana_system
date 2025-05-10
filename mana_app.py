from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Bem-vindo ao Sistema do Ministério Maná!</h1><p>Glória a DEUS!</p>"

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "mana2025":
            return redirect(url_for("home"))
        else:
            error = "Usuário ou senha incorretos."
    return render_template_string("""
        <h2>Login Ministério Maná</h2>
        {% if error %}
            <p style="color:red;">{{ error }}</p>
        {% endif %}
        <form method="post">
            Usuário: <input type="text" name="username"> <br>
            Senha: <input type="password" name="password"><br>
            <input type="submit" value="Entrar">
        </form>
    """, error=error)    

if __name__ == "__main__":
    import os
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
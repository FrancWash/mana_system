from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

escala_maio = [
    {"data": "Quinta 08/05", "responsaveis": "Ana Claudia"},
    {"data": "Domingo 11/05 - Manhã", "responsaveis": "Clóvis / Telma"},
    {"data": "Domingo 11/05 - Noite", "responsaveis": "Vanessa / Franc"},
    {"data": "Quinta-feira 15/05", "responsaveis": "Renata"},
    {"data": "Domingo 18/05 - Manhã", "responsaveis": "Vicentina / Franc"},
    {"data": "Domingo 18/05 - Noite", "responsaveis": "Thiago / Telma"},
    {"data": "Quinta-feira 22/05", "responsaveis": "Ana Claudia"},
    {"data": "Domingo 25/05 - Manhã", "responsaveis": "Clóvis / Fernanda"},
    {"data": "Domingo 25/05 - Noite", "responsaveis": "Thiago / Vanessa"},
    {"data": "Quinta-feira 29/05", "responsaveis": "Adelmo"}
]

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
            return redirect(url_for("escala"))
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

@app.route("/escala", methods=["GET", "POST"])
def escala():
    if request.method == "POST":
        for i in range(len(escala_maio)):
            nova_data = request.form.get(f"data_{i}")
            novos_responsaveis = request.form.get(f"resp_{i}")
            escala_maio[i]["data"] = nova_data
            escala_maio[i]["responsaveis"] = novos_responsaveis
        return redirect(url_for("escala"))

    return render_template_string("""
        <h2>Escala do Ministério Maná - Maio</h2>
        <form method="post">
            <table border="1" cellpadding="5">
                <tr><th>Data</th><th>Responsáveis</th></tr>
                {% for i in range(escala|length) %}
                <tr>
                    <td><input type="text" name="data_{{ i }}" value="{{ escala[i].data }}"></td>
                    <td><input type="text" name="resp_{{ i }}" value="{{ escala[i].responsaveis }}"></td>
                </tr>
                {% endfor %}
            </table>
            <br>
            <input type="submit" value="Salvar Alterações">
        </form>
        <br>
        <a href="/">← Voltar</a>
    """, escala=escala_maio)

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

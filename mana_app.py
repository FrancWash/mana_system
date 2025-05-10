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
    return render_template_string("""
        <div style="margin-bottom: 20px;">
            <a href="/" style="margin-right: 10px;">🏠 Início</a>
            <a href="/login" style="margin-right: 10px;">🔐 Login</a>
            <a href="/escala" style="margin-right: 10px;">📋 Escala</a>
            <a href="/controle">📦 Controle</a>
        </div>

        <h1>Bem-vindo ao Sistema do Ministério Maná!</h1>
        <p>Glória a DEUS!</p>
    """)

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

controle_estoque = [
    {"produto": "Arroz (1kg)", "caixa": 43, "prateleira": 0, "vencidos": 1},
    {"produto": "Feijão", "caixa": 43, "prateleira": 9, "vencidos": 2},
    {"produto": "Óleo", "caixa": 8, "prateleira": 15, "vencidos": 1},
    {"produto": "Fubá", "caixa": 0, "prateleira": 41, "vencidos": 0},
    {"produto": "Farinha de mandioca", "caixa": 0, "prateleira": 23, "vencidos": 0},
    {"produto": "Farinha de trigo", "caixa": 0, "prateleira": 12, "vencidos": 0},
    {"produto": "Molho de tomate", "caixa": 21, "prateleira": 26, "vencidos": 0},
    {"produto": "Café", "caixa": 0, "prateleira": 16, "vencidos": 0},
    {"produto": "Açúcar", "caixa": 28, "prateleira": 10, "vencidos": 0},
    {"produto": "Sal", "caixa": 0, "prateleira": 24, "vencidos": 0},
    {"produto": "Biscoito salgado", "caixa": 0, "prateleira": 40, "vencidos": 0},
    {"produto": "Biscoito doce", "caixa": 0, "prateleira": 41, "vencidos": 0},
    {"produto": "Sardinha", "caixa": 0, "prateleira": 36, "vencidos": 0},
    {"produto": "Macarrão", "caixa": 44, "prateleira": 28, "vencidos": 0},
    {"produto": "Milho", "caixa": 0, "prateleira": 25, "vencidos": 0},
    {"produto": "Achocolatado", "caixa": 0, "prateleira": 13, "vencidos": 0},
    {"produto": "Tempero pronto", "caixa": 0, "prateleira": 16, "vencidos": 0},
    {"produto": "Sabonetes", "caixa": 0, "prateleira": 56, "vencidos": 0},
    {"produto": "Pasta de dente", "caixa": 0, "prateleira": 36, "vencidos": 0},
    {"produto": "Escova de dente", "caixa": 0, "prateleira": 14, "vencidos": 0},
    {"produto": "Absorventes", "caixa": 0, "prateleira": 16, "vencidos": 0},
    {"produto": "Papel higiênico", "caixa": 0, "prateleira": 9, "vencidos": 0},
    {"produto": "Chupeta", "caixa": 0, "prateleira": 1, "vencidos": 0}
]

@app.route("/controle", methods=["GET", "POST"])
def controle():
    if request.method == "POST":
        for i in range(len(controle_estoque)):
            controle_estoque[i]["caixa"] = int(request.form.get(f"caixa_{i}", 0))
            controle_estoque[i]["prateleira"] = int(request.form.get(f"prateleira_{i}", 0))
            controle_estoque[i]["vencidos"] = int(request.form.get(f"vencidos_{i}", 0))
        return redirect(url_for("controle"))

    return render_template_string("""
        <h2>Controle de Alimentos e Kits - Ministério Maná</h2>
        <form method="post">
            <table border="1" cellpadding="5">
                <tr><th>Produto</th><th>Caixa</th><th>Prateleira</th><th>Vencidos</th></tr>
                {% for i in range(estoque|length) %}
                <tr>
                    <td>{{ estoque[i].produto }}</td>
                    <td><input type="number" name="caixa_{{ i }}" value="{{ estoque[i].caixa }}"></td>
                    <td><input type="number" name="prateleira_{{ i }}" value="{{ estoque[i].prateleira }}"></td>
                    <td><input type="number" name="vencidos_{{ i }}" value="{{ estoque[i].vencidos }}"></td>
                </tr>
                {% endfor %}
            </table>
            <br>
            <input type="submit" value="Salvar Alterações">
        </form>
        <br>
        <a href="/">← Voltar</a>
    """, estoque=controle_estoque)


if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

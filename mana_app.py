from flask import Flask, request, redirect, url_for, render_template_string, send_from_directory
import os

app = Flask(__name__)

# Escala de Maio (mantida)
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
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ministério Maná</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <div class="container" style="text-align: center; background-color: #fff9e6; padding: 20px; border-radius: 12px; max-width: 600px; margin: auto;">
                <img src="{{ url_for('static', filename='banner_mana.jpg') }}" alt="Banner Ministério Maná" class="banner-img">
                <h1>🙌 Bem-vindo ao Sistema do Ministério Maná</h1>
                <p style="font-style: italic;">"Quem se compadece do pobre empresta ao Senhor, que lhe retribuirá o benefício."<br><strong>– Provérbios 19:17</strong></p>
                <ul style="list-style: none; padding: 0; font-size: 1.2em;">
                    <li><a href='/login'>🔐 Login</a></li>
                    <li><a href='/escala'>📋 Escala</a></li>
                    <li><a href='/controle'>📦 Controle</a></li>
                    <li><a href='/fotos'>👥 Fotos da Equipe</a></li>
                    <li><a href='/familias'>👨‍👩‍👧 Cadastro de Famílias</a></li>
                </ul>
            </div>
        </body>
        </html>
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
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
            <title>Login - Ministério Maná</title>
        </head>
        <body>
            <h2>Login Ministério Maná</h2>
            {% if error %}
                <p style="color:red;">{{ error }}</p>
            {% endif %}
            <form method="post">
                Usuário: <input type="text" name="username"> <br>
                Senha: <input type="password" name="password"><br>
                <input type="submit" value="Entrar">
            </form>
            <br>
            <a href="/">← Voltar</a>
        </body>
        </html>
    """, error=error)

@app.route("/escala", methods=["GET", "POST"])
def escala():
    if request.method == "POST":
        for i in range(len(escala_maio)):
            escala_maio[i]["data"] = request.form.get(f"data_{i}")
            escala_maio[i]["responsaveis"] = request.form.get(f"resp_{i}")
        return redirect(url_for("escala"))

    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Escala - Ministério Maná</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <div class="container">
                <h1>📋 Escala do Ministério Maná - Maio</h1>
                <form method="post">
                    <table>
                        <tr><th>Data</th><th>Responsáveis</th></tr>
                        {% for i in range(escala|length) %}
                        <tr>
                            <td><input type="text" name="data_{{ i }}" value="{{ escala[i].data }}"></td>
                            <td><input type="text" name="resp_{{ i }}" value="{{ escala[i].responsaveis }}"></td>
                        </tr>
                        {% endfor %}
                    </table>
                    <br>
                    <button type="submit">Salvar Alterações</button>
                </form>
                <br>
                <a href="/">← Voltar</a>
            </div>
        </body>
        </html>
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
        <!DOCTYPE html>
        <html>
        <head>
            <title>Controle de Estoque - Ministério Maná</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <div class="container">
                <h1>📦 Controle de Alimentos e Kits - Ministério Maná</h1>
                <form method="post">
                    <table>
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
                    <button type="submit">Salvar Alterações</button>
                </form>
                <br>
                <a href="/">← Voltar</a>
            </div>
        </body>
        </html>
    """, estoque=controle_estoque)

    cadastro_familias = []

@app.route("/")
def home():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
            <title>Ministério Maná</title>
        </head>
        <body>
            <div class="container">
                <h1>🙌 Bem-vindo ao Sistema do Ministério Maná</h1>
                <p style="font-size: 1.2em;">"Quem se compadece do pobre empresta ao Senhor, que lhe retribuirá o benefício."<br><strong>– Provérbios 19:17</strong></p>
                <img src="{{ url_for('static', filename='banner_mana.jpg') }}" alt="Banner Ministério Maná" class="banner-img">
                <ul style="list-style: none; padding: 0;">
                    <li><a href='/login'>🔐 Login</a></li>
                    <li><a href='/escala'>📋 Escala</a></li>
                    <li><a href='/controle'>📦 Controle de Estoque</a></li>
                    <li><a href='/fotos'>👥 Fotos da Equipe</a></li>
                    <li><a href='/familias'>👨‍👩‍👧 Cadastro de Famílias</a></li>
                </ul>
            </div>
        </body>
        </html>
    ")

@app.route("/familias", methods=["GET", "POST"])
def familias():
    if request.method == "POST":
        nome = request.form.get("nome")
        lider = request.form.get("lider")
        endereco = request.form.get("endereco")
        data = request.form.get("data")
        cadastro_familias.append({"nome": nome, "lider": lider, "endereco": endereco, "data": data})
        return redirect(url_for("familias"))

    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
            <title>Cadastro de Famílias</title>
        </head>
        <body>
            <div class="container">
                <h2>&#128106; Cadastro de Famílias</h2>
                <form method="post">
                    <label>Nome da família ou responsável:</label>
                    <input type="text" name="nome" required><br>
                    <label>Nome do líder de célula:</label>
                    <input type="text" name="lider" required><br>
                    <label>Endereço ou bairro (célula):</label>
                    <input type="text" name="endereco" required><br>
                    <label>Data da entrega da cesta:</label>
                    <input type="text" name="data" required><br>
                    <input type="submit" value="Cadastrar">
                </form>
                <br>
                <h3>Famílias Cadastradas</h3>
                <ul>
                    {% for f in familias %}
                        <li><strong>{{ f.nome }}</strong> | Líder: {{ f.lider }} | {{ f.endereco }} | Entrega: {{ f.data }}</li>
                    {% endfor %}
                </ul>
                <br><a href="/">← Voltar</a>
            </div>
        </body>
        </html>
    """, familias=cadastro_familias)

@app.route("/fotos")
def fotos():
    imagens = [
        {"arquivo": "equipe1.jpg", "descricao": "Workshop da Assistência Social"},
        {"arquivo": "equipe2.jpg", "descricao": "Organização do estoque no Maná"},
        {"arquivo": "equipe3.jpg", "descricao": "Confraternização do Maná"}
    ]
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fotos da Equipe - Ministério Maná</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <div class="container">
                <h1>👥 Fotos da Equipe do Ministério Maná</h1>
                {% for foto in imagens %}
                    <div style="margin-bottom: 30px;">
                        <img src="{{ url_for('static', filename=foto.arquivo) }}" alt="Equipe" width="100%" style="max-width: 500px; border-radius: 8px;"><br>
                        <strong>{{ foto.descricao }}</strong>
                    </div>
                {% endfor %}
                <br>
                <a href="/">← Voltar</a>
            </div>
        </body>
        </html>
    """, imagens=imagens)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, request, redirect, url_for, render_template_string, send_from_directory, session
import os
import json
from datetime import datetime

# Caminho absoluto do arquivo JSON
json_path = os.path.join(os.path.dirname(__file__), "familias.json")

# Função para carregar os dados existentes
def carregar_familias():
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Função para salvar os dados
def salvar_familias(dados):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Lista que será usada pela aplicação
cadastro_familias = carregar_familias()

app = Flask(__name__)
app.secret_key = "supersecretkey"

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

# Middleware simples para proteger rotas
def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get("logado"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

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
            <header>🌾 Ministério Maná - Sistema Interno</header>
            <div class="container">
                <h1>🙌 Bem-vindo ao Sistema do Ministério Maná</h1>
                <p style="font-style: italic;">"Quem se compadece do pobre empresta ao Senhor, que lhe retribuirá o benefício."<br><strong>– Provérbios 19:17</strong></p>
                <a href='/login'>🔐 Login</a>
            </div>
            <footer>✨ “Servi uns aos outros, cada um conforme o dom que recebeu...” – 1 Pedro 4:10</footer>
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
            session["logado"] = True
            return redirect(url_for("painel"))
        else:
            error = "Usuário ou senha incorretos."
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <div class="container">
                <h2>🔐 Login Ministério Maná</h2>
                {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
                <form method="post">
                    <input type="text" name="username" placeholder="Usuário" required><br>
                    <input type="password" name="password" placeholder="Senha" required><br>
                    <input type="submit" value="Entrar">
                </form>
            </div>
        </body>
        </html>
    """, error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/painel")
@login_required
def painel():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Painel</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <div class="container">
                <h1>📋 Painel do Ministério Maná</h1>
                <ul>
                    <li><a href='/escala'>📅 Escala</a></li>
                    <li><a href='/controle'>📦 Controle</a></li>
                    <li><a href='/fotos'>👥 Fotos</a></li>
                    <li><a href='/familias'>👨‍👩‍👧 Cadastro de Famílias</a></li>
                    <li><a href='/logout'>🚪 Sair</a></li>
                </ul>
            </div>
        </body>
        </html>
    """)


# Arquivo de escalas por mês
ESCALAS_FILE = "escalas.json"

# Carrega ou inicializa escalas
if os.path.exists(ESCALAS_FILE):
    with open(ESCALAS_FILE, "r") as f:
        escalas_mensais = json.load(f)
else:
    escalas_mensais = {}

@app.route("/escala", methods=["GET", "POST"])
def escala():
    hoje = datetime.now()
    mes_atual = request.args.get("mes") or hoje.strftime("%m")
    ano_atual = request.args.get("ano") or hoje.strftime("%Y")
    chave = f"{mes_atual}-{ano_atual}"

    if chave not in escalas_mensais:
        escalas_mensais[chave] = [
            {"data": "", "responsaveis": ""} for _ in range(10)
        ]

    if request.method == "POST":
        for i in range(len(escalas_mensais[chave])):
            escalas_mensais[chave][i]["data"] = request.form.get(f"data_{i}", "")
            escalas_mensais[chave][i]["responsaveis"] = request.form.get(f"resp_{i}", "")
        with open(ESCALAS_FILE, "w") as f:
            json.dump(escalas_mensais, f)
        return redirect(url_for("escala", mes=mes_atual, ano=ano_atual))

    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Escala - Ministério Maná</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <div class="container">
                <h1>📋 Escala do Ministério Maná - {{ mes }}/{{ ano }}</h1>
                <form method="get">
                    <label>Selecione o mês e ano:</label>
                    <select name="mes">
                        {% for m in range(1, 13) %}
                            <option value="{{'%02d' % m}}" {% if mes == '%02d' % m %}selected{% endif %}>{{'%02d' % m}}</option>
                        {% endfor %}
                    </select>
                    <select name="ano">
                        {% for a in range(2024, 2031) %}
                            <option value="{{a}}" {% if ano == a|string %}selected{% endif %}>{{a}}</option>
                        {% endfor %}
                    </select>
                    <button type="submit">🔄 Ver Escala</button>
                </form>
                <br>
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
                <a href="/">Voltar</a>
            </div>
        </body>
        </html>
    """, escala=escalas_mensais[chave], mes=mes_atual, ano=ano_atual) 

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
                <p style="font-style: italic;">"Porque tive fome, e me destes de comer..."<br><strong>– Mateus 25:35</strong></p>

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

                <footer style="margin-top: 40px; background-color: #2e4a7d; color: white; padding: 10px; border-radius: 8px;">
                    💙 “A alma generosa prosperará; quem dá alívio aos outros, alívio receberá.” – Provérbios 11:25
                </footer>
            </div>
        </body>
        </html>
    """, estoque=controle_estoque)


cadastro_familias = []

@app.route("/familias", methods=["GET", "POST"])
def familias():
    mensagem = ""
    if request.method == "POST":
        nome = request.form.get("nome").strip()
        lider = request.form.get("lider")
        endereco = request.form.get("endereco")
        data = request.form.get("data")

        # Verifica se a família já existe
        familia_existente = next((f for f in cadastro_familias if f["nome"].lower() == nome.lower()), None)

        if familia_existente:
            familia_existente["entregas"].append(data)
        else:
            cadastro_familias.append({
                "nome": nome,
                "lider": lider,
                "endereco": endereco,
                "entregas": [data]
            })

        salvar_familias(cadastro_familias)
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
                    <input type="submit" value="Cadastrar/Atualizar">
                </form>
                <br>
                <h3>Famílias Cadastradas</h3>
                <ul>
                    {% for f in familias %}
                        <li>
                            <strong>{{ f.nome }}</strong> | Líder: {{ f.lider }} | {{ f.endereco }}<br>
                            🧺 Entregas: {{ f.entregas|length }} - {{ f.entregas|join(', ') }}
                            {% if f.entregas|length == 3 %}<br><span style="color:orange;font-weight:bold;">⚠️ Terceira cesta! Validar com líder.</span>{% endif %}
                        </li><br>
                    {% endfor %}
                </ul>
                <br><a href="/">&#8592; Voltar</a>
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
            <style>
                .galeria {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 30px;
                    justify-content: center;
                }
                .foto-box {
                    text-align: center;
                    max-width: 500px;
                    background: #fefefe;
                    padding: 15px;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                .foto-box img {
                    width: 100%;
                    border-radius: 8px;
                }
                .foto-box strong {
                    display: block;
                    margin-top: 10px;
                    color: #2e4a7d;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>👥 Galeria da Equipe do Ministério Maná</h1>
                <p style="font-style: italic;">"Oh! Quão bom e quão suave é que os irmãos vivam em união."<br><strong>– Salmos 133:1</strong></p>

                <div class="galeria">
                    {% for foto in imagens %}
                        <div class="foto-box">
                            <img src="{{ url_for('static', filename=foto.arquivo) }}" alt="Equipe">
                            <strong>{{ foto.descricao }}</strong>
                        </div>
                    {% endfor %}
                </div>

                <br><a href="/">← Voltar</a>

                <footer style="margin-top: 40px; background-color: #2e4a7d; color: white; padding: 10px; border-radius: 8px;">
                    ✝️ “Onde há unidade, ali o Senhor ordena a bênção.” – Salmos 133:3
                </footer>
            </div>
        </body>
        </html>
    """, imagens=imagens)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
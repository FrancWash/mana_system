from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template_string,
    send_from_directory,
    session,
    make_response,
)
import os
import json
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

RELATORIOS_FILE = "relatorios.json"

# Carrega ou inicializa relatórios
if os.path.exists(RELATORIOS_FILE):
    with open(RELATORIOS_FILE, "r") as f:
        relatorios = json.load(f)
else:
    relatorios = []


# Conexão com o banco PostgreSQL
import psycopg2


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("PGHOST"),
        database=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        port=os.getenv("PGPORT"),
    )
    return conn


def criar_tabela_familias():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS familias (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            lider TEXT NOT NULL,
            endereco TEXT NOT NULL,
            entregas TEXT[]
        )
    """
    )
    conn.commit()
    cur.close()
    conn.close()


def salvar_familias(lista_familias):
    conn = get_db_connection()
    cur = conn.cursor()

    # Apaga tudo antes de inserir (simples, para substituir por completo)
    cur.execute("DELETE FROM familias")

    for f in lista_familias:
        cur.execute(
            "INSERT INTO familias (nome, lider, endereco, entregas) VALUES (%s, %s, %s, %s)",
            (f["nome"], f["lider"], f["endereco"], f["entregas"]),
        )
    conn.commit()
    cur.close()
    conn.close()


def carregar_familias():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nome, lider, endereco, entregas FROM familias")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    familias = []
    for row in rows:
        familias.append(
            {
                "nome": row[0],
                "lider": row[1],
                "endereco": row[2],
                "entregas": row[
                    3
                ],  # Isso já vem como lista do tipo ARRAY no PostgreSQL
            }
        )

    return familias


# Lista que será usada pela aplicação
# cadastro_familias = carregar_familias()

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
    {"data": "Quinta-feira 29/05", "responsaveis": "Adelmo"},
]


# Middleware simples para proteger rotas
def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get("logado"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


@app.route("/relatorio", methods=["GET", "POST"])
@login_required
def relatorio():
    if request.method == "POST":
        data = request.form.get("data") or datetime.now().strftime("%d/%m/%Y")
        periodo = request.form.get("periodo")
        responsaveis = request.form.get("responsaveis")
        vencimento_junho = request.form.get("vencimento_junho")
        vencimento_julho = request.form.get("vencimento_julho")
        higiene = request.form.get("higiene")
        cestas = request.form.get("cestas")
        realizado = request.form.get("realizado")
        doacoes = request.form.get("doacoes")
        faltando = request.form.get("faltando")
        solicitacoes = request.form.get("solicitacoes")
        palavra = request.form.get("palavra")

        relatorios.append(
            {
                "data": data,
                "periodo": periodo,
                "responsaveis": responsaveis,
                "vencimento_junho": vencimento_junho,
                "vencimento_julho": vencimento_julho,
                "higiene": higiene,
                "cestas": cestas,
                "realizado": realizado,
                "doacoes": doacoes,
                "faltando": faltando,
                "solicitacoes": solicitacoes,
                "palavra": palavra,
            }
        )

        with open(RELATORIOS_FILE, "w") as f:
            json.dump(relatorios, f)

        return redirect(url_for("relatorio"))

    return render_template_string(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relatório do Dia - Ministério Maná</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <div class="container">
            <h2>📋 Registro de Relatório do Dia</h2>
            <form method="post">
                <label>Data:</label>
                <input type="text" name="data" placeholder="dd/mm/aaaa">
                <label>Período (ex: Manhã / Noite):</label>
                <input type="text" name="periodo">
                <label>Responsáveis:</label>
                <input type="text" name="responsaveis">
                <label>Vencimento em Junho:</label>
                <textarea name="vencimento_junho"></textarea>
                <label>Vencimento a partir de Julho:</label>
                <textarea name="vencimento_julho"></textarea>
                <label>Kits de Higiene:</label>
                <textarea name="higiene"></textarea>
                <label>Cestas Montadas:</label>
                <textarea name="cestas"></textarea>
                <label>Realizado:</label>
                <textarea name="realizado"></textarea>
                <label>Doações Recebidas:</label>
                <textarea name="doacoes"></textarea>
                <label>Itens em Falta:</label>
                <textarea name="faltando"></textarea>
                <label>Solicitações para próxima escala:</label>
                <textarea name="solicitacoes"></textarea>
                <label>Compartilhamento da Palavra:</label>
                <textarea name="palavra"></textarea>
                <input type="submit" value="Salvar Relatório">
            </form>

            <h3>📑 Relatórios Anteriores</h3>
            <ul>
                {% for r in relatorios|reverse %}
                <li>
                    <strong>{{ r.data }} - {{ r.periodo }}</strong><br>
                    Responsáveis: {{ r.responsaveis }}<br>
                    Cestas: {{ r.cestas }}<br>
                    Itens em falta: {{ r.faltando }}<br>
                    Palavra: {{ r.palavra }}<br><br>
                </li>
                {% endfor %}
            </ul>

            <br><a href="/">← Voltar ao painel</a>
        </div>
    </body>
    </html>
    """,
        relatorios=relatorios,
    )


@app.route("/")
def home():
    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <title>Ministério Maná</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
            <style>
                .versiculo-container {
                    background-color: #f4f8ff;
                    padding: 40px;
                    margin: 40px auto;
                    border-radius: 16px;
                    max-width: 700px;
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    animation: fadeInUp 1.5s ease;
                }

                .versiculo-container h1 {
                    font-size: 1.8em;
                    color: #2e4a7d;
                    margin-bottom: 20px;
                }

                .versiculo-container p {
                    font-size: 1.4em;
                    font-style: italic;
                    color: #555;
                }

                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            </style>
            <link rel="manifest" href="{{ url_for('static', filename='manifest.json') }}">
<link rel="icon" type="image/png" sizes="192x192" href="{{ url_for('static', filename='icon-192.png') }}">
<meta name="theme-color" content="#2e4a7d">
<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('{{ url_for('static', filename='service-worker.js') }}');
    }
</script>
        </head>
        <body>
            <header>🌾 Ministério Maná - Sistema Interno</header>

            <div class="versiculo-container">
                <h1>🙌 Bem-vindo ao Ministério Maná</h1>
                <p><strong>“E este será o seu nome: O SENHOR está ali.”</strong><br>— Ezequiel 48:35</p>
            </div>

            <div class="container" style="text-align: center;">
                <a href="/login" style="
    display: inline-block;
    padding: 15px 30px;
    font-size: 1.2em;
    font-weight: bold;
    background-color: #2e4a7d;
    color: white;
    border-radius: 10px;
    text-decoration: none;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: background-color 0.3s ease;">
    🔐 Entrar no Sistema
</a>
            </div>

            <footer>✨ “Servi uns aos outros, cada um conforme o dom que recebeu...” – 1 Pedro 4:10</footer>
        </body>
        </html>
        """
    )


USUARIOS_EDITORES = ["renata", "thiago", "aline"]


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username").lower()
        password = request.form.get("password")

        if password == "mana2025":
            session["logado"] = True
            session["usuario"] = username
            session["pode_editar_escala"] = username in USUARIOS_EDITORES
            return redirect(url_for("painel"))
        else:
            error = "Usuário ou senha incorretos."

    return render_template_string(
        """
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
    """,
        error=error,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/painel")
@login_required
def painel():
    return render_template_string(
        """
        <!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Painel - Ministério Maná</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f1f3f5;
            margin: 0;
            padding: 0;
        }
        .painel-container {
            max-width: 600px;
            margin: 60px auto;
            padding: 30px;
            background-color: #fff9e6;
            border-radius: 20px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .painel-header {
            font-size: 1.8em;
            margin-bottom: 10px;
            color: #2e4a7d;
        }
        .painel-sub {
            font-style: italic;
            color: #555;
            margin-bottom: 30px;
        }
        .painel-links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 20px;
        }
        .painel-card {
            padding: 20px;
            border-radius: 16px;
            background-color: #eef2ff;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            font-weight: bold;
            font-size: 1.1em;
            color: #2e4a7d;
            transition: 0.2s;
        }
        .painel-card:hover {
            background-color: #dce4ff;
            transform: scale(1.05);
            cursor: pointer;
        }
        .logout {
            margin-top: 40px;
            display: inline-block;
            padding: 12px 24px;
            background-color: #e74c3c;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            text-decoration: none;
            font-size: 1.1em;
        }
        .logout:hover {
            background-color: #c0392b;
        }
    </style>
</head>
<body>
    <div class="painel-container">
        <div class="painel-header">📋 Painel do Ministério Maná</div>
        <div class="painel-sub">
            "Tudo quanto fizerdes, fazei-o de todo o coração, como ao Senhor, e não aos homens."<br>
            <strong>– Colossenses 3:23</strong>
        </div>

        <div class="painel-links">
            <a href="/escala" class="painel-card">📅<br>Escala</a>
            <a href="/controle" class="painel-card">📦<br>Controle</a>
            <a href="/fotos" class="painel-card">👥<br>Equipe</a>
            <a href="/familias" class="painel-card">👨‍👩‍👧<br>Famílias</a>
            <a href='/historico' class="painel-card">📖 Histórico de Relatórios</a>
        </div>

        <a href="/logout" class="logout">🚪 Sair do Sistema</a>
    </div>
</body>
</html>
    """
    )


# Arquivo de escalas por mês
ESCALAS_FILE = "escalas.json"

# Carrega ou inicializa escalas
if os.path.exists(ESCALAS_FILE):
    with open(ESCALAS_FILE, "r") as f:
        escalas_mensais = json.load(f)
else:
    escalas_mensais = {}


@app.route("/escala", methods=["GET", "POST"])
@login_required
def escala():
    hoje = datetime.now()
    mes_atual = request.args.get("mes") or hoje.strftime("%m")
    ano_atual = request.args.get("ano") or hoje.strftime("%Y")
    chave = f"{mes_atual}-{ano_atual}"

    if chave not in escalas_mensais:
        escalas_mensais[chave] = [{"data": "", "responsaveis": ""} for _ in range(10)]

    if request.method == "POST":
        for i in range(len(escalas_mensais[chave])):
            escalas_mensais[chave][i]["data"] = request.form.get(f"data_{i}", "")
            escalas_mensais[chave][i]["responsaveis"] = request.form.get(
                f"resp_{i}", ""
            )
        with open(ESCALAS_FILE, "w") as f:
            json.dump(escalas_mensais, f)
        return redirect(url_for("escala", mes=mes_atual, ano=ano_atual))

    return render_template_string(
        """
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
                {% if session.get("pode_editar_escala") %}
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
        <button type="submit">💾 Salvar Alterações</button>
    </form>
{% else %}
    <table>
        <tr><th>Data</th><th>Responsáveis</th></tr>
        {% for item in escala %}
        <tr>
            <td>{{ item.data }}</td>
            <td>{{ item.responsaveis }}</td>
        </tr>
        {% endfor %}
    </table>
    <br>
    <p style="color: #d9534f; font-weight: bold; background-color: #ffe6e6; padding: 12px; border-radius: 10px;">
        🔒 Você não tem permissão para editar a escala.<br>Visualização apenas.
    </p>
{% endif %}
                <br>
                <a href="{{ url_for('painel') }}">← Voltar ao Painel</a>
            </div>
        </body>
        </html>
    """,
        escala=escalas_mensais[chave],
        mes=mes_atual,
        ano=ano_atual,
    )


controle_estoque = [
    {"produto": "Arroz (5kg)", "caixa": 43, "prateleira": 0, "vencidos": 1},
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
    {"produto": "Chupeta", "caixa": 0, "prateleira": 1, "vencidos": 0},
]


@app.route("/controle", methods=["GET", "POST"])
@login_required
def controle():
    if request.method == "POST":
        for i in range(len(controle_estoque)):
            controle_estoque[i]["caixa"] = int(request.form.get(f"caixa_{i}", 0))
            controle_estoque[i]["prateleira"] = int(
                request.form.get(f"prateleira_{i}", 0)
            )
            controle_estoque[i]["vencidos"] = int(request.form.get(f"vencidos_{i}", 0))
        return redirect(url_for("controle"))

    return render_template_string(
        """
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
        <tr>
            <th>🛒 Produto</th>
            <th>📦 Caixa<br><span style="font-size: 0.8em; font-weight: normal;">(quantidade nas caixas)</span></th>
            <th>📚 Prateleira<br><span style="font-size: 0.8em; font-weight: normal;">(quantidade à mostra)</span></th>
            <th>⚠️ Vencidos<br><span style="font-size: 0.8em; font-weight: normal;">(expirados ou quase)</span></th>
        </tr>
        {% for i in range(estoque|length) %}
        <tr>
            <td><strong>{{ estoque[i].produto }}</strong></td>
            <td><input type="number" name="caixa_{{ i }}" value="{{ estoque[i].caixa }}" placeholder="Ex: 10"></td>
            <td><input type="number" name="prateleira_{{ i }}" value="{{ estoque[i].prateleira }}" placeholder="Ex: 5"></td>
            <td><input type="number" name="vencidos_{{ i }}" value="{{ estoque[i].vencidos }}" placeholder="Ex: 1"></td>
        </tr>
        {% endfor %}
    </table>
    <br>
    <button type="submit">💾 Salvar Contagem</button>
</form>
                <br>
                <a href="/relatorio_gerado" style="display: inline-block; margin-top: 20px; padding: 12px 20px; background-color: #2e4a7d; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                📝 Gerar Relatório do Dia
                </a>
                <br>
                <a href="{{ url_for('painel') }}">← Voltar ao Painel</a>

                <footer style="margin-top: 40px; background-color: #2e4a7d; color: white; padding: 10px; border-radius: 8px;">
                    💙 “A alma generosa prosperará; quem dá alívio aos outros, alívio receberá.” – Provérbios 11:25
                </footer>
            </div>
        </body>
        </html>
    """,
        estoque=controle_estoque,
    )


cadastro_familias = carregar_familias()


@app.route("/familias", methods=["GET", "POST"])
@login_required
def familias():
    editar_idx = request.args.get("editar", type=int)
    excluir_idx = request.args.get("excluir", type=int)

    if excluir_idx is not None and 0 <= excluir_idx < len(cadastro_familias):
        del cadastro_familias[excluir_idx]
        salvar_familias(cadastro_familias)
        return redirect(url_for("familias"))

    if request.method == "POST":
        nome = request.form.get("nome").strip()
        lider = request.form.get("lider")
        endereco = request.form.get("endereco")
        data = request.form.get("data")

        if editar_idx is not None and 0 <= editar_idx < len(cadastro_familias):
            cadastro_familias[editar_idx]["nome"] = nome
            cadastro_familias[editar_idx]["lider"] = lider
            cadastro_familias[editar_idx]["endereco"] = endereco
            cadastro_familias[editar_idx]["entregas"] = [data]
        else:
            familia_existente = next(
                (f for f in cadastro_familias if f["nome"].lower() == nome.lower()),
                None,
            )
            if familia_existente:
                familia_existente["entregas"].append(data)
            else:
                cadastro_familias.append(
                    {
                        "nome": nome,
                        "lider": lider,
                        "endereco": endereco,
                        "entregas": [data],
                    }
                )

        salvar_familias(cadastro_familias)
        session["mensagem_sucesso"] = "✅ Cadastro salvo com sucesso!"
        return redirect(url_for("familias"))

    familia_para_editar = (
        cadastro_familias[editar_idx]
        if editar_idx is not None and 0 <= editar_idx < len(cadastro_familias)
        else None
    )
    familias_ordenadas = sorted(cadastro_familias, key=lambda f: f["nome"].lower())

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cadastro de Famílias</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
        {% if session.get('mensagem_sucesso') %}
    <div class="alerta-sucesso">{{ session.get('mensagem_sucesso') }}</div>
    {% set _ = session.pop('mensagem_sucesso') %}
{% endif %}
        <div class="container">
            <h2>👨‍👩‍👧 Cadastro de Famílias</h2>
            <form method="post">
    <label>👤 Nome da família ou responsável:</label>
    <input type="text" name="nome" placeholder="Ex: Maria da Silva" required value="{{ familia.nome if familia else '' }}">

    <label>🕊️ Nome do líder de célula:</label>
    <input type="text" name="lider" placeholder="Ex: Irmã Renata" required value="{{ familia.lider if familia else '' }}">

    <label>📍 Endereço ou bairro (célula):</label>
    <input type="text" name="endereco" placeholder="Ex: Jardim Clementino - Célula da Paz" required value="{{ familia.endereco if familia else '' }}">

    <label>📦 Data da entrega da cesta:</label>
    <input type="text" name="data" placeholder="Ex: 19/05/2025" required value="{{ familia.entregas[-1] if familia else '' }}">

    <input type="submit" value="📥 Cadastrar / Atualizar">
</form>

            <h3>Famílias Cadastradas</h3>
<input type="text" id="filtro" placeholder="🔍 Buscar por nome, líder ou bairro..." style="padding: 10px; margin-bottom: 15px; width: 100%; font-size: 1.1em; border-radius: 5px; border: 1px solid #ccc;">

<div id="lista-familias">
    {% for f in familias %}
    <div class="familia-box" style="margin-bottom: 15px;">
        <p>
            <strong>{{ f.nome }}</strong><br>
            Líder: {{ f.lider }}<br>
            Endereço: {{ f.endereco }}<br>
            Entregas: {{ f.entregas | join(', ') }}
        </p>
        <button onclick="location.href='{{ url_for('familias', editar=loop.index0) }}'" class="editar">✏️ Editar</button>
        <button onclick="abrirModal({{ loop.index0 }});" class="excluir">🗑️ Excluir</button>
    </div>
    {% endfor %}
</div>
            <!-- Modal de confirmação -->
<div id="modal-confirmacao" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background-color:rgba(0,0,0,0.6); z-index:9999; justify-content:center; align-items:center;">
    <div style="background:#fff; padding:30px; border-radius:12px; text-align:center; max-width:400px; width:90%; box-shadow:0 4px 15px rgba(0,0,0,0.3);">
        <h3 style="color:#d9534f;">⚠️ Confirmação</h3>
        <p>Você tem certeza que deseja excluir esta família?</p>
        <div style="margin-top: 20px;">
            <button onclick="fecharModal()" style="padding:10px 20px; border:none; border-radius:6px; background:#ccc; margin-right:10px; cursor:pointer;">Cancelar</button>
            <button onclick="confirmarExclusao()" style="padding:10px 20px; border:none; border-radius:6px; background:#d9534f; color:white; cursor:pointer;">Confirmar</button>
        </div>
    </div>
</div>

            <br>
            <a href="/exportar_csv" class="botao-exportar">📥 Exportar CSV</a>
            <br><br>
            <a href="{{ url_for('painel') }}">← Voltar ao Painel</a>
        </div>

        <script>
        document.getElementById('filtro').addEventListener('input', function() {
            const termo = this.value.toLowerCase();
            const itens = document.querySelectorAll('#lista-familias li');
            itens.forEach(item => {
                const texto = item.textContent.toLowerCase();
                item.style.display = texto.includes(termo) ? '' : 'none';
            });
        });
        let idParaExcluir = null;

    function abrirModal(id) {
        idParaExcluir = id;
        document.getElementById("modal-confirmacao").style.display = "flex";
    }

    function fecharModal() {
        document.getElementById("modal-confirmacao").style.display = "none";
        idParaExcluir = null;
    }

    function confirmarExclusao() {
        if (idParaExcluir !== null) {
            window.location.href = `/familias?excluir=${idParaExcluir}`;
        }
    }
        </script>
        </body>
        </html>
    """,
        familias=familias_ordenadas,
        familia=familia_para_editar,
    )


@app.route("/fotos")
@login_required
def fotos():
    imagens = [
        {"arquivo": "equipe1.jpg", "descricao": "Workshop da Assistência Social"},
        {"arquivo": "equipe2.jpg", "descricao": "Organização do estoque no Maná"},
        {"arquivo": "equipe3.jpg", "descricao": "Confraternização do Maná"},
    ]
    return render_template_string(
        """
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

                <br><a href="{{ url_for('painel') }}">← Voltar ao Painel</a>

                <footer style="margin-top: 40px; background-color: #2e4a7d; color: white; padding: 10px; border-radius: 8px;">
                    ✝️ “Onde há unidade, ali o Senhor ordena a bênção.” – Salmos 133:3
                </footer>
            </div>
        </body>
        </html>
    """,
        imagens=imagens,
    )


@app.route("/exportar_csv")
@login_required
def exportar_csv():
    import csv
    from flask import make_response

    si = []
    si.append(["Nome", "Líder", "Endereço", "Entregas"])

    for f in cadastro_familias:
        si.append(
            [f["nome"], f["lider"], f["endereco"], ", ".join(f.get("entregas", []))]
        )

    response = make_response()
    response.headers["Content-Disposition"] = (
        "attachment; filename=familias_exportadas.csv"
    )
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.data = "\ufeff" + "\n".join([",".join(map(str, linha)) for linha in si])
    return response


@app.route("/excluir_familia/<int:idx>")
@login_required
def excluir_familia(idx):
    if 0 <= idx < len(cadastro_familias):
        del cadastro_familias[idx]
        salvar_familias(cadastro_familias)
    return redirect(url_for("familias"))


@app.route("/relatorio_gerado", methods=["GET", "POST"])
@login_required
def relatorio_gerado():
    hoje = datetime.now().strftime("%d/%m/%Y")
    periodo = "Manhã"
    responsaveis = session.get("usuario", "Desconhecido")

    # Geração automática do relatório baseado no controle
    relatorio_gerado = f"""
📆 {periodo} - {hoje}
Alistados: {responsaveis}

🔜 Alimentos com Vencimento em JUNHO de 2025

🔜 Alimentos com Vencimento a partir JULHO de 2025
"""

    for item in controle_estoque:
        total = item["caixa"] + item["prateleira"]
        if total > 0:
            relatorio_gerado += f"- {str(total).zfill(2)} {item['produto']}\n"

    relatorio_gerado += """
\n🔜 Kits de Limpeza e Higiene

🔺 Cestas Completas

✅ Relatório: \n
Recebidos:

Realizado:

Doações:

🚨 ITENS EM FALTA

Solicitação para próxima escala

📖 Compartilhamento da palavra:
"""

    # Se o formulário for submetido
    if request.method == "POST":
        relatorio_customizado = request.form.get("relatorio")
        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Relatório Editado</title>
                <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
            </head>
            <body>
            <div class="container">
                <h2>📋 Relatório Atualizado</h2>
                <textarea readonly style="width: 100%; height: 500px;">{{ relatorio }}</textarea>
                <br><br>
                <a href="/controle">← Voltar para o Controle</a>
            </div>
            </body>
            </html>
            """,
            relatorio=relatorio_customizado,
        )

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Editar Relatório</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
            <style>
                textarea {
                    font-family: monospace;
                    font-size: 1.1em;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid #ccc;
                    width: 100%;
                    height: 500px;
                    box-sizing: border-box;
                }
                button {
                    background-color: #2e4a7d;
                    color: white;
                    padding: 12px 20px;
                    border: none;
                    border-radius: 8px;
                    font-size: 1.1em;
                    cursor: pointer;
                }
            </style>
            <script>
                function copiarRelatorio() {
                    const textarea = document.querySelector("textarea");
                    textarea.select();
                    document.execCommand("copy");
                    alert("📋 Relatório copiado com sucesso!");
                }
            </script>
        </head>
        <body>
        <div class="container">
            <h2>📋 Relatório Gerado Automaticamente</h2>
            <form method="post" action="/salvar_relatorio">
    <input type="hidden" name="data" value="{{ data }}">
    <input type="hidden" name="periodo" value="{{ periodo }}">
    <input type="hidden" name="responsaveis" value="{{ responsaveis }}">
    <textarea name="relatorio">{{ relatorio }}</textarea>
                <br><br>
                <button type="submit">💾 Salvar Alterações</button>
                <button type="button" onclick="copiarRelatorio()">📋 Copiar Relatório</button>
            </form>
            <br><br>
            <a href="/controle">← Voltar para o Controle</a>
        </div>
        </body>
        </html>
        """,
        relatorio=relatorio_gerado,
    )


# Rota para exibir histórico de relatórios
@app.route("/historico", methods=["GET"])
@login_required
def historico_relatorios():
    mes = request.args.get("mes") or datetime.now().strftime("%m")
    ano = request.args.get("ano") or datetime.now().strftime("%Y")

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT data, periodo, responsaveis, conteudo FROM relatorios
            WHERE LENGTH(data) >= 10
              AND SUBSTRING(data FROM 4 FOR 2) = %s
              AND SUBSTRING(data FROM 7 FOR 4) = %s
            ORDER BY criado_em DESC
            """,
            (mes.zfill(2), ano),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        return f"<h1>Erro no filtro:</h1><pre>{str(e)}</pre>"

    relatorios = []
    for row in rows:
        relatorios.append(
            {
                "data": row[0],
                "periodo": row[1],
                "responsaveis": row[2],
                "conteudo": row[3],
            }
        )

    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <title>Histórico de Relatórios</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <div class="container">
                <h1>📚 Histórico de Relatórios</h1>
                <form method="get" style="margin-bottom: 20px;">
                    <label for="mes">📅 Mês:</label>
                    <select name="mes" id="mes">
                        {% for i in range(1, 13) %}
                            <option value="{{'%02d' % i}}" {% if mes == '%02d' % i %}selected{% endif %}>{{'%02d' % i}}</option>
                        {% endfor %}
                    </select>

                    <label for="ano">🗓️ Ano:</label>
                    <select name="ano" id="ano">
                        {% for a in range(2024, 2031) %}
                            <option value="{{a}}" {% if ano == a|string %}selected{% endif %}>{{a}}</option>
                        {% endfor %}
                    </select>

                    <button type="submit">🔍 Filtrar</button>
                </form>

                {% if relatorios %}
                    {% for rel in relatorios %}
                        <div style="border:1px solid #ccc; border-radius:10px; padding:20px; margin-bottom:20px; background:#f9f9f9;">
                            <h3>{{ rel.data }} - {{ rel.periodo }} | Responsáveis: {{ rel.responsaveis }}</h3>
                            <pre style="white-space: pre-wrap; font-family: inherit;">{{ rel.conteudo }}</pre>
                        </div>
                    {% endfor %}
                {% else %}
                    <p>Nenhum relatório registrado ainda.</p>
                {% endif %}

                <br>
                <a href="/painel">← Voltar para o Painel</a>
            </div>
        </body>
        </html>
        """,
        relatorios=relatorios,
        mes=mes,
        ano=ano,
        datetime=datetime,
    )


@app.route("/salvar_relatorio", methods=["POST"])
@login_required
def salvar_relatorio():
    data = request.form.get("data")
    periodo = request.form.get("periodo")
    responsaveis = request.form.get("responsaveis")
    conteudo = request.form.get("relatorio")

    print("Conteúdo recebido:", conteudo)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO relatorios (data, periodo, responsaveis, conteudo) VALUES (%s, %s, %s, %s)",
        (data, periodo, responsaveis, conteudo),
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect("/historico")


def criar_tabela_relatorios():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS relatorios")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS relatorios (
            id SERIAL PRIMARY KEY,
            data TEXT,
            periodo TEXT,
            responsaveis TEXT,
            vencimento_junho TEXT,
            vencimento_julho TEXT,
            higiene TEXT,
            cestas TEXT,
            conteudo TEXT,
            realizado TEXT,
            doacoes TEXT,
            faltando TEXT,
            solicitacoes TEXT,
            palavra TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    )
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    criar_tabela_familias()
    criar_tabela_relatorios()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

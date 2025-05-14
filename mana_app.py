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

load_dotenv()


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


@app.route("/")
def home():
    return render_template_string(
        """
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
    """
    )


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
                .painel-container {
                    max-width: 800px;
                    margin: auto;
                    padding: 30px;
                    background-color: #fff9e6;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    text-align: center;
                }
                .painel-header {
                    font-size: 1.6em;
                    margin-bottom: 10px;
                    color: #2e4a7d;
                }
                .painel-sub {
                    font-style: italic;
                    color: #666;
                    margin-bottom: 30px;
                }
                .painel-links {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .painel-card {
                    padding: 20px;
                    border-radius: 10px;
                    background-color: #f0f2ff;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                    font-weight: bold;
                    font-size: 1.1em;
                    color: #2e4a7d;
                    transition: 0.2s;
                }
                .painel-card:hover {
                    background-color: #e3e8ff;
                    transform: scale(1.02);
                    cursor: pointer;
                }
                .logout {
                    margin-top: 30px;
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 6px;
                    font-weight: bold;
                    text-decoration: none;
                }
                .logout:hover {
                    background-color: #c0392b;
                }
            </style>
        </head>
        <body>
            <div class="painel-container">
                <div class="painel-header">📋 Painel do Ministério Maná</div>
                <div class="painel-sub">"Tudo quanto fizerdes, fazei-o de todo o coração, como ao Senhor, e não aos homens." – Colossenses 3:23</div>

                <div class="painel-links">
                    <a href='/escala' class="painel-card">📅 Escala</a>
                    <a href='/controle' class="painel-card">📦 Controle</a>
                    <a href='/fotos' class="painel-card">👥 Fotos da Equipe</a>
                    <a href='/familias' class="painel-card">👨‍👩‍👧 Cadastro de Famílias</a>
                </div>

                <a href='/logout' class="logout">🚪 Sair do Sistema</a>
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
    """,
        escala=escalas_mensais[chave],
        mes=mes_atual,
        ano=ano_atual,
    )


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
        <div class="container">
            <h2>👨‍👩‍👧 Cadastro de Famílias</h2>
            <form method="post">
                <label>Nome da família ou responsável:</label>
                <input type="text" name="nome" required value="{{ familia.nome if familia else '' }}">
                <label>Nome do líder de célula:</label>
                <input type="text" name="lider" required value="{{ familia.lider if familia else '' }}">
                <label>Endereço ou bairro (célula):</label>
                <input type="text" name="endereco" required value="{{ familia.endereco if familia else '' }}">
                <label>Data da entrega da cesta:</label>
                <input type="text" name="data" required value="{{ familia.entregas[-1] if familia else '' }}">
                <input type="submit" value="Cadastrar/Atualizar">
            </form>

            <h3>Famílias Cadastradas</h3>
            <input type="text" id="filtro" placeholder="🔍 Buscar por nome, líder ou bairro..." style="padding: 10px; margin-bottom: 15px; width: 100%; font-size: 1.1em; border-radius: 5px; border: 1px solid #ccc;">

            <ul id="lista-familias">
                {% for f in familias %}
                <li>
                    <strong>{{ f.nome }}</strong> | Líder: {{ f.lider }} | {{ f.endereco }} | Entregas: {{ f.entregas | join(', ') }}
                    <a href="{{ url_for('familias', editar=loop.index0) }}">✏️ Editar</a> |
                    <a href="#" onclick="abrirModal({{ loop.index0 }}); return false;">🗑️ Excluir</a>
                </li>
                {% endfor %}
            </ul>
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
            <a href="/">← Voltar</a>
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

                <br><a href="/">← Voltar</a>

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


if __name__ == "__main__":
    criar_tabela_familias()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

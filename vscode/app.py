from flask import Flask, render_template, request, redirect, session, jsonify
import bcrypt
from config import conectar

app = Flask(__name__)
app.secret_key = "segredo"

# ================== CADASTRO ==================

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        # criptografar senha
        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

        db = conectar()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        if cursor.fetchone():
            db.close()
            return render_template("cadastro.html", mensagem="Email já cadastrado!")

        try:
            cursor.execute("""
                INSERT INTO usuarios (name, email, senha)
                VALUES (%s,%s,%s)
            """, (nome, email, senha_hash.decode()))
            db.commit()

            mensagem = "Usuário cadastrado com sucesso!"

        except:
            mensagem = "Erro ao cadastrar usuário!"

        finally:
            db.close()

        return render_template("cadastro.html", mensagem=mensagem)
        
    return render_template("cadastro.html")

# ================== LOGIN ==================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        db = conectar()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        usuario = cursor.fetchone()
        db.close()
        if not usuario:
            return render_template("login.html", mensagem="Usuário não encontrado!")


        if usuario and bcrypt.checkpw(
            senha.encode(),
            usuario["senha"].encode()
        ):
            session["usuario_id"] = usuario["id"]
            return render_template("home.html", mensagem="Login realizado com sucesso!")


        return render_template("login.html", mensagem="Email ou senha inválidos!")

    return render_template('login.html')

# ================== HOME TESTE ==================

@app.route("/")
def home():
    if "usuario_id" not in session:
        return redirect("/login")

    busca = request.args.get("busca", "")
    status = request.args.get("status", "")

    db = conectar()
    cursor = db.cursor(dictionary=True)

    sql = "SELECT * FROM livros WHERE usuario_id = %s"
    valores = [session["usuario_id"]]

    if busca:
        sql += " AND (titulo LIKE %s OR autor LIKE %s)"
        termo = f"%{busca}%"
        valores.append(termo)
        valores.append(termo)

    if status:
        sql += " AND status = %s"
        valores.append(status)

    cursor.execute(sql, tuple(valores))
    livros = cursor.fetchall()
    db.close()

    return render_template("home.html", livros=livros, busca=busca)

# ================== LOGOUT ==================

@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)


# ================== CADASTRO LIVRO ==================

@app.route("/cadastro_livro", methods=["GET", "POST"])
def cadastro_livro():
    if "usuario_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        titulo = request.form["titulo"]
        autor = request.form["autor"]
        status = request.form["status"]
        imagem = request.form["imagem"]
        estrelas = request.form["estrelas"]
        resenha = request.form["resenha"]

        db = conectar()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO livros (usuario_id, titulo, autor, status, imagem, estrelas, resenha)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session["usuario_id"],
            titulo,
            autor,
            status,
            imagem,
            estrelas,
            resenha
        ))

        db.commit()
        db.close()

        return redirect("/")

    return render_template("cadastro_livro.html")

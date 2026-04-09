from flask import Flask, render_template, request, redirect, session
import bcrypt
from config import conectar

app = Flask(__name__)
app.secret_key = "segredo"


# ================== CADASTRO DE USUÁRIO ==================

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        senha = request.form["senha"]

        if not nome or not email or not senha:
            return render_template("cadastro.html", mensagem="Preencha todos os campos.")

        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

        db = conectar()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            db.close()
            return render_template("cadastro.html", mensagem="Email já cadastrado!")

        try:
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha)
                VALUES (%s, %s, %s)
            """, (nome, email, senha_hash.decode()))
            db.commit()
            mensagem = "Usuário cadastrado com sucesso!"
        except Exception as e:
            print("Erro no cadastro:", e)
            mensagem = "Erro ao cadastrar usuário!"
        finally:
            db.close()

        return render_template("cadastro.html", mensagem=mensagem)

    return render_template("cadastro.html")


# ================== LOGIN ==================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        senha = request.form["senha"]

        db = conectar()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        db.close()

        if not usuario:
            return render_template("login.html", mensagem="Usuário não encontrado!")

        if bcrypt.checkpw(senha.encode(), usuario["senha"].encode()):
            session["usuario_id"] = usuario["id"]
            return redirect("/")

        return render_template("login.html", mensagem="Email ou senha inválidos!")

    return render_template("login.html")


# ================== HOME ==================

@app.route("/")
def home():
    if "usuario_id" not in session:
        return redirect("/login")

    busca = request.args.get("busca", "").strip()
    status = request.args.get("status", "").strip()

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

    sql += " ORDER BY id DESC"

    cursor.execute(sql, tuple(valores))
    livros = cursor.fetchall()
    db.close()

    return render_template("home.html", livros=livros, busca=busca)


# ================== CADASTRO DE LIVRO ==================

@app.route("/cadastro_livro", methods=["GET", "POST"])
def cadastro_livro():
    if "usuario_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        autor = request.form["autor"].strip()
        status = request.form["status"].strip()
        imagem = request.form["imagem"].strip()
        estrelas = request.form["estrelas"]
        resenha = request.form["resenha"].strip()

        if not titulo or not autor or not status:
            return render_template("cadastro_livro.html", mensagem="Preencha os campos obrigatórios.")

        db = conectar()
        cursor = db.cursor()

        try:
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
        except Exception as e:
            print("Erro ao cadastrar livro:", e)
            db.close()
            return render_template("cadastro_livro.html", mensagem="Erro ao cadastrar livro.")

        db.close()
        return redirect("/")

    return render_template("cadastro_livro.html")


# ================== DETALHES DO LIVRO ==================

@app.route("/livro/<int:id>", methods=["GET", "POST"])
def detalhe_livro(id):
    if "usuario_id" not in session:
        return redirect("/login")

    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM livros WHERE id = %s AND usuario_id = %s",
        (id, session["usuario_id"])
    )
    livro = cursor.fetchone()

    if not livro:
        db.close()
        return "Livro não encontrado ou sem permissão."

    if request.method == "POST":
        estrelas = request.form["estrelas"]

        try:
            cursor = db.cursor()
            cursor.execute(
                "UPDATE livros SET estrelas = %s WHERE id = %s AND usuario_id = %s",
                (estrelas, id, session["usuario_id"])
            )
            db.commit()
        except Exception as e:
            print("Erro ao atualizar estrelas:", e)

        db.close()
        return redirect(f"/livro/{id}")

    db.close()
    return render_template("detalhe_livro.html", livro=livro)


# ================== EDITAR LIVRO ==================

@app.route("/editar_livro/<int:id>", methods=["GET", "POST"])
def editar_livro(id):
    if "usuario_id" not in session:
        return redirect("/login")

    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM livros WHERE id = %s AND usuario_id = %s",
        (id, session["usuario_id"])
    )
    livro = cursor.fetchone()

    if not livro:
        db.close()
        return "Livro não encontrado ou sem permissão."

    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        autor = request.form["autor"].strip()
        status = request.form["status"].strip()
        imagem = request.form["imagem"].strip()
        estrelas = request.form["estrelas"]
        resenha = request.form["resenha"].strip()

        if not titulo or not autor or not status:
            db.close()
            return render_template("editar_livro.html", livro=livro, mensagem="Preencha os campos obrigatórios.")

        try:
            cursor = db.cursor()
            cursor.execute("""
                UPDATE livros
                SET titulo = %s,
                    autor = %s,
                    status = %s,
                    imagem = %s,
                    estrelas = %s,
                    resenha = %s
                WHERE id = %s AND usuario_id = %s
            """, (
                titulo,
                autor,
                status,
                imagem,
                estrelas,
                resenha,
                id,
                session["usuario_id"]
            ))
            db.commit()
        except Exception as e:
            print("Erro ao editar livro:", e)
            db.close()
            return render_template("editar_livro.html", livro=livro, mensagem="Erro ao editar livro.")

        db.close()
        return redirect(f"/livro/{id}")

    db.close()
    return render_template("editar_livro.html", livro=livro)


# ================== EXCLUIR LIVRO ==================

@app.route("/excluir_livro/<int:id>", methods=["POST"])
def excluir_livro(id):
    if "usuario_id" not in session:
        return redirect("/login")

    db = conectar()
    cursor = db.cursor()

    try:
        cursor.execute(
            "DELETE FROM livros WHERE id = %s AND usuario_id = %s",
            (id, session["usuario_id"])
        )
        db.commit()
    except Exception as e:
        print("Erro ao excluir livro:", e)

    db.close()
    return redirect("/")


# ================== LOGOUT ==================

@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
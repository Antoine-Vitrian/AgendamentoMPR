import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = "segredo" 

def criarDB():
    connectSQL = sqlite3.connect("mpr.db")
    cursor = connectSQL.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            tipo TEXT NOT NULL,
            empresa TEXT NOT NULL,
            transportadora TEXT NOT NULL,
            placa TEXT NOT NULL,
            cavalo TEXT NOT NULL,
            nome_motorista TEXT NOT NULL,
            rg_motorista TEXT NOT NULL,
            nota_fiscal TEXT NOT NULL,
            data TEXT NOT NULL   
        )
    """)

def contar_carros_por_data(data_str):
    conn = sqlite3.connect("mpr.db")
    cur = conn.cursor()
    # FRaz o select com a soma de certa data
    cur.execute("SELECT COUNT(*) FROM agendamento WHERE data = ?", (data_str,))
    # Retorna uma linha do resultado da consulta
    # Ou seja, o único valor que é o número de carros naquele dia
    total = cur.fetchone()[0]
    conn.close()
    return total

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":
        data_str = request.form.get("data", "").strip()
        if not data_str:
            flash("Data não informada. Escolha uma data antes de enviar.")
            return redirect(url_for("formulario"))

        try:
            data_obj = datetime.strptime(data_str, "%Y-%m-%d")
        except ValueError:
            flash("Formato de data inválido.")
            return redirect(url_for("formulario"))

        dia_semana = data_obj.weekday()  # 0=segunda ... 6=domingo

        # regra de limite
        limite = 15 if dia_semana < 5 else 6  # segunda a sexta = 15, sábado = 6
        total = contar_carros_por_data(data_str)

        if dia_semana == 6:
            flash("Domingos não são permitidos. Escolha outra data.")
            return redirect(url_for("formulario"))

        if data_obj.date() < datetime.today().date():
            flash("Não é permitido escolher datas passadas.")
            return redirect(url_for("formulario"))

        if total >= limite and request.form.get("forcar") != "true":
            flash(f"Limite de {limite} carros já atingido para esta data. Deseja continuar mesmo assim?")
            return render_template("form.html", limite_atingido=True, dados=request.form)



        # se passou nas validações, salvar no banco
        dados = (
            request.form["email"],
            request.form["tipo"],
            request.form["empresa"],
            request.form["transportadora"],
            request.form["placa"],
            request.form["cavalo"],
            request.form["nome_motorista"],
            request.form["rg_motorista"],
            request.form["nota_fiscal"],
            data_str,
        )
        conn = sqlite3.connect("mpr.db")
        cur = conn.cursor()
        cur.execute("""INSERT INTO agendamento 
            (email, tipo, empresa, transportadora, placa, cavalo, nome_motorista, rg_motorista, nota_fiscal, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", dados)
        conn.commit()
        conn.close()
        flash("Cadastro realizado com sucesso!")
        return redirect(url_for("formulario"))

    return render_template("form.html", limite_atingido=False, dados={})

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = sqlite3.connect("mpr.db")
    cur = conn.cursor()

    if request.method == "POST":
        dados = (
            request.form["email"],
            request.form["tipo"],
            request.form["empresa"],
            request.form["transportadora"],
            request.form["placa"],
            request.form["cavalo"],
            request.form["nome_motorista"],
            request.form["rg_motorista"],
            request.form["nota_fiscal"],
            request.form["data"],
            id,
        )
        cur.execute("""UPDATE agendamento SET 
            email=?, tipo=?, empresa=?, transportadora=?, placa=?, cavalo=?, 
            nome_motorista=?, rg_motorista=?, nota_fiscal=?, data=? 
            WHERE id=?""", dados)
        conn.commit()
        conn.close()
        flash("Agendamento atualizado com sucesso!")
        return redirect(url_for("visualizar"))

    cur.execute("SELECT * FROM agendamento WHERE id=?", (id,))
    registro = cur.fetchone()
    conn.close()
    return render_template("editar.html", registro=registro)

@app.route("/deletar/<int:id>", methods=["POST"])
def deletar(id):
    conn = sqlite3.connect("mpr.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM agendamento WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Agendamento deletado com sucesso!")
    return redirect(url_for("visualizar"))

@app.route("/visualizar", methods=["GET", "POST"])
def visualizar():
    conn = sqlite3.connect("mpr.db")
    cur = conn.cursor()
    data_filtro = request.form.get("data_filtro")  # pega a data do formulário

    if data_filtro:
        cur.execute("SELECT * FROM agendamento WHERE data = ?", (data_filtro,))
    else:
        cur.execute("SELECT * FROM agendamento")

    registros = cur.fetchall()
    conn.close()

    # Converter a coluna de data (última posição reg[10]) para dd/mm/aaaa
    registros_formatados = []
    for reg in registros:
        reg = list(reg)
        try:
            reg[10] = datetime.strptime(reg[10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            pass  # se não conseguir converter, mantém como está
        registros_formatados.append(reg)

    # Também converter o valor do filtro, se existir
    if data_filtro:
        try:
            data_filtro = datetime.strptime(data_filtro, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            pass

    return render_template("visualizar.html", registros=registros_formatados, data_filtro=data_filtro)

if __name__ == "__main__":
    criarDB()
    app.run(debug=True)
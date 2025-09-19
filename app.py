from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
app.secret_key = "chave_super_secreta"
socketio = SocketIO(app, cors_allowed_origins="*")

def init_db():
    con = sqlite3.connect("signals.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user TEXT,
        password TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY,
        ativo TEXT,
        direcao TEXT,
        horario TEXT
    )""")
    cur.execute("INSERT OR IGNORE INTO users (id,user,password) VALUES (1,'admin','1234')")
    con.commit()
    con.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]
        con = sqlite3.connect("signals.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE user=? AND password=?", (user, password))
        if cur.fetchone():
            session["user"] = user
            return redirect("/painel")
    return render_template("login.html")

@app.route("/painel")
def painel():
    if "user" not in session:
        return redirect("/")
    return render_template("painel.html")

@app.route("/add_signal", methods=["POST"])
def add_signal():
    data = request.form
    ativo, direcao, horario = data["ativo"], data["direcao"], data["horario"]
    con = sqlite3.connect("signals.db")
    cur = con.cursor()
    cur.execute("INSERT INTO signals (ativo, direcao, horario) VALUES (?, ?, ?)", (ativo, direcao, horario))
    con.commit()
    con.close()
    socketio.emit("novo_sinal", {"ativo": ativo, "direcao": direcao, "horario": horario}, broadcast=True)
    return "ok"

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

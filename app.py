from flask import Flask, render_template, request, redirect, url_for
import csv
from datetime import datetime

import os
from werkzeug.utils import secure_filename
from datetime import datetime

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpeg', "jpg"}


# Cria a aplicação Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define a rota principal, que irá renderizar o index.html
@app.get("/")
def index():
    books = []
    with open('books.csv', mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            books.append(row)
    
    return render_template("index.html", books=books)

@app.get("/book/<int:book_id>")
def book_details(book_id):
    found_book = None

    with open('books.csv', mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for book in csv_reader:
            # Compara o ID da linha (convertido para int) com o ID da URL
            if int(book['id']) == book_id:
                found_book = book
                break # Encontramos o filme, podemos parar o loop
    
    # Se um filme foi encontrado, renderiza a página de detalhes com seus dados
    if found_book:
        return render_template("details-codigodavince.html", book=found_book)


    # Se não, retorna uma página de erro 404
    else:
        return "book not found!", 404

@app.get("/add-review")
def show_add_form():
    return render_template("add-review.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/add-review', methods=['POST'], endpoint='add-review') #corrigir bug do endpoint
def add_review():

    # 1. Busca o último ID adicionado (código que vimos acima)
    with open("books.csv", mode="r", encoding="utf-8") as csv_file:
        reader = list(csv.reader(csv_file))
        last_id = 0

        if len(reader) > 1:
            last_row = reader[-1]
            if last_row:
                last_id = int(last_row[0])

        next_id = last_id + 1

    # 2. Converte a data para o formato esperado
    watched_date_raw = request.form.get("date")
    date_object = datetime.strptime(watched_date_raw, "%Y-%m-%d")

    formatted_date = date_object.strftime("%m/%d/%Y")

    # --- LÓGICA DE UPLOAD DA IMAGEM ---

    # 1. Acessa o arquivo enviado
    poster_file = request.files.get('poster')
    
    # Variável para guardar o caminho do arquivo
    poster_path = None

    # 2. Valida e Salva o Arquivo
    if poster_file and allowed_file(poster_file.filename):

        # 3. Garante um nome de arquivo seguro
        original_filename = secure_filename(poster_file.filename)

        # Cria um nome único para evitar sobreposição de arquivos
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{original_filename}"
        
        # 4. Salva o arquivo na pasta de uploads
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        poster_file.save(filepath)
        
        # 5. Guardamos o caminho relativo para salvar no CSV
        poster_path = f"uploads/{unique_filename}"

    else:
        return "Invalid file format. Only PNG and JPEG images are allowed.", 400

    # 3. Coleta os dados do formulário usando o atributo 'name' de cada campo
    new_book_data = [
        next_id,
        request.form.get("name"),
        poster_path,
        request.form.get("ranking"),
        formatted_date,
        request.form.get("review"),
    ]

    # 3. Anexa os novos dados ao arquivo CSV
    with open("books.csv", mode="a", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(new_book_data)

    # 4. Redireciona para a página principal
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

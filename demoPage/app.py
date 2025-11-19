from flask import Flask, render_template, request, redirect, url_for
import json
import os
from recommender import get_recommendations # Importaremos esto luego

app = Flask(__name__)

# Función auxiliar para cargar datos
def load_data():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    data = load_data()
    books = data['books']
    
    # Simulación: Usuario logueado (hardcodeado para la demo)
    user_history = [101] 
    
    # Obtener recomendaciones basadas en el último libro leído
    recommended_books = get_recommendations(user_history, books)
    
    # Agrupar por categorías para el diseño tipo Netflix
    scifi_books = [b for b in books if "Ciencia Ficción" in b['genre']]
    classic_books = [b for b in books if "Clásico" in b['genre']]
    
    return render_template('index.html', 
                           rec_books=recommended_books, 
                           scifi=scifi_books, 
                           classics=classic_books)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    data = load_data()
    # Buscar el libro por ID (manera sencilla)
    book = next((item for item in data['books'] if item["id"] == book_id), None)
    return render_template('book_detail.html', book=book)

if __name__ == '__main__':
    app.run(debug=True)
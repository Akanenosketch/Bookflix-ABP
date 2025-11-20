from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Pequeña lista de "stop words" en español para limpiar el análisis
# (Palabras que se repiten mucho y no aportan significado)
SPANISH_STOP_WORDS = [
    'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para', 
    'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'mas', 'pero', 'sus', 'le', 'ya', 'o', 
    'este', 'si', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'ser'
]

def get_recommendations(all_books, user_history_ids=None, search_query=None):
    """
    Calcula la probabilidad de lectura basada en similitud de contenido (NLP).
    Puede basarse en el historial de lectura O en una búsqueda específica.
    """
    
    # 1. Preparar los datos (DataFrame)
    df = pd.DataFrame(all_books)
    
    # Evitar errores si la base de datos está vacía
    if df.empty:
        return []

    # 2. CREACIÓN DE LA "SOPA" (El contenido a analizar)
    # Unimos Título + Género + Descripción para tener más texto que analizar
    # Asumimos que en tu JSON cada libro tiene campo 'description' y 'genre'
    df['soup'] = df.apply(lambda x: f"{x['title']} {' '.join(x['genre'])} {x.get('description', '')}", axis=1)
    
    # 3. Vectorización (Convertir palabras a números usando TF-IDF)
    tfidf = TfidfVectorizer(stop_words=SPANISH_STOP_WORDS)
    try:
        tfidf_matrix = tfidf.fit_transform(df['soup'])
    except ValueError:
        # Si no hay suficiente texto, devolvemos lista vacía o populares
        return all_books[:5]

    # 4. Definir el "Perfil de Interés" (El vector contra el que comparamos)
    user_profile_vector = None
    
    if search_query:
        # CASO A: El usuario escribió algo en el buscador
        # "Quiero libros de dragones y fuego"
        user_profile_vector = tfidf.transform([search_query])
        
    elif user_history_ids:
        # CASO B: Basado en historial
        # Cogemos todos los libros que ha leído y creamos un "Super Libro" con sus descripciones
        read_books = df[df['id'].isin(user_history_ids)]
        if not read_books.empty:
            # Unimos todo el texto de los libros leídos
            user_history_text = " ".join(read_books['soup'].tolist())
            user_profile_vector = tfidf.transform([user_history_text])
    
    # Si no tenemos info (usuario nuevo sin búsqueda), devolvemos vacíos o populares
    if user_profile_vector is None:
        return all_books[:10]

    # 5. CÁLCULO DE PROBABILIDAD (Similitud del Coseno)
    # Comparamos el vector del usuario contra TODOS los libros
    cosine_sim = cosine_similarity(user_profile_vector, tfidf_matrix)
    
    # Obtener puntuaciones: [(index_libro_0, score), (index_libro_1, score)...]
    scores = list(enumerate(cosine_sim[0]))
    
    # Ordenar de mayor a menor probabilidad
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    
    recommendations = []
    for idx, score in scores:
        book = all_books[idx]
        
        # Filtro: No recomendar lo que ya ha leído (solo si no es una búsqueda explícita)
        if user_history_ids and not search_query:
            if book['id'] in user_history_ids:
                continue
        
        # Convertir score (0.0 a 1.0) a Porcentaje (0% a 100%)
        probability = round(score * 100, 1)
        
        # Solo recomendamos si hay una mínima conexión (> 5%)
        if probability > 5:
            # Inyectamos el dato 'match' en el objeto libro para mostrarlo en el HTML
            book['match_percentage'] = probability 
            recommendations.append(book)
            
    return recommendations[:10]
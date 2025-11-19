def get_recommendations(user_history_ids, all_books):
    """
    Sistema simple que recomienda libros basados en coincidencias de género
    con los libros que el usuario ya ha leído.
    """
    if not user_history_ids:
        return all_books[:5] # Si es nuevo, devolver los primeros 5 por defecto

    # 1. Obtener los géneros que le gustan al usuario
    liked_genres = set()
    for b in all_books:
        if b['id'] in user_history_ids:
            for g in b['genre']:
                liked_genres.add(g)
    
    # 2. Buscar libros que no haya leído pero que tengan esos géneros
    recommendations = []
    for b in all_books:
        if b['id'] not in user_history_ids:
            # Intersección: si el libro tiene géneros en común con los gustos
            book_genres = set(b['genre'])
            if not book_genres.isdisjoint(liked_genres):
                recommendations.append(b)
                
    return recommendations[:10] # Devolver top 10
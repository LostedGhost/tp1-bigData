import streamlit as st

# Titre de l'application
st.title("Système de Recommandation : Filtrage Collaboratif (Item-Item Top-N)")
st.sidebar.title("RS-CF-APP")
# Étape 1 : Chargement des données
st.header("1. Chargement des données")
data_option = st.radio("Choisissez la méthode de chargement des données :", ["Manuelle", "Fichier CSV"])

# Initialisation des données
data = {}
if data_option == "Manuelle":
    # Entrée manuelle des données
    st.write("Entrez les données manuellement :")
    rows = st.number_input("Nombre d'utilisateurs", min_value=1, value=3)
    cols = st.number_input("Nombre de films", min_value=1, value=3)
    
    users = [f"Utilisateur {i+1}" for i in range(rows)]
    movies = [f"Film {j+1}" for j in range(cols)]
    
    for user in users:
        data[user] = {}
        for movie in movies:
            value = st.number_input(f"Note pour {user}, {movie} (-1 pour valeur manquante)", min_value=-1, max_value=5, value=-1)
            data[user][movie] = value if value != -1 else None
else:
    # Chargement depuis un fichier CSV
    uploaded_file = st.file_uploader("Téléchargez un fichier CSV contenant les notes", type=["csv"])
    if uploaded_file is not None:
        lines = uploaded_file.readlines()
        movies = lines[0].decode("utf-8").strip().split(",")[1:]  # Première ligne = noms des films
        users = []
        for line in lines[1:]:
            parts = line.decode("utf-8").strip().split(",")
            user = parts[0]
            users.append(user)
            data[user] = {}
            for i, rating in enumerate(parts[1:]):
                data[user][movies[i]] = int(rating) if rating.strip() and int(rating) != -1 else None

# Affichage de la matrice des notes
if data:
    st.write("Matrice des notes :")
    display_data = {user: {movie: rating if rating is not None else "Non évalué" for movie, rating in user_ratings.items()} for user, user_ratings in data.items()}
    st.table(display_data)

# Étape 2 : Calcul de la matrice des similarités (Pearson)
st.header("2. Matrice des similarités entre les films")
if data:
    # Calcul de la similarité de Pearson entre les films
    def pearson_similarity(vec1, vec2):
        # Filtrer les valeurs non nulles communes
        common_ratings = [(a, b) for a, b in zip(vec1, vec2) if a is not None and b is not None]
        if len(common_ratings) == 0:
            return 0  # Pas de similarité si aucun utilisateur commun
        
        # Extraire les notes communes
        ratings1, ratings2 = zip(*common_ratings)
        
        # Calculer les moyennes
        mean1 = sum(ratings1) / len(ratings1)
        mean2 = sum(ratings2) / len(ratings2)
        
        # Calculer la covariance et les écarts-types
        covariance = sum((a - mean1) * (b - mean2) for a, b in common_ratings)
        std1 = (sum((a - mean1) ** 2 for a, _ in common_ratings)) ** 0.5
        std2 = (sum((b - mean2) ** 2 for _, b in common_ratings)) ** 0.5
        
        # Retourner la similarité de Pearson
        return covariance / (std1 * std2) if std1 * std2 != 0 else 0

    similarity_matrix = {}
    for movie1 in movies:
        similarity_matrix[movie1] = {}
        for movie2 in movies:
            vec1 = [data[user].get(movie1) for user in users]
            vec2 = [data[user].get(movie2) for user in users]
            similarity_matrix[movie1][movie2] = round(pearson_similarity(vec1, vec2), 2)
    
    # Affichage de la matrice des similarités
    st.write("Matrice des similarités entre les films :")
    st.table(similarity_matrix)

# Étape 3 : Calcul du Top-N
st.header("3. Calcul du Top-N")
if data:
    n = st.number_input("Entrez le nombre de recommandations (Top-N)", min_value=1, value=3)
    
    # Fonction pour prédire les notes manquantes
    def predict_ratings(user, item, data, similarity_matrix):
        if data[user].get(item) is None:
            # Calcul de la note prédite
            similar_items = similarity_matrix[item]
            weighted_sum = sum(similarity_matrix[item][movie] * data[user].get(movie, 0) for movie in similar_items if data[user].get(movie) is not None)
            sum_of_weights = sum(abs(similarity_matrix[item][movie]) for movie in similar_items if data[user].get(movie) is not None)
            return round(weighted_sum / sum_of_weights, 2) if sum_of_weights > 0 else None
        else:
            return data[user].get(item)
    
    # Remplissage des notes manquantes
    predicted_data = {}
    for user in users:
        predicted_data[user] = {}
        for movie in movies:
            predicted_data[user][movie] = predict_ratings(user, movie, data, similarity_matrix)
    
    # Affichage de la matrice avec les notes prédites
    st.write("Matrice des notes prédites :")
    display_predicted_data = {user: {movie: rating if rating is not None else "Non évalué" for movie, rating in user_ratings.items()} for user, user_ratings in predicted_data.items()}
    st.table(display_predicted_data)
    
    # Recommandation pour un utilisateur donné
    st.header("4. Recommandation pour un utilisateur")
    user = st.selectbox("Sélectionnez un utilisateur :", users)
    movie = st.selectbox("Sélectionnez un film :", movies)
    
    if user and movie:
        original_rating = data[user].get(movie)
        predicted_rating = predicted_data[user].get(movie)
        
        st.write(f"Note originale pour {movie} par {user} : {'Non évalué' if original_rating is None else original_rating}")
        st.write(f"Note prédite pour {movie} par {user} : {predicted_rating}")
        
        if original_rating is None and predicted_rating is not None:
            st.write(f"Recommandation : Oui, nous recommandons {movie} à {user}.")
        elif predicted_rating is not None and predicted_rating >= 4:
            st.write(f"Recommandation : Oui, nous recommandons {movie} à {user}.")
        else:
            st.write(f"Recommandation : Non, nous ne recommandons pas {movie} à {user}.")
import streamlit as st

# Title of the application
st.title("Recommendation System: Collaborative Filtering (Item-Item Top-N)")
st.sidebar.title("RS-CF-APP")
# Step 1: Data loading
st.header("1. Data Loading")
data_option = st.radio("Choose the data loading method:", ["Manual", "CSV File"])

# Data initialization
data = {}
if data_option == "Manual":
    # Manual data entry
    st.write("Enter the data manually:")
    rows = st.number_input("Number of users", min_value=1, value=3)
    cols = st.number_input("Number of movies", min_value=1, value=3)
    
    users = [f"User {i+1}" for i in range(rows)]
    movies = [f"Movie {j+1}" for j in range(cols)]
    
    for user in users:
        data[user] = {}
        for movie in movies:
            value = st.number_input(f"Rating for {user}, {movie} (-1 for missing value)", min_value=-1, max_value=5, value=-1)
            data[user][movie] = value if value != -1 else None
else:
    # Load data from a CSV file
    uploaded_file = st.file_uploader("Upload a CSV file containing ratings", type=["csv"])
    if uploaded_file is not None:
        lines = uploaded_file.readlines()
        movies = lines[0].decode("utf-8").strip().split(",")[1:]  # First line = movie names
        cols = len(movies)
        users = []
        for line in lines[1:]:
            parts = line.decode("utf-8").strip().split(",")
            user = parts[0]
            users.append(user)
            data[user] = {}
            for i, rating in enumerate(parts[1:]):
                data[user][movies[i]] = int(rating) if rating.strip() and int(rating) != -1 else None
        rows = len(users)

# Display the ratings matrix
if data:
    st.write("Ratings Matrix:")
    display_data = {user: {movie: rating if rating is not None else "Not rated" for movie, rating in user_ratings.items()} for user, user_ratings in data.items()}
    st.table(display_data)

# Step 2: Choose similarity method
st.header("2. Choose Similarity Method")
similarity_method = st.selectbox("Select similarity method:", ["Cosine Similarity", "Pearson Similarity"])

# Similarity calculation functions
def cosine_similarity(vec1, vec2):
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2) if a is not None and b is not None)
    # Calculate norms
    norm_vec1 = sum(a ** 2 for a in vec1 if a is not None) ** 0.5
    norm_vec2 = sum(b ** 2 for b in vec2 if b is not None) ** 0.5
    # Return cosine similarity
    return dot_product / (norm_vec1 * norm_vec2) if norm_vec1 * norm_vec2 != 0 else 0

def pearson_similarity(vec1, vec2):
    # Filter common non-null values
    common_ratings = [(a, b) for a, b in zip(vec1, vec2) if a is not None and b is not None]
    if len(common_ratings) == 0:
        return 0  # No similarity if no common users
    
    # Extract common ratings
    ratings1, ratings2 = zip(*common_ratings)
    
    # Calculate means
    mean1 = sum(ratings1) / len(ratings1)
    mean2 = sum(ratings2) / len(ratings2)
    
    # Calculate covariance and standard deviations
    covariance = sum((a - mean1) * (b - mean2) for a, b in common_ratings)
    std1 = (sum((a - mean1) ** 2 for a, _ in common_ratings)) ** 0.5
    std2 = (sum((b - mean2) ** 2 for _, b in common_ratings)) ** 0.5
    
    # Return Pearson similarity
    return covariance / (std1 * std2) if std1 * std2 != 0 else 0

# Step 3: Similarity matrix calculation
st.header("3. Movie Similarity Matrix")
if data:
    similarity_matrix = {}
    for movie1 in movies:
        similarity_matrix[movie1] = {}
        for movie2 in movies:
            vec1 = [data[user].get(movie1) for user in users]
            vec2 = [data[user].get(movie2) for user in users]
            if similarity_method == "Cosine Similarity":
                similarity_matrix[movie1][movie2] = round(cosine_similarity(vec1, vec2), 2)
            else:
                similarity_matrix[movie1][movie2] = round(pearson_similarity(vec1, vec2), 2)
    
    # Display the similarity matrix
    st.write(f"{similarity_method} Matrix:")
    st.table(similarity_matrix)

# Step 4: Top-N Calculation
st.header("4. Top-N Calculation")
if data:
    n = st.number_input("Enter the number of recommendations (Top-N)", min_value=1, max_value=cols, value=3)
    
    # Function to predict missing ratings
    def predict_ratings(user, item, data, similarity_matrix):
        if data[user].get(item) is None:
            # Predicted rating calculation
            similar_items = similarity_matrix[item]
            weighted_sum = sum(similarity_matrix[item][movie] * data[user].get(movie, 0) for movie in similar_items if data[user].get(movie) is not None)
            sum_of_weights = sum(abs(similarity_matrix[item][movie]) for movie in similar_items if data[user].get(movie) is not None)
            return round(weighted_sum / sum_of_weights, 2) if sum_of_weights > 0 else None
        else:
            return data[user].get(item)
    
    # Fill missing ratings
    predicted_data = {}
    for user in users:
        predicted_data[user] = {}
        for movie in movies:
            predicted_data[user][movie] = predict_ratings(user, movie, data, similarity_matrix)
    
    # Display the predicted ratings matrix
    st.write("Predicted Ratings Matrix:")
    display_predicted_data = {user: {movie: rating if rating is not None else "Not rated" for movie, rating in user_ratings.items()} for user, user_ratings in predicted_data.items()}
    st.table(display_predicted_data)
    
    # Recommendation for a specific user
    st.header("5. Recommendation for a User")
    user = st.selectbox("Select a user:", users)
    movie = st.selectbox("Select a movie:", movies)
    
    if user and movie:
        original_rating = data[user].get(movie)
        predicted_rating = predicted_data[user].get(movie)
        
        st.write(f"Original rating for {movie} by {user}: {'Not rated' if original_rating is None else original_rating}")
        st.write(f"Predicted rating for {movie} by {user}: {predicted_rating}")
        
        if predicted_rating is not None and predicted_rating >= 3:
            st.write(f"Recommendation: Yes, we recommend {movie} to {user}.")
        else:
            st.write(f"Recommendation: No, we do not recommend {movie} to {user}.")
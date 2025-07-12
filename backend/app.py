import pickle
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

if __name__ == "__main__":
    # Step 1: Load the dataset
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'Zomato_Cleaned.csv')
    df = pd.read_csv(file_path)
    print("Initial shape:", df.shape)
    print(df.head(3))

    # Step 2: View columns
    print("\n🧾 Available columns in the dataset:")
    print(df.columns.tolist())

    # Step 3: Handle missing values
    df.dropna(subset=['Cuisines', 'Rating', 'Average_Cost_for_two'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Step 4: Clean the cuisine column (take first cuisine only, lowercase + strip)
    df['Primary_Cuisine'] = df['Cuisines'].str.lower().str.split(',').str[0].str.strip()

    # Step 5: Encode categorical columns
    le_cuisine = LabelEncoder()
    le_cuisine.fit(df['Primary_Cuisine'])

    le_city = LabelEncoder()
    df['City_Clean'] = df['City'].str.lower().str.strip()
    le_city.fit(df['City_Clean'])

    df['Cuisine_Encoded'] = le_cuisine.transform(df['Primary_Cuisine'])
    df['City_Encoded'] = le_city.transform(df['City_Clean'])

    # Step 6: Final features for clustering
    features = df[[
        'Cuisine_Encoded',
        'Average_Cost_for_two',
        'Rating',
        'Votes',
        'City_Encoded'
    ]]

    # Step 7: Standardize the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    # Step 8: Elbow Method (optional visualization)
    inertia = []
    K = range(2, 11)
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertia.append(kmeans.inertia_)

    plt.figure(figsize=(8, 4))
    plt.plot(K, inertia, 'bx-')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.title('Elbow Method For Optimal k')
    elbow_plot_path = os.path.join(os.path.dirname(__file__), 'data', 'elbow_plot.png')
    plt.savefig(elbow_plot_path)
    plt.close()

    # Step 9: Silhouette Score
    score = silhouette_score(X_scaled, kmeans.labels_)
    print("Silhouette Score:", score)

    # Step 10: PCA (optional)
    pca = PCA(n_components=5)
    X_pca = pca.fit_transform(X_scaled)

    # Step 11: Apply final KMeans (choose k=5 or based on elbow)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    df['Cluster'] = clusters

    # Step 12: Save everything in one pickle file
    model_bundle = {
        'kmeans': kmeans,
        'scaler': scaler,
        'le_cuisine': le_cuisine,
        'le_city': le_city,
        'df': df
    }

    bundle_path = os.path.join(os.path.dirname(__file__), 'data', 'full_model_bundle.pkl')
    with open(bundle_path, 'wb') as f:
        pickle.dump(model_bundle, f)

    print("✅ Everything saved in one file: full_model_bundle.pkl")
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # Step 1: Load the dataset
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'Zomato_Cleaned.csv')
    df = pd.read_csv(file_path)
    print("Initial shape:", df.shape)
    print(df.head(3))

    # Step 2: View columns
    print("\n🧾 Available columns in the dataset:")
    print(df.columns.tolist())

    # Step 3: Handle missing values (correct column names)
    df.dropna(subset=['Cuisines', 'Rating', 'Average_Cost_for_two'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Step 4: Encode categorical columns
    le_cuisine = LabelEncoder()
    le_city = LabelEncoder()
    df['Cuisine_Encoded'] = le_cuisine.fit_transform(df['Cuisines'])
    df['City_Encoded'] = le_city.fit_transform(df['City'])

    # Step 5: Final features for clustering
    features = df[[
        'Cuisine_Encoded',
        'Average_Cost_for_two',
        'Rating',
        'Votes',
        'City_Encoded'
    ]]

    # Step 6: Standardize the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    # Step 7: Elbow Method for optimal k
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

    # Step 8: Apply KMeans (you can change k based on the elbow plot)
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    df['Cluster'] = clusters

    # Step 9: Save the clustered dataset
    clustered_csv_path = os.path.join(os.path.dirname(__file__), 'data', 'zomato_clustered_cleaned.csv')
    df.to_csv(clustered_csv_path, index=False)
    print("✅ Clustering done. File saved to:", clustered_csv_path)





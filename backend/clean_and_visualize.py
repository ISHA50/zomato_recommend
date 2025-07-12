import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load dataset
df = pd.read_csv("data/zomato.csv")
print(df.shape)
# ----------------- Data Cleaning -----------------

# Drop duplicates
df.drop_duplicates(inplace=True)

# Drop rows with missing essential fields
df.dropna(subset=["RestaurantName", "Cuisines", "City", "Rating", "Average_Cost_for_two"], inplace=True)

# Convert cost and rating to numeric
df["Average_Cost_for_two"] = pd.to_numeric(df["Average_Cost_for_two"], errors='coerce')
df["Rating"] = pd.to_numeric(df["Rating"], errors='coerce')

# Drop rows with NaNs in numeric columns after conversion
df.dropna(subset=["Rating", "Average_Cost_for_two"], inplace=True)

# Remove outliers based on IQR
Q1 = df["Average_Cost_for_two"].quantile(0.25)
Q3 = df["Average_Cost_for_two"].quantile(0.75)
IQR = Q3 - Q1
df = df[(df["Average_Cost_for_two"] >= Q1 - 1.5 * IQR) & (df["Average_Cost_for_two"] <= Q3 + 1.5 * IQR)]

# Reset index
df.reset_index(drop=True, inplace=True)

# Save cleaned data
df.to_csv("Zomato_Cleaned.csv", index=False)
print("✅ Cleaned data saved to 'Zomato_Cleaned.csv'")
print("Final shape:",df.shape)

# ----------------- Data Visualization -----------------

sns.set(style="whitegrid")
output_dir = "visuals"
os.makedirs(output_dir, exist_ok=True)

# 1. Rating Distribution
plt.figure(figsize=(8, 4))
sns.histplot(df["Rating"], bins=20, kde=True, color="tomato")
plt.title("Rating Distribution")
plt.xlabel("Rating")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(f"{output_dir}/rating_distribution.png")
plt.close()

# 2. Top 10 Cities with Most Restaurants
plt.figure(figsize=(10, 4))
top_cities = df["City"].value_counts().nlargest(10)
sns.barplot(x=top_cities.index, y=top_cities.values, palette="viridis")
plt.title("Top 10 Cities by Number of Restaurants")
plt.xlabel("City")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{output_dir}/top_cities.png")
plt.close()

# 3. Average Cost Distribution
plt.figure(figsize=(8, 4))
sns.histplot(df["Average_Cost_for_two"], bins=30, kde=True, color="seagreen")
plt.title("Average Cost for Two Distribution")
plt.xlabel("Cost (₹)")
plt.ylabel("Count")
plt.tight_layout()
plt.savefig(f"{output_dir}/cost_distribution.png")
plt.close()

# 4. Cost vs Rating
plt.figure(figsize=(8, 5))
sns.scatterplot(data=df, x="Rating", y="Average_Cost_for_two", hue="City", legend=False, alpha=0.6)
plt.title("Cost vs Rating")
plt.xlabel("Rating")
plt.ylabel("Cost for Two (₹)")
plt.tight_layout()
plt.savefig(f"{output_dir}/cost_vs_rating.png")
plt.close()
os.makedirs("visuals", exist_ok=True)
print("✅ Plots saved to the 'visuals' folder.")

<script>
  document.addEventListener("DOMContentLoaded", () => {
    const userId = localStorage.getItem("user_id");
    const resContainer = document.getElementById("results");

    // Load Default Restaurants on Page Load
    loadDefaultRestaurants();

    // Load Recent Searches if user is logged in
    if (userId) {
      loadRecentSearchRecommendations(userId);
    } else {
      const recentContainer = document.getElementById("recentContainer");
      if (recentContainer) {
        recentContainer.innerHTML = '<p class="text-center">Login to see your recent searches.</p>';
      }
    }

    // Handle Search Button
    document.getElementById("searchBtn").addEventListener("click", () => {
      const query = document.getElementById("searchInput").value.trim();
      if (query) {
        window.location.href = `search.html?q=${encodeURIComponent(query)}`;
      }
    });

    // Handle Cuisine Dropdown Change
    document.getElementById("cuisineFilter").addEventListener("change", async (e) => {
      const cuisine = e.target.value;
      resContainer.innerHTML = "Loading...";
      try {
        const response = await fetch(`http://127.0.0.1:5000/search?q=${encodeURIComponent(cuisine)}${userId ? `&user_id=${userId}` : ''}`);
        const data = await response.json();
        renderRestaurants(data, resContainer);
      } catch (err) {
        console.error("Cuisine fetch error:", err);
        resContainer.innerHTML = '<p class="text-danger text-center">Error loading data.</p>';
      }
    });
  });

  // Load Default Data
  async function loadDefaultRestaurants() {
    const resContainer = document.getElementById("results");
    resContainer.innerHTML = "Loading default restaurants...";
    try {
      const response = await fetch("http://127.0.0.1:5000/default_restaurants");
      const data = await response.json();
      renderRestaurants(data, resContainer);
    } catch (err) {
      console.error("Default load error:", err);
      resContainer.innerHTML = '<p class="text-danger text-center">Could not load default data.</p>';
    }
  }

  // Render Restaurant Cards
  function renderRestaurants(data, container) {
    if (!Array.isArray(data) || data.length === 0) {
      container.innerHTML = '<p class="text-center">No results found.</p>';
      return;
    }

    const imageMap = {
      pizza: ["/images/pizza1.jpg", "/images/pizza2.jpg"],
      burger: ["/images/burger1.jpg", "/images/burger2.jpg"],
      italian: ["/images/italian1.jpg", "/images/italian2.jpg"],
      chinese: ["/images/chinese1.jpg"],
      default: ["/images/food1.jpg"]
    };

    function getImage(cuisine) {
      cuisine = cuisine.toLowerCase();
      for (const key in imageMap) {
        if (cuisine.includes(key)) {
          const imgs = imageMap[key];
          return imgs[Math.floor(Math.random() * imgs.length)];
        }
      }
      const fallback = imageMap["default"];
      return fallback[Math.floor(Math.random() * fallback.length)];
    }

    container.innerHTML = data.map(item => `
      <div class="col-md-3">
        <div class="card h-100">
          <img src="${getImage(item.Cuisines)}" class="card-img-top" style="height: 200px; object-fit: cover;" alt="${item.RestaurantName}">
          <div class="card-body">
            <h5 class="card-title">${item.RestaurantName}</h5>
            <p><strong>Cuisines:</strong> ${item.Cuisines}</p>
            <p><strong>City:</strong> ${item.City}</p>
            <p><strong>Rating:</strong> ⭐ ${item.Rating}</p>
            <p><strong>Cost:</strong> ₹${item.Average_Cost_for_two}</p>
          </div>
        </div>
      </div>
    `).join("");
  }

  // Load Past Searches from Backend
  async function loadRecentSearchRecommendations(userId) {
    const recentContainer = document.getElementById("recentContainer");
    try {
      const response = await fetch(`http://127.0.0.1:5000/history_recommend?user_id=${userId}`);
      const result = await response.json();
      const data = result.recommendations || result;

      if (!Array.isArray(data) || data.length === 0) {
        recentContainer.innerHTML = '<p class="text-center">No recent searches found.</p>';
        return;
      }

      const imageMap = {
        pizza: ["/images/pizza1.jpg", "/images/pizza2.jpg"],
        burger: ["/images/burger1.jpg", "/images/burger2.jpg"],
        italian: ["/images/italian1.jpg", "/images/italian2.jpg"],
        default: ["/images/food1.jpg"]
      };

      function getImage(cuisine) {
        cuisine = cuisine.toLowerCase();
        for (const key in imageMap) {
          if (cuisine.includes(key)) {
            const imgs = imageMap[key];
            return imgs[Math.floor(Math.random() * imgs.length)];
          }
        }
        const fallback = imageMap["default"];
        return fallback[Math.floor(Math.random() * fallback.length)];
      }

      recentContainer.innerHTML = data.map(item => `
        <div class="col-md-3">
          <div class="card h-100">
            <img src="${getImage(item.Cuisines)}" class="card-img-top" alt="${item.RestaurantName}" style="height:200px;object-fit:cover;">
            <div class="card-body">
              <h5 class="card-title">${item.RestaurantName}</h5>
              <p><strong>Cuisines:</strong> ${item.Cuisines}</p>
              <p><strong>City:</strong> ${item.City}</p>
              <p><strong>Rating:</strong> ⭐ ${item.Rating}</p>
              <p><strong>Cost:</strong> ₹${item.Average_Cost_for_two}</p>
            </div>
          </div>
        </div>
      `).join("");

    } catch (err) {
      console.error("Error loading history:", err);
      recentContainer.innerHTML = '<p class="text-danger text-center">Error loading recent searches.</p>';
    }
  }
</script>

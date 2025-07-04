document.addEventListener("DOMContentLoaded", () => {
  const userId = localStorage.getItem("user_id");

  if (!userId) {
    console.warn("No user ID found in localStorage.");
    return;
  }

  fetch(`http://127.0.0.1:5000/history_recommend?user_id=${userId}`)
    .then(res => res.json())
    .then(result => {
      const data = result.recommendations || [];
      const container = document.getElementById("userHistoryContainer");

      if (!container) {
        console.error("Container #userHistoryContainer not found in HTML.");
        return;
      }

      if (data.length === 0) {
        container.innerHTML = '<p class="text-center">No personalized recommendations found.</p>';
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

      container.innerHTML = data.map(item => `
        <div class="col-md-3">
          <div class="card h-100">
            <img src="${getImage(item.Cuisines)}" class="card-img-top" alt="${item.RestaurantName}" style="height:200px; object-fit:cover;">
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
    })
    .catch(err => {
      console.error("Error fetching recent history data:", err);
      const container = document.getElementById("userHistoryContainer");
      if (container) {
        container.innerHTML = '<p class="text-danger text-center">Failed to load user history.</p>';
      }
    });
});

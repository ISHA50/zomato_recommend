// document.addEventListener("DOMContentLoaded", () => {
//   const userId = localStorage.getItem("user_id");

//   if (!userId) {
//     console.warn("No user ID found in localStorage.");
//     return;
//   }

//   fetch(`http://127.0.0.1:5000/history_recommend?user_id=${userId}`)
//     .then(res => res.json())
//     .then(result => {
//       const data = result.recommendations || [];
//       const container = document.getElementById("userHistoryContainer");

//       if (!container) {
//         console.error("Container #userHistoryContainer not found in HTML.");
//         return;
//       }

//       if (data.length === 0) {
//         container.innerHTML = '<p class="text-center">No personalized recommendations found.</p>';
//         return;
//       }

//   const imageMap = {
//     pizza: ["images/pizza1.jpg", "images/pizza2.jpg", "images/pizza3.jpg"],
//     icecream: ["images/ice1","images/ice2","images/ice3"],
//     burger: ["images/burger1.jpg", "images/burger2.jpg"],
//     momos: ["images/momos1.jpg", "images/momos2.jpg"],
//     pasta: ["images/pasta1.jpg"],
//     thai: ["images/thai1.jpg", "images/thai2.jpg"],
//     chai: ["images/thai1.jpg", "images/thai2.jpg"],
//     afghani: ["images/afghani1.jpg"],
//     chinese: ["images/chinese1.jpg"],
//     italian: ["images/SI1.jpg"],
//     american: ["images/american1.jpg"],
//     chaat: ["images/american1.jpg"],
//     mexican: ["images/mexican1.jpg"],
//     north_indian: ["images/indian1.jpg", "images/indian2.jpg"],
//     southindian: ["images/south1.jpg", "images/SI2.jpg","images/SI3.jpg","images/SI4.jpg","images/SI5.jpg","images/SI6.jpg","images/SI7.jpg","images/SI8.jpg",
//     "images/SI9.jpg","images/SI10.jpg"],
//     default: ["images/pizza5.jpg"]
//   };

//       function getImage(cuisine) {
//         cuisine = cuisine.toLowerCase();
//         for (const key in imageMap) {
//           if (cuisine.includes(key)) {
//             const imgs = imageMap[key];
//             return imgs[Math.floor(Math.random() * imgs.length)];
//           }
//         }
//         const fallback = imageMap["default"];
//         return fallback[Math.floor(Math.random() * fallback.length)];
//       }

//       container.innerHTML = data.map(item => `
//         <div class="col-md-3">
//           <div class="card h-100">
//             <img src="${getImage(item.Cuisines)}" class="card-img-top" alt="${item.RestaurantName}" style="height:200px; object-fit:cover;">
//             <div class="card-body">
//               <h5 class="card-title">${item.RestaurantName}</h5>
//               <p><strong>Cuisines:</strong> ${item.Cuisines}</p>
//               <p><strong>City:</strong> ${item.City}</p>
//               <p><strong>Rating:</strong> ⭐ ${item.Rating}</p>
//               <p><strong>Cost:</strong> ₹${item.Average_Cost_for_two}</p>
//             </div>
//           </div>
//         </div>
//       `).join("");
//     })
//     .catch(err => {
//       console.error("Error fetching recent history data:", err);
//       const container = document.getElementById("userHistoryContainer");
//       if (container) {
//         container.innerHTML = '<p class="text-danger text-center">Failed to load user history.</p>';
//       }
//     });
// });


















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
      const pastQueries = result.based_on_queries || [];
      const container = document.getElementById("userHistoryContainer");

      if (!container) {
        console.error("Container #userHistoryContainer not found in HTML.");
        return;
      }

      if (data.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">No personalized recommendations found.</p>';
        return;
      }

      // Optional: Log what query was used
      console.log("📌 Based on past searches:", pastQueries);

      const imageMap = {
        pizza: ["images/pizza1.jpg", "images/pizza2.jpg", "images/pizza3.jpg"],
        icecream: ["images/ice1.jpg", "images/ice2.jpg", "images/ice3.jpg"],
        burger: ["images/burger1.jpg", "images/burger2.jpg"],
        momos: ["images/momos1.jpg", "images/momos2.jpg"],
        pasta: ["images/pasta1.jpg"],
        thai: ["images/thai1.jpg", "images/thai2.jpg"],
        chai: ["images/thai1.jpg", "images/thai2.jpg"],
        afghani: ["images/afghani1.jpg"],
        chinese: ["images/chinese1.jpg"],
        italian: ["images/SI1.jpg"],
        american: ["images/american1.jpg"],
        chaat: ["images/american1.jpg"],
        mexican: ["images/mexican1.jpg"],
        north_indian: ["images/indian1.jpg", "images/indian2.jpg"],
        southindian: [
          "images/south1.jpg", "images/SI2.jpg", "images/SI3.jpg", "images/SI4.jpg",
          "images/SI5.jpg", "images/SI6.jpg", "images/SI7.jpg", "images/SI8.jpg",
          "images/SI9.jpg", "images/SI10.jpg"
        ],
        default: ["images/pizza5.jpg"]
      };

      function getImage(cuisineStr) {
        const cuisine = cuisineStr.toLowerCase().replace(/\s+/g, '_');
        for (const key in imageMap) {
          if (cuisine.includes(key)) {
            const imgs = imageMap[key];
            return imgs[Math.floor(Math.random() * imgs.length)];
          }
        }
        const fallback = imageMap["default"];
        return fallback[Math.floor(Math.random() * fallback.length)];
      }

      // Render recommendations
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
      console.error("Error fetching user history data:", err);
      const container = document.getElementById("userHistoryContainer");
      if (container) {
        container.innerHTML = '<p class="text-danger text-center">Failed to load user history.</p>';
      }
    });
});

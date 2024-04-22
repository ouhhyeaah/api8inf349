document.addEventListener("DOMContentLoaded", function () {
  var addToCartButtons = document.querySelectorAll(".add_to_cart");
  localStorage.clear();
  addToCartButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var productId = button.getAttribute("data-product-id");

      var quantityInput =
        button.parentElement.parentElement.querySelector(".quantity");
      var errorMessage =
        button.parentElement.parentElement.querySelector(".error-message");
      var quantity = quantityInput.value;
      if (quantity > 0) {
        // Réinitialisez le message d'erreur s'il y en avait un précédemment
        errorMessage.textContent = "";
        // Effectuez l'ajout au panier ou toute autre action appropriée
        localStorage.setItem(
          `product_${productId}`,
          `{ id: ${productId}, quantity: ${quantity} }`,
        );
      } else if (quantity > 10) {
        errorMessage.textContent =
          "La quantité ne peut pas être supérieure à 10";
      } else {
        // Affichez un message d'erreur spécifique au produit
        errorMessage.textContent = "La quantité ne peut pas être nulle.";
      }
      checkCart();
    });
  });
});

// Path: app.js
function checkCart() {
  var cartItems = Object.keys(localStorage).filter(function (key) {
    return key.includes("product_");
  });
  console.log(cartItems);
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("form");
  const btns = document.getElementById("btns");
  function order() {
    const productInputs = document.querySelectorAll("#form .product"); // Sélectionnez tous les éléments avec la classe .product
    const response_span = document.getElementById("res");
    // Si le nombre de produits est supérieur à 2, construisez un objet products
    if (productInputs.length >= 2) {
      const products = [];
      productInputs.forEach((productInput) => {
        const productId = productInput.querySelector("#product_id").value;
        const productQuantity =
          productInput.querySelector("#product_quantity").value;
        products.push({ id: productId, quantity: productQuantity });
      });
      // Effectuez la requête avec l'objet products
      fetch("/order", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ products }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.order) {
            response_span.innerHTML =
              "Order placed successfully, Order ID: " +
              data.order.id +
              "<a href='http://localhost:5000/order/" +
              data.order.id +
              "'>" +
              dara.order.id +
              "</a>";

            response_span.style.color = "green";
          } else {
            response_span.innerHTML =
              data.errors.product.name || "Order failed";
            response_span.style.color = "red";
          }
        });
    } else {
      // Si le nombre de produits est inférieur ou égal à 2, effectuez la requête normale
      const productId = document.getElementById("product_id").value;
      const productQuantity = document.getElementById("product_quantity").value;
      fetch("/order", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product: {
            id: productId,
            quantity: productQuantity,
          },
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.order) {
            response_span.innerHTML =
              "Order placed successfully, Order ID: " +
              data.order.id +
              "<a href='http://localhost:5000/order/" +
              data.order.id +
              "'>" +
              "</br> Lien vers la commande " +
              data.order.id +
              "</a>" +
              "</br>" +
              "<a href = 'http://localhost:5000/order/" +
              data.order.id +
              "/complete'>" +
              "</br> Completer la commande " +
              data.order.id +
              "</a>";
            response_span.style.color = "green";
          } else {
            response_span.innerHTML =
              data.errors.product.name || "Order failed";
            response_span.style.color = "red";
          }
        });
    }
  }

  // Ajoutez un écouteur d'événements 'submit' au formulaire
  form.addEventListener("submit", function (event) {
    event.preventDefault(); // Empêche la soumission du formulaire par défaut
    if (form.checkValidity()) {
      // Vérifiez si les champs du formulaire sont valides
      order(); // Si les champs sont valides, appelez la fonction order()
    }
    form.classList.add("was-validated"); // Ajoutez la classe 'was-validated' pour afficher les messages d'erreur
  });

  // Ajoutez un écouteur d'événements au bouton "Add Product" pour ajouter de nouveaux champs d'entrée
  const addProductBtn = document.getElementById("addProductBtn");
  addProductBtn.addEventListener("click", function () {
    const productFields = `
              <div class="col-md-4">
                  <label for="validationCustom01" class="form-label">Product ID</label>
                  <input type="number" class="form-control" id="product_id" placeholder="Enter the product ID" required />
                  <div class="valid-feedback">Looks good!</div>
              </div>
              <div class="col-md-4">
                  <label for="validationCustom02" class="form-label">Quantity</label>
                  <input type="number" class="form-control" id="product_quantity" placeholder="Enter the quantity" required />
                  <div class="valid-feedback">Looks good!</div>
              </div>
        `;
    const productContainer = document.createElement("div");
    productContainer.classList.add(
      "d-flex",
      "justify-content-center",
      "my-3",
      "product",
    );
    productContainer.innerHTML = productFields;
    form.insertBefore(productContainer, btns); // Ajoutez les nouveaux champs d'entrée avant le bouton
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const ORDER_ID = document.getElementById("order_id").innerText;
  const client_information_form = document.getElementById(
    "client-informations",
  );
  function complete_informations() {
    const inputs = Array.from(document.querySelectorAll("input")).slice(0, 6);
    const RES = document.getElementById("res");
    const btn = document.getElementById("client-informations-button");
    const isAnyInputEmpty = Array.from(inputs).some(
      (input) => input.value.trim() === "",
    );
    if (isAnyInputEmpty) {
      RES.innerText = "Please fill in all fields";
      RES.classList = "text-danger fw-bold mx-auto w-100";
      return;
    }
    fetch(`/order/${ORDER_ID}`, {
      method: "PUT",
      headers: {
        "Content-type": "application/json",
      },
      body: JSON.stringify({
        order: {
          email: inputs[0].value,
          shipping_information: {
            country: capitalizeFirstLetter(inputs[5].value),
            address: inputs[1].value,
            postal_code: inputs[3].value,
            city: capitalizeFirstLetter(inputs[2].value),
            province: inputs[4].value.toUpperCase(),
          },
        },
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.order) {
          RES.innerText = "Your information has been correctly added";
          RES.classList = "text-success fw-bold mx-auto w-100";
          btn.classList.add("bg-success", "bg-gradient");
        } else {
          RES.innerText = data.errrors;
        }
      });
  }
  // Ajoutez un écouteur d'événements 'submit' au formulaire
  client_information_form.addEventListener("submit", function (event) {
    event.preventDefault(); // Empêche la soumission du formulaire par défaut
    if (client_information_form.checkValidity()) {
      // Vérifiez si les champs du formulaire sont valides
      complete_informations(); // Si les champs sont valides, appelez la fonction order()
    }
    client_information_form.classList.add("was-validated"); // Ajoutez la classe 'was-validated' pour afficher les messages d'erreur
  });

  // Partie paiement

  const payment_form = document.getElementById("payment-informations");
  payment_form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (payment_form.checkValidity()) {
      complete_payment();
    }
    payment_form.classList.add("was-validated");
  });
  function complete_payment() {
    const inputs = Array.from(document.querySelectorAll("input")).slice(6, 10);
    const RES = document.getElementById("res");
    const isAnyInputEmpty = Array.from(inputs).some(
      (input) => input.value.trim() === "",
    );
    if (isAnyInputEmpty) {
      RES.innerText = "Please fill in all fields";
      RES.classList = "text-danger fw-bold mx-auto w-100";
      return;
    }
    const expiration_month = inputs[3].value.split("-")[1];
    const expiration_year = inputs[3].value.split("-")[0];
    const credit_card_content = {
      name: inputs[0].value,
      number: inputs[1].value,
      expiration_year: expiration_year,
      cvv: inputs[2].value,
      expiration_month: expiration_month,
    };
    console.log(credit_card_content);

    // VALID CARD
    // 4242 4242 4242 4242
    // INVALID CARD
    // 4000 0000 0000 0002
    fetch(`/order/${ORDER_ID}`, {
      method: "PUT",
      headers: {
        "Content-type": "application/json",
      },
      body: JSON.stringify({
        credit_card: credit_card_content,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.order) {
          RES.innerText = "Your order has been completed";
          RES.classList = "text-success fw-bold mx-auto w-100";
          btn.classList.add("bg-success", "bg-gradient");
        } else {
          RES.innerText = data.errrors;
        }
      });
  }
  const creditCardInput = document.getElementById("credit_card_number");
  creditCardInput.addEventListener("input", function (event) {
    let trimmedValue = event.target.value.replace(/\s+/g, ""); // Supprimer les espaces existants
    let formattedValue = "";
    for (let i = 0; i < trimmedValue.length; i++) {
      if (i > 0 && i % 4 === 0) {
        formattedValue += " "; // Ajouter un espace tous les quatre caractères
      }
      formattedValue += trimmedValue[i];
    }
    event.target.value = formattedValue.trim(); // Supprimer les espaces en trop à la fin
  });
  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }
});

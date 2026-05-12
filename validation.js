const data = {
  Colombia: {
    Medellin: ["El Poblado", "Laureles", "Envigado", "Sabaneta"],
    Bogota: ["Usaquén", "Chapinero","Zona Rosa"],
    Cali: ["Granada", "Unicentro", "Ciudad Jardín"]
  },
  USA: {
    Miami: ["Brickell", "Coral Gables"],
    Orlando: ["Downtown", "International Drive"],
  }
};

function initFormValidation() {
  const form = document.getElementById("form");
  const country = document.getElementById("country");
  const city = document.getElementById("city");
  const locationSelect = document.getElementById("location");

  if (!form || !country || !city || !locationSelect) {
    console.warn("validation.js: faltan elementos del formulario en esta página.");
    return;
  }

  function loadCountries() {
    country.innerHTML = '<option value="">País</option>';

    Object.keys(data).forEach(c => {
      country.innerHTML += `<option value="${c}">${c}</option>`;
    });
  }

  country.addEventListener("change", () => {
    city.innerHTML = '<option value="">Ciudad</option>';
    locationSelect.innerHTML = '<option value="">Ubicación</option>';

    if (!data[country.value]) return;

    Object.keys(data[country.value]).forEach(c => {
      city.innerHTML += `<option value="${c}">${c}</option>`;
    });
  });

  city.addEventListener("change", () => {
    locationSelect.innerHTML = '<option value="">Ubicación</option>';

    if (!data[country.value] || !data[country.value][city.value]) return;

    data[country.value][city.value].forEach(loc => {
      locationSelect.innerHTML += `<option value="${loc}">${loc}</option>`;
    });
  });

  loadCountries();

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    let valid = true;

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const birth = document.getElementById("birthdate").value;
    const source = document.getElementById("source").value;
    const terms = document.getElementById("terms").checked;
    const selectedLocation = locationSelect.value;

    [
      "error-name",
      "error-email",
      "error-phone",
      "error-country",
      "error-city",
      "error-location",
      "error-birthdate",
      "error-source",
      "error-terms"
    ].forEach(id => {
      const errorElement = document.getElementById(id);
      if (errorElement) errorElement.innerText = "";
    });

    if (name.split(" ").length < 2) {
      document.getElementById("error-name").innerText = "Nombre y apellido";
      valid = false;
    }

    if (!email.includes("@")) {
      document.getElementById("error-email").innerText = "Email inválido";
      valid = false;
    }

    if (!phone.startsWith("+57") && !phone.startsWith("+1")) {
      document.getElementById("error-phone").innerText = "Debe iniciar con +57 o +1";
      valid = false;
    }

    if (!country.value) {
      document.getElementById("error-country").innerText = "Seleccione país";
      valid = false;
    }

    if (!city.value) {
      document.getElementById("error-city").innerText = "Seleccione ciudad";
      valid = false;
    }

    if (!selectedLocation) {
      document.getElementById("error-location").innerText = "Seleccione ubicación";
      valid = false;
    }

    if (!birth) {
      document.getElementById("error-birthdate").innerText = "Ingrese fecha";
      valid = false;
    }

    if (!source) {
      document.getElementById("error-source").innerText = "Seleccione opción";
      valid = false;
    }

    if (!terms) {
      document.getElementById("error-terms").innerText = "Debe aceptar";
      valid = false;
    }

    if (valid) {
      alert("¡Bienvenido a Brasa Points!Tu registro ha sido exitoso. Recibirás un email de confirmación en los próximos minutos con los detalles de tu cuenta y cómo empezar a acumular puntos.¡Ya puedes disfrutar de tus beneficios en cualquiera de nuestras 14 ubicaciones!");
      
      form.reset();
      city.innerHTML = '<option value="">Ciudad</option>';
      locationSelect.innerHTML = '<option value="">Ubicación</option>';
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initFormValidation);
} else {
  initFormValidation();
}
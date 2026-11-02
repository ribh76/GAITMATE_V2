const form = document.querySelector("[data-contact-form]");
const success = document.querySelector("[data-contact-success]");

if (form && success) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    success.hidden = false;
  });
}

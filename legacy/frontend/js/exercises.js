document.querySelectorAll(".set-toggle").forEach((button) => {
  button.addEventListener("click", () => {
    button.classList.toggle("is-complete");
    button.setAttribute("aria-pressed", String(button.classList.contains("is-complete")));
  });
});

document.querySelectorAll(".exercise-row").forEach((row) => {
  const ratingButtons = row.querySelectorAll("[data-rating]");

  ratingButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const selected = Number(button.dataset.rating);
      ratingButtons.forEach((item) => {
        const isSelected = Number(item.dataset.rating) === selected;
        item.classList.toggle("is-selected", isSelected);
        item.setAttribute("aria-pressed", String(isSelected));
      });
    });
  });

  const textarea = row.querySelector(".feedback-text");
  const counter = row.querySelector("[data-count]");

  if (textarea && counter) {
    textarea.addEventListener("input", () => {
      counter.textContent = `${textarea.value.length}/300`;
    });
  }
});

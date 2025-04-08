// Heart and pencil button behavior
document.body.addEventListener("click", function (e) {
  if (e.target.closest(".heart-button")) {
    e.target.closest(".heart-button").classList.toggle("is-clicked-heart");
  }
});

// Seleziona elementi
const toggleButton = document.getElementById("toggleFilters");
const closeButton = document.getElementById("closeFilters");
const filterPanel = document.getElementById("filterPanel");
const overlay = document.querySelector(".overlay");

// Mostra/nasconde il pannello
toggleButton.addEventListener("click", () => {
  filterPanel.classList.toggle("is-visible");
  overlay.classList.toggle("is-visible");
});

closeButton.addEventListener("click", () => {
  filterPanel.classList.remove("is-visible");
  overlay.classList.remove("is-visible");
});

//chiude cliccando sull'overlay
overlay.addEventListener("click", () => {
  filterPanel.classList.remove("is-visible");
  overlay.classList.remove("is-visible");
});

//chiusura panel se clicco fuori
document.addEventListener("click", (event) => {
  if (
    !filterPanel.contains(event.target) &&
    !toggleButton.contains(event.target) &&
    !filterPanel.classList.contains("is-visible")
  ) {
    filterPanel.classList.remove("is-visible");
    overlay.classList.remove("is-visible");
  }
});

//apparizione drink casuale
const diceButton = document.getElementById("diceButton");
const modal = document.getElementById("modal");
const modalBackground = modal.querySelector(".modal-background");

// Mostra la modale al clic del bottone dado
diceButton.addEventListener("click", () => {
  modal.classList.add("is-active");
});

// Chiude la modale al clic sullo sfondo
modalBackground.addEventListener("click", () => {
  modal.classList.remove("is-active");
});

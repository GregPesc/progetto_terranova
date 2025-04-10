document.querySelectorAll(".delete").forEach((button) => {
  button.addEventListener("click", () => {
    button.closest(".notification").remove();
  });
});

document.addEventListener("DOMContentLoaded", () => {
  // Get all "navbar-burger" elements
  const $navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll(".navbar-burger"),
    0
  );

  // Add a click event on each of them
  $navbarBurgers.forEach((el) => {
    el.addEventListener("click", () => {
      // Get the target from the "data-target" attribute
      const target = el.dataset.target;
      const $target = document.getElementById(target);

      // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
      el.classList.toggle("is-active");
      $target.classList.toggle("is-active");
    });
  });
});

// Heart and pencil button behavior
document.body.addEventListener("click", function (e) {
  if (e.target.closest(".trash-button")) {
    e.target.closest(".trash-button").classList.toggle("is-clicked-trash");
  }

  if (e.target.closest(".heart-button")) {
    e.target.closest(".heart-button").classList.toggle("is-clicked-heart");
  }
});

// homepage
const images = document.querySelectorAll(".scroll-image");

window.addEventListener("scroll", () => {
  const viewportHeight = window.innerHeight;

  images.forEach((image) => {
    const rect = image.getBoundingClientRect();

    // Check if the image is in the viewport
    if (rect.top <= viewportHeight && rect.bottom >= 0) {
      image.classList.add("active");
    } else {
      image.classList.remove("active");
    }
  });
});

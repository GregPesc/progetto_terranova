document.addEventListener("DOMContentLoaded", () => {
  // Delete notification buttons
  document.querySelectorAll(".delete").forEach((button) => {
    button.addEventListener("click", () => {
      button.closest(".notification").remove();
    });
  });

  // Navbar burger menu
  const $navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll(".navbar-burger"),
    0
  );

  $navbarBurgers.forEach((el) => {
    el.addEventListener("click", () => {
      const target = el.dataset.target;
      const $target = document.getElementById(target);

      el.classList.toggle("is-active");
      $target.classList.toggle("is-active");
    });
  });

  // Set top padding for main content based on navbar height
  function adjustContentPadding() {
    const navbar = document.querySelector(".navbar");
    const content = document.getElementById("content");

    if (navbar && content) {
      const navbarHeight = navbar.offsetHeight;
      content.style.paddingTop = navbarHeight + "px";
    }
  }

  // Adjust padding on load
  adjustContentPadding();

  // Adjust padding on window resize
  window.addEventListener("resize", adjustContentPadding);

  // Heart and trash button behavior
  document.body.addEventListener("click", function (e) {
    if (e.target.closest(".trash-button")) {
      e.target.closest(".trash-button").classList.toggle("is-clicked-trash");
    }

    if (e.target.closest(".heart-button")) {
      e.target.closest(".heart-button").classList.toggle("is-clicked-heart");
    }
  });

  // Homepage scroll animation
  const images = document.querySelectorAll(".scroll-image");

  // Make all images visible immediately on page load
  images.forEach((image) => {
    image.classList.add("active");
  });

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
});

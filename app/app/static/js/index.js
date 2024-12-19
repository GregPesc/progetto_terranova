document.querySelectorAll('.delete').forEach(button => {
    button.addEventListener('click', () => {
      button.closest('.notification').remove();
    });
  });

  // Clear form when they submit
  document.querySelector('form').addEventListener('submit', function() {
      setTimeout(() => {
          this.reset();
      }, 100);
  });

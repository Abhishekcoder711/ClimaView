document.addEventListener('DOMContentLoaded', () => {
  const observer = new MutationObserver(() => {
    const darkButton = document.getElementById("toggle-dark");
    if (darkButton) {
      darkButton.onclick = () => {
        document.body.classList.toggle("dark-mode");
      };
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
});


// static/js/about.js
//FAQ toggle function
function toggleFAQ(element) {
  const content = element.nextElementSibling;
  const plusSign = element.querySelector('span:last-child');

  if (content.classList.contains('hidden')) {
    content.classList.remove('hidden');
    plusSign.textContent = '-';
  } else {
    content.classList.add('hidden');
    plusSign.textContent = '+';
  }
}

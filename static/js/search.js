document.addEventListener('DOMContentLoaded', () => {
  const searchButton = document.getElementById('searchButton');
  const resultsContainer = document.getElementById('resultsContainer');
  const results = document.getElementById('results');

  // Add references for saved events container and div
  const savedEventsContainer = document.getElementById('savedEventsContainer');
  const savedEventsDiv = document.getElementById('savedEvents');

  const notification = document.createElement('div');
  notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg opacity-0 transition-opacity duration-300';
  document.body.appendChild(notification);

  const mockEvents = [
    { id: '1', title: 'Food Giveaway at Community Center', location: '123 Main St, Downtown', date: 'Today, 2:00 PM - 4:00 PM' },
    { id: '2', title: 'Networking Mixer with Complimentary Appetizers', location: 'Business Hub, 456 Market St', date: 'Tomorrow, 6:00 PM - 8:00 PM' },
    { id: '3', title: 'Free Pizza in Union Square', location: 'Union Square Park', date: 'Saturday, 12:00 PM - 2:00 PM' },
    { id: '4', title: 'Cultural Food Festival', location: 'City Convention Center', date: 'This Weekend, All Day' },
  ];

  function showNotification(message) {
    notification.textContent = message;
    notification.classList.remove('opacity-0');
    notification.classList.add('opacity-100');
    setTimeout(() => {
      notification.classList.remove('opacity-100');
      notification.classList.add('opacity-0');
    }, 1500);
  }

  function renderSavedEvents() {
    const savedIds = JSON.parse(localStorage.getItem('savedEvents') || '[]');
    const savedEvents = mockEvents.filter(event => savedIds.includes(event.id));

    if (savedEvents.length === 0) {
      savedEventsDiv.innerHTML = '<p class="text-gray-500">You have no saved events.</p>';
      savedEventsContainer.classList.add('hidden');
      return;
    }

    savedEventsContainer.classList.remove('hidden');
    savedEventsDiv.innerHTML = '';

    savedEvents.forEach(event => {
      const card = document.createElement('div');
      card.className = 'result-item bg-white rounded-lg shadow-md p-4 border-l-4 border-green-500';

      card.innerHTML = `
        <h3 class="font-semibold text-lg">${event.title}</h3>
        <div class="flex items-center text-gray-600 mt-1">
          <span class="mr-1">📍</span>
          <span>${event.location}</span>
        </div>
        <div class="flex items-center text-gray-600 mt-1">
          <span class="mr-1">🕒</span>
          <span>${event.date}</span>
        </div>
      `;

      savedEventsDiv.appendChild(card);
    });
  }

  function renderEvents(events) {
    results.innerHTML = '';
    const savedIds = JSON.parse(localStorage.getItem('savedEvents') || '[]');

    if (!events.length) {
      results.innerHTML = '<p class="text-gray-500">No events found matching your criteria.</p>';
      return;
    }

    events.forEach(event => {
      const isSaved = savedIds.includes(event.id);
      const eventEl = document.createElement('div');
      eventEl.className = 'result-item bg-white rounded-lg shadow-md p-4 border-l-4 border-orange-500';

      eventEl.innerHTML = `
        <h3 class="font-semibold text-lg">${event.title}</h3>
        <div class="flex items-center text-gray-600 mt-1">
          <span class="mr-1">📍</span>
          <span>${event.location}</span>
        </div>
        <div class="flex items-center text-gray-600 mt-1">
          <span class="mr-1">🕒</span>
          <span>${event.date}</span>
        </div>
        <button data-id="${event.id}" class="mt-3 px-3 py-1 rounded text-white font-semibold ${
          isSaved ? 'bg-green-600 hover:bg-green-700' : 'bg-orange-500 hover:bg-orange-600'
        }">
          ${isSaved ? 'Saved' : 'Save'}
        </button>
      `;

      results.appendChild(eventEl);
    });

    // Add event listeners for save buttons
    document.querySelectorAll('#results button').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-id');
        let saved = JSON.parse(localStorage.getItem('savedEvents') || '[]');

        if (saved.includes(id)) {
          saved = saved.filter(eid => eid !== id);
          btn.textContent = 'Save';
          btn.classList.remove('bg-green-600', 'hover:bg-green-700');
          btn.classList.add('bg-orange-500', 'hover:bg-orange-600');
          showNotification('Event removed from saved!');
        } else {
          saved.push(id);
          btn.textContent = 'Saved';
          btn.classList.remove('bg-orange-500', 'hover:bg-orange-600');
          btn.classList.add('bg-green-600', 'hover:bg-green-700');
          showNotification('Event saved!');
        }
        localStorage.setItem('savedEvents', JSON.stringify(saved));

        // Refresh saved events display after toggle
        renderSavedEvents();
      });
    });
  }

  searchButton.addEventListener('click', () => {
    const locationInput = document.getElementById('location').value.trim();
    const interestsInput = document.getElementById('interests').value.trim();


    if (!locationInput) {
      alert('Please enter a location to search for events.');
      return;
    }

    resultsContainer.classList.remove('hidden');
    renderEvents(mockEvents);
    renderSavedEvents(); // Show saved events too
  });


  renderSavedEvents();
});

document.addEventListener("DOMContentLoaded", () => {
  const searchButton = document.getElementById("searchButton");
  const locationInput = document.getElementById("location");
  const interestsInput = document.getElementById("interests");
  const resultsContainer = document.getElementById("resultsContainer");
  const results = document.getElementById("results");

  // Add references for saved events container and div
  const savedEventsContainer = document.getElementById("savedEventsContainer");
  const savedEventsDiv = document.getElementById("savedEvents");

  const notification = document.createElement("div");
  notification.className =
    "fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg opacity-0 transition-opacity duration-300";
  document.body.appendChild(notification);

  function showNotification(message, type = "success") {
    notification.textContent = message;
    notification.classList.remove("bg-green-500", "bg-red-500");
    if (type === "success") {
      notification.classList.add("bg-green-500");
    } else {
      notification.classList.add("bg-red-500");
    }
    notification.classList.remove("opacity-0");
    notification.classList.add("opacity-100");
    setTimeout(() => {
      notification.classList.remove("opacity-100");
      notification.classList.add("opacity-0");
    }, 3000);
  }

  async function fetchEvents(location, interests) {
    results.innerHTML =
      '<p class="text-gray-500 text-center">Searching for events...</p>'; // Loading message
    resultsContainer.classList.remove("hidden");

    try {
      const response = await fetch(
        `/api/events?location=${encodeURIComponent(
          location
        )}&interests=${encodeURIComponent(interests)}`
      );
      const data = await response.json();

      if (!response.ok) {
        showNotification(data.error || "Error fetching events.", "error");
        results.innerHTML = `<p class="text-gray-500 text-center">Error: ${
          data.error || "Failed to load events."
        }</p>`;
        return [];
      }

      if (data.events && data.events.length > 0) {
        return data.events;
      }
      return [];
    } catch (error) {
      console.error("Error fetching events:", error);
      return [];
    }
  }

  async function fetchSavedEvents() {
    try {
      const response = await fetch("/api/saved_events");
      const data = await response.json();

      if (!response.ok) {
        // If the response is not OK, something went wrong (e.g., not logged in)
        console.error("Error fetching saved events:", data.message);
        // savedEventsDiv.innerHTML = `<p class="text-red-500">Error loading saved events: ${data.message}</p>`;
        savedEventsContainer.classList.add("hidden"); // Hide if not logged in or error
        return [];
      }
      if (data.events && data.events.length > 0) {
        savedEventsContainer.classList.remove("hidden");
        return data.events;
      } else {
        savedEventsContainer.classList.add("hidden");
        return [];
      }
    } catch (error) {
      console.error("Network error fetching saved events:", error);
      savedEventsContainer.classList.add("hidden"); // Hide if network error
      return [];
    }
  }

  async function saveEvent(eventData) {
    try {
      const response = await fetch("/api/save_event", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(eventData),
      });
      const result = await response.json();

      if (response.ok) {
        showNotification(result.message, "success");
        return true;
      } else {
        showNotification(result.message || "Failed to save event.", "error");
        return false;
      }
    } catch (error) {
      return false;
    }
  }

  async function deleteEvent(globalId) {
    try {
      const response = await fetch("/api/delete_saved_event", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ global_id: globalId }),
      });
      const result = await response.json();

      if (response.ok) {
        showNotification(result.message, "success");
        return true;
      }
    } catch (error) {
      showNotification("Network error. Could not unsave event.", "error");
      return false;
    }
  }

  async function renderSavedEvents() {
    const savedEvents = await fetchSavedEvents();
    savedEventsDiv.innerHTML = "";

    if (savedEvents.length === 0) {
      savedEventsDiv.innerHTML =
        '<p class="text-gray-500">You have no saved events.</p>';
      savedEventsContainer.classList.add("hidden");
      return;
    }

    savedEventsContainer.classList.remove("hidden");

    savedEvents.forEach((event) => {
      const card = document.createElement("div");
      card.className =
        "result-item bg-white rounded-lg shadow-md p-4 border-l-4 border-green-500";

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
        <button data-global-id="${event.global_id}" class="unsave-btn px-3 py-1 rounded text-white font-semibold bg-red-500 hover:bg-red-600">
        Unsave
        </button>
      `;

      savedEventsDiv.appendChild(card);
    });

    document.querySelectorAll("#savedEvents .unsave-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const globalId = btn.getAttribute("data-global-id");
        const success = await deleteEvent(globalId);
        if (success) {
          renderSavedEvents();
        }
      });
    });
  }

  function renderEvents(events, savedEvents) {
    results.innerHTML = "";

    if (!events.length) {
      results.innerHTML =
        '<p class="text-gray-500">No events found matching your criteria.</p>';
      return;
    }

    const savedGlobalIds = new Set(savedEvents.map((e) => e.global_id));

    events.forEach((event) => {
      const isSaved = savedGlobalIds.has(event.globalId_id);
      const eventEl = document.createElement("div");
      eventEl.className =
        "result-item bg-white rounded-lg shadow-md p-4 border-l-4 border-orange-500";

      eventEl.innerHTML = `
        <div>
            <h3 class="font-semibold text-lg">${event.title}</h3>
            <div class="flex items-center text-gray-600 mt-1">
                <span class="mr-1">📍</span>
                <span>${event.location}</span>
            </div>
            <div class="flex items-center text-gray-600 mt-1">
                <span class="mr-1">🕒</span>
                <span>${event.date}</span>
            </div>
            ${
              event.url
                ? `<a href="${event.url}" target="_blank" class="text-blue-500 hover:underline text-sm mt-1 inline-block">More Info</a>`
                : ""
            }
        </div>
        <button 
            data-global-id="${event.global_id}" 
            data-source="${event.source}"
            data-title="${event.title}"
            data-date="${event.date}"
            data-location="${event.location}"
            data-url="${event.url}"
            class="save-toggle-btn mt-3 px-3 py-1 rounded text-white font-semibold ${
              isSaved
                ? "bg-green-600 hover:bg-green-700"
                : "bg-orange-500 hover:bg-orange-600"
            }">
            ${isSaved ? "Saved" : "Save"}
        </button>
            `;

      results.appendChild(eventEl);
    });

    // Add event listeners for save buttons
    document.querySelectorAll("#results button").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const globalId = btn.getAttribute("data-global-id");
        const source = btn.getAttribute("data-source");
        const title = btn.getAttribute("data-title");
        const date = btn.getAttribute("data-date");
        const location = btn.getAttribute("data-location");
        const url = btn.getAttribute("data-url");

        const eventData = {
          global_id: globalId,
          source,
          title,
          date,
          location,
          url,
        };

        let savedEventStatus = savedGlobalIds.has(globalId);

        if (savedEventStatus) {
          const success = await deleteEvent(globalId);
          if (success) {
            savedGlobalIds.delete(globalId);
            btn.textContent = "Save";
            btn.classList.remove("bg-green-600", "hover:bg-green-700");
            btn.classList.add("bg-orange-500", "hover:bg-orange-600");
            renderSavedEvents();
          }
        } else {
          const success = await saveEvent(eventData);
          if (success) {
            savedGlobalIds.add(globalId);
            btn.textContent = "Saved";
            btn.classList.remove("bg-orange-500", "hover:bg-orange-600");
            btn.classList.add("bg-green-600", "hover:bg-green-700");
            renderSavedEvents();
          }
        }
      });
    });
  }

  // --- Event Listeners and Initial Load ---

  searchButton.addEventListener("click", async () => {
    const location = locationInput.value.trim();
    const interests = interestsInput.value.trim();

    if (!location) {
      showNotification(
        "Please enter a location to search for events.",
        "error"
      );
      return;
    }

    const savedEventsForUser = await fetchSavedEvents();
    const searchResults = await fetchEvents(location, interests);
    renderEvents(searchResults, savedEventsForUser);
  });

  renderSavedEvents();
});

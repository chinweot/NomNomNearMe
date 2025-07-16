const sampleEvents = [
  {
    title: "Food Giveaway at Community Center",
    location: "123 Main St, Downtown",
    date: "Today, 2:00 PM - 4:00 PM",
  },
  {
    title: "Networking Mixer with Complimentary Appetizers",
    location: "Business Hub, 456 Market St",
    date: "Tomorrow, 6:00 PM - 8:00 PM",
  },
  {
    title: "Free Pizza in Union Square",
    location: "Union Square Park",
    date: "Saturday, 12:00 PM - 2:00 PM",
  },
  {
    title: "Cultural Food Festival",
    location: "City Convention Center",
    date: "This Weekend, All Day",
  },
];

function displayResults(events) {
  const resultsContainer = document.getElementById("results");
  resultsContainer.innerHTML = ""; // Clear previous results

  console.log(events);
  if (!events || events.length === 0) {
    resultsContainer.innerHTML =
      '<p class="text-gray-500">No events found matching your criteria.</p>';
    return;
  }

  events.forEach((event) => {
    const eventElement = document.createElement("div");
    eventElement.className =
      "result-item bg-white rounded-lg shadow-md p-4 border-l-4 border-orange-500";

    eventElement.innerHTML = `
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

    resultsContainer.appendChild(eventElement);
  });
}

async function fetchEventsFromAPI(location, interests) {
  const resultsContainerDiv = document.getElementById("resultsContainer");
  const resultsDiv = document.getElementById("results");

  resultsDiv.innerHTML = '<p class="text-gray-500">Searching for events...</p>';
  resultsContainerDiv.classList.remove("hidden");

  try {
    const apiUrl = `/api/events?location=${encodeURIComponent(
      location
    )}&interests=${encodeURIComponent(interests)}`;
    const response = await fetch(apiUrl);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        `HTTP error! Status: ${response.status} - ${
          errorData.error || "Unknown error"
        }`
      );
    }

    const data = await response.json();
    console.log("Data from Flask API:", data);
    displayResults(data);
  } catch (error) {
    console.error("Error fetching events:", error);
    resultsDiv.innerHTML = `<p class="text-red-500">Error: ${error.message}. Please check your location and try again.</p>`;
  }
}

document.getElementById("searchButton").addEventListener("click", () => {
  const locationInput = document.getElementById("location").value.trim();
  const interestsInput = document.getElementById("interests").value.trim();

  if (!locationInput) {
    alert("Please enter a location to search for events.");
    return;
  }
  fetchEventsFromAPI(locationInput, interestsInput);
});

document.addEventListener("DOMContentLoaded", () => {
  const defaultLocation =
    document.getElementById("location").value.trim() || "Aspen Hill, MD";
  const defaultInterests =
    document.getElementById("interests").value.trim() || "free food";
  fetchEventsFromAPI(defaultLocation, defaultInterests);
});

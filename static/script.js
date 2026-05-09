const showsContainer = document.getElementById("shows-container");
const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-button");
const yearFilter = document.getElementById("year-filter");
const genreFilter = document.getElementById("genre-filter");
const genreFilterGroup = document.getElementById("genre-filter-group");
const resetButton = document.getElementById("reset-button");
const ratingSort = document.getElementById("rating-sort");
const showCount = document.getElementById("show-count");

let allShows = [];
let genreNameById = new Map();
let expandedShowId = null;

const filters = {
	search: "",
	year: "all",
	genre: "all",
	ratingSortOrder: "default",
};

function renderShows(shows) {
	showCount.textContent = `Showing ${shows.length} show${shows.length === 1 ? "" : "s"}`;

	if (!Array.isArray(shows) || shows.length === 0) {
		showsContainer.innerHTML = '<p class="empty-state">No shows found.</p>';
		return;
	}

	showsContainer.innerHTML = shows
		.map((show) => {
			const title = show.title ?? "Untitled Show";
			const releaseYear = show.release_year ?? "Unknown year";
			const showId = show.show_id ?? "N/A";
			const genreName = genreNameById.get(String(show.genre_id)) ?? "Unknown genre";
			const description = show.description ?? "No description available.";
			const isExpanded = String(show.show_id) === String(expandedShowId);
			const imageUrl = show.image_url ?? "";
			const rating = show.rating != null ? `⭐ ${show.rating} / 10` : "Not available";
			const imageMarkup = imageUrl
				? `<img class="show-poster" src="${imageUrl}" alt="Poster for ${title}">`
				: `<div class="show-poster placeholder" aria-hidden="true"><span>No image</span></div>`;

			return `
				<article class="show-card ${isExpanded ? "is-expanded" : ""}" data-show-id="${showId}" tabindex="0" role="button" aria-expanded="${isExpanded}">
					${imageMarkup}
					<h2>${title}</h2>
					<p><span>ID:</span> ${showId}</p>
					<p><span>Release year:</span> ${releaseYear}</p>
					<p><span>Genre:</span> ${genreName}</p>
					<p><span>Rating:</span> ${rating}</p>
					<div class="show-description ${isExpanded ? "visible" : ""}">
						<p>${description}</p>
					</div>
					<p class="card-hint">${isExpanded ? "Click to hide description" : "Click to read description"}</p>
				</article>
			`;
		})
		.join("");

	showsContainer.querySelectorAll(".show-card").forEach((card) => {
		card.addEventListener("click", () => {
			const clickedId = card.dataset.showId;
			expandedShowId = expandedShowId === clickedId ? null : clickedId;
			updateDisplayedShows();
		});

		card.addEventListener("keydown", (event) => {
			if (event.key === "Enter" || event.key === " ") {
				event.preventDefault();
				const clickedId = card.dataset.showId;
				expandedShowId = expandedShowId === clickedId ? null : clickedId;
				updateDisplayedShows();
			}
		});
	});
}

function getFilteredShows() {
	const searchTerm = filters.search.toLowerCase();

	const filtered = allShows.filter((show) => {
		const title = (show.title ?? "").toLowerCase();
		const releaseYear = show.release_year == null ? "" : String(show.release_year);
		const genreName = show.genre_id == null ? "" : (genreNameById.get(String(show.genre_id)) ?? "").toLowerCase();

		const matchesSearch = !searchTerm || title.includes(searchTerm);
		const matchesYear = filters.year === "all" || releaseYear === filters.year;
		const matchesGenre = filters.genre === "all" || genreName === filters.genre;

		return matchesSearch && matchesYear && matchesGenre;
	});

	if (filters.ratingSortOrder === "default") {
		return filtered;
	}

	return [...filtered].sort((a, b) => {
		const rA = a.rating ?? null;
		const rB = b.rating ?? null;

		if (rA === null && rB === null) return 0;
		if (rA === null) return 1;
		if (rB === null) return -1;

		return filters.ratingSortOrder === "desc" ? rB - rA : rA - rB;
	});
}

function updateDisplayedShows() {
	renderShows(getFilteredShows());
}

function populateYearFilter(shows) {
	const years = [...new Set(shows.map((show) => show.release_year).filter((year) => year !== null && year !== undefined))].sort((a, b) => a - b);

	yearFilter.innerHTML = '<option value="all">All years</option>';
	for (const year of years) {
		const option = document.createElement("option");
		option.value = String(year);
		option.textContent = String(year);
		yearFilter.appendChild(option);
	}
}

function populateGenreFilter(genres) {
	if (!Array.isArray(genres) || genres.length === 0) {
		genreFilterGroup.style.display = "none";
		return;
	}

	genreNameById = new Map(
		genres
			.filter((genre) => genre.genre_id != null)
			.map((genre) => [String(genre.genre_id), genre.genre_name ?? "Unknown genre"])
	);

	const uniqueGenreNames = [];
	const seenGenreNames = new Set();
	for (const genre of genres) {
		const genreName = (genre.genre_name ?? "Unknown genre").trim();
		const normalizedName = genreName.toLowerCase();

		if (!seenGenreNames.has(normalizedName)) {
			seenGenreNames.add(normalizedName);
			uniqueGenreNames.push(genreName);
		}
	}

	genreFilter.innerHTML = '<option value="all">All genres</option>';
	for (const genreName of uniqueGenreNames) {
		const option = document.createElement("option");
		option.value = genreName.toLowerCase();
		option.textContent = genreName;
		genreFilter.appendChild(option);
	}

	genreFilter.disabled = false;
	genreFilterGroup.style.display = "flex";
}

async function fetchShows(url) {
	showsContainer.innerHTML = '<p class="empty-state">Loading shows...</p>';

	try {
		const response = await fetch(url);

		if (!response.ok) {
			throw new Error(`Request failed with status ${response.status}`);
		}

		const shows = await response.json();
		return shows;
	} catch (error) {
		showsContainer.innerHTML = `<p class="empty-state error">Could not load shows. ${error.message}</p>`;
		showCount.textContent = "Showing 0 shows";
		return [];
	}
}

async function loadAllShows() {
	const shows = await fetchShows("/shows");
	allShows = Array.isArray(shows) ? shows : [];
	populateYearFilter(allShows);
	updateDisplayedShows();
}

function applyFilters() {
	filters.search = searchInput.value.trim();
	filters.year = yearFilter.value;
	filters.genre = genreFilter.value;
	filters.ratingSortOrder = ratingSort.value;
	updateDisplayedShows();
}

function resetFilters() {
	searchInput.value = "";
	yearFilter.value = "all";
	if (genreFilter) {
		genreFilter.value = "all";
	}
	ratingSort.value = "default";
	filters.search = "";
	filters.year = "all";
	filters.genre = "all";
	filters.ratingSortOrder = "default";
	expandedShowId = null;
	updateDisplayedShows();
}

async function loadGenres() {
	try {
		const response = await fetch("/genres");

		if (!response.ok) {
			throw new Error(`Request failed with status ${response.status}`);
		}

		const genres = await response.json();
		populateGenreFilter(genres);
	} catch {
		genreFilterGroup.style.display = "none";
	}
}

searchButton.addEventListener("click", applyFilters);

yearFilter.addEventListener("change", applyFilters);

ratingSort.addEventListener("change", applyFilters);

genreFilter.addEventListener("change", applyFilters);

resetButton.addEventListener("click", resetFilters);

searchInput.addEventListener("keydown", (event) => {
	if (event.key === "Enter") {
		applyFilters();
	}
});

Promise.all([loadAllShows(), loadGenres()]).then(() => {
	updateDisplayedShows();
});

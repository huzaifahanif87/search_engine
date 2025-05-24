
let currentPage = 1;

document.getElementById('searchInput').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        const query = event.target.value.trim();
        if (!query) {
            alert('Please enter a search term');
            return;
        }
        fetchResults(query, currentPage);
    }
});
function fetchResults(query, page) {
    const startTime = performance.now();
    fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, page })
    })
        .then(response => response.json())
        .then(data => {
            const endTime = performance.now(); // Capture the end time
            const elapsedTime = ((endTime - startTime) / 1000).toFixed(4); // Calculate elapsed time in seconds
            if (data.status === 'success') {
                displayResults(data.results);
                updatePaginationControls(data.total_pages, data.current_page);
                document.getElementById('tabsNavbar').classList.remove('hidden');
                document.getElementById('paginationControls').classList.remove('hidden');
                document.getElementById('paginationControls').classList.add('flex');
                displayQueryTime(elapsedTime);
            } else if (data.status === 'no_matches') {
                displayNoMatchesMessage();
                updatePaginationControls(0, 0); // Hide pagination for no matches
            }
        })
        .catch(error => {
            console.error('Error during fetch:', error);
            alert('An error occurred. Please try again later.');
        });
}
function displayNoMatchesMessage() {
    const documentsList = document.getElementById('documentsList');
    const imagesGrid = document.getElementById('imagesGrid');

    // Clear previous results
    documentsList.innerHTML = '';
    imagesGrid.innerHTML = '';

    // Add a friendly no results message
    documentsList.innerHTML = `
        <li class="no-results-message">
            <strong>Looks like there are no great matches for your query.</strong>
            <p>Kindly check your spelling or try different keywords for better results.</p>
        </li>
    `;
    imagesGrid.innerHTML = `
        no images too
    `;
}



// Tab switching for the navbar
document.getElementById('documentsTab').addEventListener('click', function () {
    toggleTabs('documents');
});

document.getElementById('imagesTab').addEventListener('click', function () {
    toggleTabs('images');
});

function toggleTabs(activeTab) {
    const documentsList = document.getElementById('documentsList');
    const imagesGrid = document.getElementById('imagesGrid');
    const documentsTab = document.getElementById('documentsTab');
    const imagesTab = document.getElementById('imagesTab');

    if (activeTab === 'documents') {
        documentsList.style.display = 'block';
        imagesGrid.style.display = 'none';
        documentsTab.classList.add('active');
        imagesTab.classList.remove('active');
    } else {
        imagesGrid.style.display = 'grid';
        documentsList.style.display = 'none';
        imagesTab.classList.add('active');
        documentsTab.classList.remove('active');
    }
}

function displayResults(results) {
    const documentsList = document.getElementById('documentsList');
    const imagesGrid = document.getElementById('imagesGrid');

    // Clear previous results
    documentsList.innerHTML = '';
    imagesGrid.innerHTML = '';

    if (!results || results.length === 0) {
        // Display a "No results found" message
        documentsList.innerHTML = `
            <li class="no-results-message">
                <strong>No results found</strong>
                <p>Try using different keywords or check your spelling.</p>
            </li>
        `;
        imagesGrid.innerHTML = `
            <div class="no-results-message">
                <strong>No images found</strong>
                <p>Try refining your search query for better results.</p>
            </div>
        `;
        return;
    }

    let imageCounter = 0; // Counter to track the image pattern

    results.forEach((result) => {
        const { title, url, description, source, image_url } = result.details;

        // Document results
        if (title) {
            const li = document.createElement('li');
            li.innerHTML = `
                <strong><a href="${url}" target="_blank">${title}</a></strong>
                <br>${description || 'No description available'}
                <br><small>Source: ${source || 'Unknown'}</small>
            `;
            documentsList.appendChild(li);
        }

        // Image results
        if (image_url) {
            const imgDiv = document.createElement('div');
            imgDiv.classList.add('image-item');

            // Apply the 'large' class based on the pattern
            if (imageCounter % 3 === 0) {
                imgDiv.classList.add('large');
            }

            imgDiv.innerHTML = `
                <a href="${url || '#'}" target="_blank" style="text-decoration: none; color: inherit;">
                    <img src="${image_url}" alt="${title}" title="${title}">
                    <p>${title || 'Untitled'}</p>
                </a>
            `;
            imagesGrid.appendChild(imgDiv);

            imageCounter++;
        }
    });
}



function displayQueryTime(elapsedTime) {
    const queryTimeElement = document.getElementById('queryTime');

    // Update the content to show the elapsed time
    queryTimeElement.textContent = `Search completed in ${elapsedTime} seconds.`;
    queryTimeElement.style.display = 'block'; // Ensure it's visible
}

function updatePaginationControls(totalPages, currentPage) {
    const pageInfo = document.getElementById('pageInfo');
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');

    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;

    prevPage.style.display = currentPage > 1 ? 'inline-block' : 'none';
    nextPage.style.display = currentPage < totalPages ? 'inline-block' : 'none';

    prevPage.onclick = () => changePage('prev');
    nextPage.onclick = () => changePage('next');
}

function changePage(direction) {
    const query = document.getElementById('searchInput').value.trim();
    if (direction === 'prev' && currentPage > 1) currentPage--;
    if (direction === 'next') currentPage++;
    if (query) fetchResults(query, currentPage);
}

// Theme switcher
document.getElementById('themeSwitcher').addEventListener('click', function () {
    const body = document.body;
    const isDark = body.classList.toggle('dark-theme');
    body.classList.toggle('light-theme', !isDark);
    this.textContent = isDark ? '🌞' : '🌙';
});


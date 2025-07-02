document.getElementById('searchButton')
.addEventListener('click', function() {
    const searchTerm = document.getElementById('searchInput').value;
    if (searchTerm.trim() !== '') {
        const apiUrl = `/search?search_query=${encodeURIComponent(searchTerm)}`;
        fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '';
            data.forEach(imagePath => {
                const img = document.createElement('img');
                img.src = `/${imagePath}`;
                img.style.maxWidth = '200px';
                img.style.margin = '10px';
                resultsDiv.appendChild(img);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('results').innerHTML = 'Error loading results';
        });
    }
});
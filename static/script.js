document.addEventListener("DOMContentLoaded", function () {
    // Create a container for the dropdown (we'll position this next to the input)
    const dropdownContainer = document.getElementById('dropdown-container');
    dropdownContainer.style.position = 'absolute';
    dropdownContainer.style.zIndex = '1000';  // Ensure it's above other content
    dropdownContainer.style.backgroundColor = 'white';

    document.querySelectorAll('input').forEach(input => {
        // Event listener to handle input and fetch suggestions
        input.addEventListener('input', async function () {
            const query = input.value.trim();

            if (query.length >= 2) { // Only trigger when query length is >= 2
                try {
                    const response = await fetch(`http://127.0.0.1:5000/search?query=${query}`);
                    const suggestions = await response.json();

                    // Clear previous suggestions
                    dropdownContainer.innerHTML = '';

                    if (suggestions.length > 0) {
                        // Create a dropdown list with the suggestions
                        suggestions.forEach(name => {
                            const item = document.createElement('div');
                            item.textContent = name;
                            item.style.padding = '8px';
                            item.style.cursor = 'pointer';
                            item.style.borderBottom = '1px solid #ccc';

                            // Highlight the item on hover
                            item.addEventListener('mouseover', () => {
                                item.style.backgroundColor = '#f0f0f0';
                            });
                            item.addEventListener('mouseout', () => {
                                item.style.backgroundColor = 'white';
                            });

                            // When an item is clicked, autofill the input field and hide the dropdown
                            item.addEventListener('click', function () {
                                input.value = name;
                                dropdownContainer.style.display = 'none';  // Hide the dropdown after selection

                                // Trigger input validation after selection
                                const rowAttr = input.dataset.row;
                                const colAttr = input.dataset.col;
                                fetch('http://127.0.0.1:5000/validate', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({
                                        row_attr: rowAttr,
                                        col_attr: colAttr,
                                        champion_name: name
                                    })
                                })
                                .then(response => response.json())
                                .then(result => {
                                    if (result.valid) {
                                        input.style.backgroundColor = 'lightgreen';
                                    } else {
                                        input.style.backgroundColor = 'lightcoral';
                                    }
                                })
                                .catch(error => {
                                    console.error('Error validating input:', error);
                                    input.style.backgroundColor = 'lightcoral';
                                });
                            });

                            dropdownContainer.appendChild(item);
                        });

                        // Position the dropdown directly under the input field
                        const rect = input.getBoundingClientRect();
                        dropdownContainer.style.left = `${rect.left + window.scrollX}px`;
                        dropdownContainer.style.top = `${rect.bottom + window.scrollY}px`;
                        dropdownContainer.style.width = `${rect.width}px`;
                        dropdownContainer.style.display = 'block';
                    }
                } catch (error) {
                    console.error('Error fetching suggestions:', error);
                }
            } else {
                dropdownContainer.style.display = 'none'; // Hide dropdown if query length is less than 2
            }
        });

        // Hide the dropdown when clicking outside the dropdown or input field
        document.addEventListener('click', function (event) {
            if (!input.contains(event.target) && !dropdownContainer.contains(event.target)) {
                dropdownContainer.style.display = 'none';  // Hide dropdown if clicked outside
            }
        });
    });
});

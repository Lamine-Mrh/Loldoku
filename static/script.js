document.addEventListener("DOMContentLoaded", function () {

    window.onload = function() {
        const modal = document.getElementById('welcome-modal');
        const overlay = document.getElementById('overlay');
        const startButton = document.getElementById('start-button');
    
        // Display the modal and overlay
        modal.style.display = 'block';
        overlay.style.display = 'block';
    
        // Hide the modal and overlay when "Let's go" button is clicked
        startButton.addEventListener('click', function() {
            modal.style.display = 'none';
            overlay.style.display = 'none';
        });
    };
    const maxTries = 9;
    let remainingTries = maxTries;

    // Variables for scoring and streak
    let score = 0;
    let streak = 0;
    const startTime = Date.now();
    let highScore = localStorage.getItem("highScore") || 0;

    // Set to keep track of selected champions
    const selectedChampions = new Set();

    // Display remaining tries
    const triesDisplay = document.createElement("div");
    triesDisplay.id = "tries-display";
    triesDisplay.textContent = `Mana: ${remainingTries}/9`;
    document.body.insertBefore(triesDisplay, document.querySelector("table"));

    // Display score, streak, and high score
    const scoreDisplay = document.createElement("div");
    scoreDisplay.id = "score-display";
    scoreDisplay.textContent = `Score: ${score} | Streak: ${streak} | High Score: ${highScore}`;
    document.body.insertBefore(scoreDisplay, triesDisplay);

    const dropdownContainer = document.getElementById("dropdown-container");
    dropdownContainer.style.position = "absolute";
    dropdownContainer.style.zIndex = "1000";
    dropdownContainer.style.backgroundColor = "white";

    const attributes = {
        region: ["Demacia", "Freljord", "Ionia", "Piltover", "Zaun", "Noxus", "Ixtal", "Shurima", "Bilgewater", "Shadow Isles", "Targon", "Bandle City", "Runeterra", "The Void"],
        role: ["Top", "Mid", "Bot", "Support", "Jungle"],
        champion_type: ["Tank", "Fighter", "Mage", "Marksman", "Slayer", "Controller","Specialist"],
        subclass: ["Vanguard", "Warden", "Artillery", "Burst", "Battlemage", "Diver","Juggernaut","Marksman","Assassin","Skirmisher","Enchanter","Catcher"],
        specie: ["Human", "Yordle", "Voidborn", "Golem", "Darkin", "Mutant","Aspect","Ascended","Dragon","Elemental","Spirit","Specter"],
        gender: ["Male", "Female", "Genderless"],
        resource_type: ["Mana", "Energy", "Manaless", "Other"],
        range: ["Melee", "Ranged","Both"],
        release_year: [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022,2023,2024], // You can add more years here
    };
    
    // Helper function to shuffle arrays
    function shuffle(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]]; // Swap elements
        }
    }

    function getKeyFromValue(obj, value) {
        console.log("Looking for value:", value);
        for (const key in obj) {
            if (Array.isArray(obj[key])) {
                const normalizedValue = typeof obj[key][0] === "number" ? Number(value) : String(value); // Normalize champion_type
                if (obj[key].includes(normalizedValue)) {
                    console.log(`Found match for ${value} in key: ${key}`);
                    return key;
                }
            } else if (obj[key] === value) {
                console.log(`Found match for ${value} in key: ${key}`);
                return key;
            }
        }
        console.log(`No match found for value: ${value}`);
        return null; // If value is not found
    }
    
    // Helper function to get a random attribute from the list
    function getRandomAttribute(attributeList) {
        return attributeList[Math.floor(Math.random() * attributeList.length)];
    }

    // Shuffle arrays for more randomization
    shuffle(attributes.region);
    shuffle(attributes.role);
    shuffle(attributes.champion_type);
    shuffle(attributes.subclass);
    shuffle(attributes.specie);
    shuffle(attributes.gender);
    shuffle(attributes.resource_type);
    shuffle(attributes.range);
    shuffle(attributes.release_year);

    // Create the table dynamically
    const gameTable = document.getElementById('game-table');
    const columnHeaders = document.getElementById('column-headers');
    const rowsContainer = document.getElementById('rows');

    // Randomize the row attributes (e.g., region, class, etc.)
    const TheAttributes = {
        region: getRandomAttribute(attributes.region),
        role: getRandomAttribute(attributes.role),
        champion_type: getRandomAttribute(attributes.champion_type),
        subclass: getRandomAttribute(attributes.subclass),
        specie: getRandomAttribute(attributes.specie),
        gender: getRandomAttribute(attributes.gender),
        range: getRandomAttribute(attributes.range),
        release_year: String(getRandomAttribute(attributes.release_year)),
        resource_type: getRandomAttribute(attributes.resource_type),
    };

    // Columns: Randomize the attributes to be used as columns
    const columnAttributes = [
        'region', 'role', 'champion_type', 'subclass', 'specie', 'gender', 'range', 'release_year', 'resource_type'
    ];

    // Shuffle column attributes
    shuffle(columnAttributes);

    // Select the first 3 attributes after shuffle
    const selectedColumns = columnAttributes.slice(0, 3);

    // Create column headers dynamically
    selectedColumns.forEach(attr => {
        const th = document.createElement('th');
        const randomAttributeValue = TheAttributes[attr];
        th.textContent = randomAttributeValue;
        columnHeaders.appendChild(th);
    });


    // Create rows dynamically
    const numRows = 3; // Adjust the number of rows you want
    for (let i = 0; i < numRows; i++) {
        const row = document.createElement('tr');
        const randomAttributeKey = Object.keys(TheAttributes)[Math.floor(Math.random() * Object.keys(TheAttributes).length)];
        const randomAttributeValue = TheAttributes[randomAttributeKey];
        const th = document.createElement('th');
        th.textContent = `${randomAttributeValue}`;
        row.appendChild(th);

        // Create a cell for each column
        selectedColumns.forEach(attr => {
            const td = document.createElement('td');
            const input = document.createElement('input');
            input.setAttribute('data-row', randomAttributeValue);  // Store the row attribute for validation
            input.setAttribute('data-col', TheAttributes[attr]);  // Store the column attribute for validation
            td.appendChild(input);
            row.appendChild(td);
        });

        rowsContainer.appendChild(row);
    }

    document.querySelectorAll("input").forEach((input) => {
        input.dataset.validated = "false"; // Track if the cell is validated

        input.addEventListener("input", async function () {
            const query = input.value.trim();

            if (query.length >= 2) {
                try {
                    const response = await fetch(`http://127.0.0.1:5000/search?query=${query}`);
                    let suggestions = await response.json();

                    // Filter out already selected champions
                    suggestions = suggestions.filter((name) => !selectedChampions.has(name));

                    dropdownContainer.innerHTML = "";
                    if (suggestions.length > 0) {
                        const sortedSuggestions = suggestions.sort((a, b) => {
                            if (a.toLowerCase().startsWith(query.toLowerCase()) && !b.toLowerCase().startsWith(query.toLowerCase())) {
                                return -1;
                            } else if (!a.toLowerCase().startsWith(query.toLowerCase()) && b.toLowerCase().startsWith(query.toLowerCase())) {
                                return 1;
                            }
                            return 0;
                        });

                        sortedSuggestions.forEach((name, index) => {
                            const item = document.createElement("div");
                            item.textContent = name;
                            item.style.padding = "8px";
                            item.style.cursor = "pointer";
                            item.style.borderBottom = "1px solid #ccc";

                            item.addEventListener("mouseover", () => {
                                item.style.backgroundColor = "#f0f0f0";
                            });
                            item.addEventListener("mouseout", () => {
                                item.style.backgroundColor = "white";
                            });

                            item.addEventListener("click", async function () {
                                input.value = name;
                                dropdownContainer.style.display = "none";

                                const rowAttr = input.dataset.row;
                                const colAttr = input.dataset.col;

                                // Validate input
                                const champRow = getKeyFromValue(attributes,rowAttr);
                                const champCol = getKeyFromValue(attributes,colAttr);

                                input.value = name;
                                dropdownContainer.style.display = "none";

                                const t = "http://127.0.0.1:5000/getChampData?name="

                                console.log(t + name)

                                const champDataResponse = await fetch(t + name);
                                const champData = await champDataResponse.json();

                                const champRowF = champData[champRow];
                                const champColF = champData[champCol];

                                console.log(champData)
                                console.log(getKeyFromValue(TheAttributes,rowAttr)); // Should return the correct key.
                                console.log(getKeyFromValue(TheAttributes,colAttr)); // Should return the correct key.

                                console.log(champRow,champCol)
                                console.log(champRowF,champColF)
                                console.log(rowAttr,colAttr)

                                const validationResponse = await fetch("http://127.0.0.1:5000/validate", {
                                    method: "POST",
                                    headers: { "Content-Type": "application/json" },
                                    body: JSON.stringify({
                                        row_attr: champRowF,
                                        col_attr: champColF,
                                        row_a: champRow,
                                        col_a:champCol,
                                        champion_name: name,
                                        expected_value_row: rowAttr, // Get the row attribute value for comparison
                                        expected_value_col: colAttr,
                                    }),
                                });

                                const result = await validationResponse.json();

                                if (result.valid) {
                                    input.style.backgroundColor = "lightgreen"; // Mark as correct
                                    input.disabled = true; // Disable input
                                    input.dataset.validated = "true"; // Mark as validated
                                    selectedChampions.add(name); // Add to selected champions
                                    score += 10 + streak * 5; // Add score with streak multiplier
                                    streak++; // Increase streak
                                } else {
                                    input.style.backgroundColor = "lightcoral"; // Mark as incorrect
                                    input.value = ""; // Clear the input
                                    score = Math.max(0, score - 5); // Deduct points for incorrect answer
                                    streak = 0; // Reset streak
                                }

                                // Deduct one try per selection
                                remainingTries--;
                                triesDisplay.textContent = `Mana: ${remainingTries}/9`;
                                scoreDisplay.textContent = `Score: ${score} | Streak: ${streak} | High Score: ${highScore}`;

                                // Check game state
                                checkGameState();
                            });
                            dropdownContainer.appendChild(item);
                        });

                        const rect = input.getBoundingClientRect();
                        dropdownContainer.style.left = `${rect.left + window.scrollX}px`;
                        dropdownContainer.style.top = `${rect.bottom + window.scrollY}px`;
                        dropdownContainer.style.width = `${rect.width}px`;
                        dropdownContainer.style.display = "block";
                    }
                } catch (error) {
                    console.error("Error fetching suggestions:", error);
                }
            } else {
                dropdownContainer.style.display = "none";
            }
        });

        // Listen for Enter key press to select the first suggestion
        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter" && dropdownContainer.children.length > 0) {
                const firstSuggestion = dropdownContainer.children[0];
                firstSuggestion.click();
            }
        });

        document.addEventListener("click", function (event) {
            if (!input.contains(event.target) && !dropdownContainer.contains(event.target)) {
                dropdownContainer.style.display = "none";
            }
        });
    });

    function checkGameState() {
        const inputs = document.querySelectorAll("input");
        const allValidated = Array.from(inputs).every((input) => input.dataset.validated === "true");

        if (remainingTries <= 0) {
            const elapsedTime = Math.floor((Date.now() - startTime) / 1000); // Time in seconds
            const timePenalty = Math.floor(elapsedTime / 10); // Deduct 1 point per 10 seconds
            score = Math.max(0, score - timePenalty); // Apply time-based penalty

            if (score > highScore) {
                highScore = score; // Update high score
                localStorage.setItem("highScore", highScore);
            }

            // Create a result container
            const resultContainer = document.createElement("div");
            resultContainer.id = "result-container";
            resultContainer.style.position = "fixed";
            resultContainer.style.top = "50%";
            resultContainer.style.left = "50%";
            resultContainer.style.transform = "translate(-50%, -50%)";
            resultContainer.style.padding = "20px";
            resultContainer.style.backgroundColor = "#fff";
            resultContainer.style.border = "2px solid #ccc";
            resultContainer.style.zIndex = "2000";
            resultContainer.style.boxShadow = "0 4px 8px rgba(0,0,0,0.1)";
            resultContainer.style.textAlign = "center";
            resultContainer.style.fontSize = "20px";
            resultContainer.style.color = "#333";

            // Darken the background
            const overlay = document.createElement("div");
            overlay.style.position = "fixed";
            overlay.style.top = "0";
            overlay.style.left = "0";
            overlay.style.width = "100%";
            overlay.style.height = "100%";
            overlay.style.backgroundColor = "rgba(0, 0, 0, 0.6)";
            overlay.style.zIndex = "1000";
            document.body.appendChild(overlay);

            const resultMessage = document.createElement("p");
            resultMessage.textContent = allValidated
                ? `Victory! You filled all cells correctly!\nFinal Score: ${score}\nHigh Score: ${highScore}` 
                : `Defeat! You ran out of tries.\nFinal Score: ${score}\nHigh Score: ${highScore}`;
            resultContainer.appendChild(resultMessage);

            const proceedButton = document.createElement("button");
            proceedButton.textContent = "Proceed";
            proceedButton.style.marginTop = "20px";
            proceedButton.style.padding = "10px 20px";
            proceedButton.style.fontSize = "16px";
            proceedButton.style.cursor = "pointer";

            proceedButton.addEventListener("click", function () {
                resultContainer.remove();
                overlay.remove();
            });

            resultContainer.appendChild(proceedButton);
            document.body.appendChild(resultContainer);

            // Disable all inputs when the game ends
            inputs.forEach((input) => {
                input.disabled = true;
            });

            // Stop further actions (no reset here).
            return;
        }
    }
});

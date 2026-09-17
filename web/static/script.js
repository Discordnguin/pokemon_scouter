let tourCount = 0;

function addTour() {
    const container = document.getElementById('toursContainer');
    const tourId = tourCount++;
    
    const tourCard = document.createElement('div');
    tourCard.className = 'tour-card';
    tourCard.id = `tour-${tourId}`;
    
    tourCard.innerHTML = `
        <button type="button" class="remove-tour-btn" onclick="removeTour(${tourId})">Remove</button>
        <label for="tourName-${tourId}">Tour Name:</label>
        <input type="text" id="tourName-${tourId}" name="tourName" placeholder="e.g., Masters, RCoP, OUPL" required>
        
        <label for="replays-${tourId}">Replay URLs (one per line):</label>
        <textarea id="replays-${tourId}" name="replays" placeholder="Paste replay URLs here, one per line" required></textarea>
    `;
    
    container.appendChild(tourCard);
}

function removeTour(tourId) {
    const tourCard = document.getElementById(`tour-${tourId}`);
    if (tourCard) {
        tourCard.remove();
    }
}

document.getElementById('addTourBtn').addEventListener('click', function(e) {
    e.preventDefault();
    addTour();
});

document.getElementById('scoutForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Hide previous results
    document.getElementById('outputSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    
    try {
        // Collect form data
        const usernames = document.getElementById('usernames').value;
        const tier = document.getElementById('tier').value;
        
        const tours = [];
        document.querySelectorAll('.tour-card').forEach(card => {
            const inputs = card.querySelectorAll('input[name="tourName"]');
            const textareas = card.querySelectorAll('textarea[name="replays"]');
            
            if (inputs.length > 0 && textareas.length > 0) {
                tours.push({
                    name: inputs[0].value,
                    replays: textareas[0].value
                });
            }
        });
        
        if (tours.length === 0) {
            throw new Error('Please add at least one tour');
        }
        
        // Send request to backend
        const response = await fetch('/api/generate-scouts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                usernames: usernames,
                tier: tier,
                tours: tours
            })
        });
        
        const data = await response.json();
        
        document.getElementById('loading').style.display = 'none';
        
        if (response.ok && data.status === 'success') {
            const resultData = data.output;

            // 1. Build the Visual UI
            const visualContainer = document.getElementById('visualOutput');
            visualContainer.innerHTML = ''; // Clear previous scouts
            
            resultData.teams.forEach(team => {
                const teamBox = document.createElement('div');
                teamBox.className = 'team-box';
                
                const headerDiv = document.createElement('div');
                headerDiv.className = 'team-header';
                headerDiv.innerHTML = team.header.replace(/\]\s(.*?)\s\(/, '] <strong>$1</strong> (');
                
                const spritesDiv = document.createElement('div');
                spritesDiv.className = 'team-sprites';
                
                team.mons.forEach(mon => {
                    // Get artwork sprite URL
                    const spriteUrl = getIconStyle(mon);
                    
                    const img = document.createElement('img');
                    img.className = 'picon-img';
                    img.src = spriteUrl;
                    img.alt = mon;
                    img.title = mon;
                    img.style.width = '80px';
                    img.style.height = '80px';
                    img.style.imageRendering = 'pixelated';
                    
                    // Fallback if image fails to load
                    img.onerror = function() {
                        this.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><rect fill="%23ddd" width="80" height="80"/><text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="10" fill="%23999" font-weight="bold">?</text></svg>';
                    };
                    
                    spritesDiv.appendChild(img);
                });
                
                teamBox.appendChild(headerDiv);
                teamBox.appendChild(spritesDiv);
                visualContainer.appendChild(teamBox);
            });

            // 2. Insert the Raw Text Importable
            document.getElementById('output').textContent = resultData.raw_text;
            document.getElementById('outputSection').style.display = 'block';
            
            window.lastOutput = resultData.raw_text;
        } else {
            throw new Error(data.message || 'Unknown error');
        }
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('errorMessage').textContent = error.message;
        document.getElementById('errorSection').style.display = 'block';
    }
});

document.getElementById('copyBtn').addEventListener('click', function() {
    if (window.lastOutput) {
        navigator.clipboard.writeText(window.lastOutput).then(function() {
            const btn = document.getElementById('copyBtn');
            const originalText = btn.textContent;
            btn.textContent = 'Copied!';
            btn.style.background = '#28a745';
            setTimeout(function() {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 2000);
        }).catch(function(err) {
            alert('Failed to copy: ' + err);
        });
    }
});

document.getElementById('downloadBtn').addEventListener('click', function() {
    if (window.lastOutput) {
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(window.lastOutput));
        element.setAttribute('download', 'scouts_output.txt');
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }
});

// Initialize with one tour field
addTour();

// Test function to display sample teams (for debugging sprite rendering)
function testSpriteRendering() {
    const testData = {
        status: 'success',
        output: {
            raw_text: 'Scizor-Mega (Scizor) (Scizor-Mega) @ Choice Band\nAbility: Technician\nEVs: 248 HP / 8 Atk / 252 SpD\nAdamant Nature\n- Bullet Punch\n- Superpower\n- X-Scissor\n- Sword Dance',
            teams: [
                {
                    header: '[1] testuser (gen7ou)',
                    mons: ['Scizor-Mega', 'Heatran', 'Kyurem-Black', 'Tornadus-Therian', 'Tapu Koko', 'Gastrodon-East']
                },
                {
                    header: '[2] testuser (gen7ou)',
                    mons: ['Medicham-Mega', 'Landorus-Therian', 'Clefable', 'Greninja', 'Jirachi', 'Rotom-Wash']
                }
            ]
        }
    };

    // Display output
    const visualContainer = document.getElementById('visualOutput');
    visualContainer.innerHTML = '';
    
    testData.output.teams.forEach(team => {
        const teamBox = document.createElement('div');
        teamBox.className = 'team-box';
        
        const headerDiv = document.createElement('div');
        headerDiv.className = 'team-header';
        headerDiv.textContent = team.header;
        
        const spritesDiv = document.createElement('div');
        spritesDiv.className = 'team-sprites';
        
        team.mons.forEach(mon => {
            // Use Showdown's artwork sprite URL
            const spriteUrl = getIconStyle(mon);
            
            const img = document.createElement('img');
            img.className = 'picon-img';
            img.src = spriteUrl;
            img.alt = mon;
            img.title = mon;
            img.style.width = '80px';
            img.style.height = '80px';
            img.style.imageRendering = 'pixelated';
            
            // Fallback if image fails to load
            img.onerror = function() {
                this.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><rect fill="%23ddd" width="80" height="80"/><text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="10" fill="%23999" font-weight="bold">?</text></svg>';
            };
            
            spritesDiv.appendChild(img);
        });
        
        teamBox.appendChild(headerDiv);
        teamBox.appendChild(spritesDiv);
        visualContainer.appendChild(teamBox);
    });

    document.getElementById('output').textContent = testData.output.raw_text;
    document.getElementById('outputSection').style.display = 'block';
}

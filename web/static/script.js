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
            // Show output
            document.getElementById('output').textContent = data.output;
            document.getElementById('outputSection').style.display = 'block';
            
            // Store output for download
            window.lastOutput = data.output;
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

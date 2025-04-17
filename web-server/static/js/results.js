const questionId = document.getElementById('question-id').value;
let resultsChart = null;

document.addEventListener('DOMContentLoaded', function() {
    loadResults();
    setupWebSocket();
});

async function loadResults() {
    try {

        const response = await fetch(`/api/results/${questionId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch results');
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Error loading results:', error);
        document.getElementById('summary-container').innerHTML = 
            '<div class="alert alert-danger">Failed to load results. Please try again.</div>';
        document.getElementById('votes-container').innerHTML = 
            '<div class="alert alert-danger">Failed to load results. Please try again.</div>';
    }
}

function displayResults(data) {
    // Display summary
    const summaryHTML = data.summary.map(item => 
        `<div class="d-flex justify-content-between align-items-center mb-2">
            <strong>${item.vote}:</strong> <span>${item.count} vote(s)</span>
         </div>`
    ).join('');
    
    document.getElementById('summary-container').innerHTML = summaryHTML || '<p>No votes yet</p>';
    
    // Display individual votes
    const votesHTML = data.votes.length ? 
        `<table class="table table-striped">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Vote</th>
                </tr>
            </thead>
            <tbody>
                ${data.votes.map(vote => 
                    `<tr>
                        <td>${vote.name}</td>
                        <td>${vote.vote}</td>
                    </tr>`
                ).join('')}
            </tbody>
        </table>` : 
        '<p>No votes yet</p>';
    
    document.getElementById('votes-container').innerHTML = votesHTML;
    
    // Create or update chart
    if (data.summary.length > 0) {
        updateChart(data.summary);
    }
}

function updateChart(summary) {
    const labels = summary.map(item => item.vote);
    const counts = summary.map(item => item.count);
    const colors = generateColors(labels.length);
    
    const ctx = document.getElementById('resultsChart').getContext('2d');
    
    if (resultsChart) {
        resultsChart.data.labels = labels;
        resultsChart.data.datasets[0].data = counts;
        resultsChart.data.datasets[0].backgroundColor = colors;
        resultsChart.update();
    } else {
        resultsChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: colors
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

function setupWebSocket() {
    // Use secure WebSocket if the page is loaded over HTTPS
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    
    ws.onopen = function() {
        console.log('WebSocket connection established');
    };
    
    ws.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            
            // Only update if this message is for our question
            if (data.question_id && data.question_id == questionId) {
                console.log('Received update for this question');
                loadResults(); // Reload results when a new vote comes in
            }
        } catch (e) {
            console.error('Error processing WebSocket message:', e);
        }
    };
    
    ws.onclose = function(event) {
        console.log('WebSocket connection closed', event.code, event.reason);
        // Try to reconnect in 5 seconds
        setTimeout(setupWebSocket, 5000);
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        // Don't close here - let the onclose handle reconnection
    };
}

function generateColors(count) {
    const baseColors = [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(199, 199, 199, 0.7)'
    ];
    
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    
    return colors;
}

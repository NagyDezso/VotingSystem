let resultsChart = null;

document.addEventListener('DOMContentLoaded', function() {
    loadQuestions();
    
    // Set up modal event handlers
    const resultsModal = document.getElementById('resultsModal');
    resultsModal.addEventListener('hidden.bs.modal', function () {
        if (resultsChart) {
            resultsChart.destroy();
            resultsChart = null;
        }
    });
});

async function loadQuestions() {
    try {
        const response = await fetch('/questions?active_only=false');
        const questions = await response.json();
        
        const container = document.getElementById('questions-container');
        
        if (questions.length === 0) {
            container.innerHTML = '<div class="col-12 text-center p-5">No questions found.</div>';
            return;
        }
        
        container.innerHTML = questions.map(q => `
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header ${q.active ? 'bg-success bg-opacity-25' : 'bg-secondary bg-opacity-25'}">
                        <span class="badge ${q.active ? 'bg-success' : 'bg-secondary'} me-2">
                            ${q.active ? 'Active' : 'Inactive'}
                        </span>
                        Question ID: ${q.id}
                    </div>
                    <div class="card-body">
                        <h5 class="card-title">${q.title}</h5>
                        <p class="card-text">${q.description || 'No description'}</p>
                        <p class="card-text"><small>Options: ${q.options.join(', ')}</small></p>
                    </div>
                    <div class="card-footer d-flex justify-content-between">
                        <button class="btn btn-sm btn-primary" onclick="viewResults(${q.id})">View Results</button>
                        <a href="/question/${q.id}" class="btn btn-sm btn-outline-primary">Vote Page</a>
                    </div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading questions:', error);
        document.getElementById('questions-container').innerHTML = 
            '<div class="col-12 text-center p-5 text-danger">Error loading questions. Please try again.</div>';
    }
}

async function viewResults(questionId) {
    // Show modal and loading indicator
    const resultsModal = new bootstrap.Modal(document.getElementById('resultsModal'));
    resultsModal.show();
    
    document.getElementById('results-loading').style.display = 'block';
    document.getElementById('results-content').style.display = 'none';
    
    try {
        const response = await fetch(`/results/${questionId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch results');
        }
        
        const data = await response.json();
        
        // Update modal title
        document.getElementById('resultsModalLabel').textContent = `Results: ${data.question}`;
        
        // Display summary
        const summaryHTML = data.summary.map(item => 
            `<div class="d-flex justify-content-between align-items-center mb-2">
                <strong>${item.vote}:</strong> <span>${item.count} vote(s)</span>
             </div>`
        ).join('');
        
        document.getElementById('results-summary').innerHTML = summaryHTML;
        
        // Create chart
        const labels = data.summary.map(item => item.vote);
        const counts = data.summary.map(item => item.count);
        const colors = generateColors(labels.length);
        
        const ctx = document.getElementById('results-chart').getContext('2d');
        if (resultsChart) {
            resultsChart.destroy();
        }
        
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
                    },
                    title: {
                        display: true,
                        text: 'Vote Distribution'
                    }
                }
            }
        });
        
        // Display individual votes
        const votesTableBody = document.getElementById('votes-table-body');
        votesTableBody.innerHTML = data.votes.map(vote => 
            `<tr>
                <td>${vote.name}</td>
                <td>${vote.vote}</td>
            </tr>`
        ).join('');
        
        // Show results content
        document.getElementById('results-loading').style.display = 'none';
        document.getElementById('results-content').style.display = 'block';
        
    } catch (error) {
        console.error('Error fetching results:', error);
        document.getElementById('results-content').innerHTML = 
            '<div class="alert alert-danger">Failed to load results. Please try again.</div>';
        document.getElementById('results-loading').style.display = 'none';
        document.getElementById('results-content').style.display = 'block';
    }
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
    
    // If we have more items than colors, we'll repeat colors
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    
    return colors;
}

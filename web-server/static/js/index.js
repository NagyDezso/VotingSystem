// Fetch and display active questions
async function loadQuestions() {
    try {
        const response = await fetch('/questions?active_only=true');
        const questions = await response.json();
        
        const container = document.getElementById('questions-container');
        
        if (questions.length === 0) {
            container.innerHTML = '<div class="col-12 text-center p-5">No active questions found.</div>';
            return;
        }
        
        container.innerHTML = questions.map(q => `
            <div class="col">
                <div class="card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${q.title}</h5>
                        <p class="card-text">${q.description}</p>
                    </div>
                    <div class="card-footer">
                        <a href="/question/${q.id}" class="btn btn-sm btn-primary">Vote</a>
                        <a href="/results/${q.id}" class="btn btn-sm btn-secondary">View Results</a>
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

// Load questions when page loads
document.addEventListener('DOMContentLoaded', loadQuestions);

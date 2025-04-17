document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('vote-form');
    const questionId = document.getElementById('question-id').value;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const name = document.getElementById('name').value.trim();
        const voteOption = document.querySelector('input[name="vote"]:checked')?.value;
        
        if (!name || !voteOption) {
            showError('Please enter your name and select an option');
            return;
        }
        
        try {
            const response = await fetch(`/vote/${questionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    vote: voteOption
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to submit vote');
            }
            
            // Show success message
            document.getElementById('success-message').classList.remove('d-none');
            document.getElementById('error-message').classList.add('d-none');
            
            // Disable form
            Array.from(form.elements).forEach(element => {
                element.disabled = true;
            });
            
            // Redirect to results page after 2 seconds
            setTimeout(() => {
                window.location.href = `/results/${questionId}`;
            }, 2000);
            
        } catch (error) {
            showError(error.message);
        }
    });
    
    function showError(message) {
        const errorElement = document.getElementById('error-message');
        errorElement.textContent = message;
        errorElement.classList.remove('d-none');
        document.getElementById('success-message').classList.add('d-none');
    }
});

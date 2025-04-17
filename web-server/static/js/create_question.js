document.addEventListener('DOMContentLoaded', function() {
    const optionsContainer = document.getElementById('options-container');
    const addOptionBtn = document.getElementById('add-option');
    const form = document.getElementById('question-form');
    
    // Add option button handler
    addOptionBtn.addEventListener('click', function() {
        const newOption = document.createElement('div');
        newOption.className = 'input-group mb-2';
        newOption.innerHTML = `
            <input type="text" class="form-control option-input" required>
            <button type="button" class="btn btn-outline-danger remove-option">Remove</button>
        `;
        optionsContainer.appendChild(newOption);
    });
    
    // Remove option button handler (using event delegation)
    optionsContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-option')) {
            // Don't remove if there are only 2 options left
            if (document.querySelectorAll('.option-input').length > 2) {
                e.target.closest('.input-group').remove();
            } else {
                alert('A question must have at least 2 options');
            }
        }
    });
    
    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const title = document.getElementById('title').value.trim();
        const description = document.getElementById('description').value.trim();
        const optionInputs = document.querySelectorAll('.option-input');
        const options = Array.from(optionInputs).map(input => input.value.trim()).filter(val => val);
        
        // Basic validation
        if (!title) {
            showError('Please enter a question title');
            return;
        }
        
        if (options.length < 2) {
            showError('Please provide at least 2 options');
            return;
        }
        
        try {
            const response = await fetch('/questions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title,
                    description,
                    options
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to create question');
            }
            
            // Show success message
            document.getElementById('success-message').classList.remove('d-none');
            document.getElementById('error-message').classList.add('d-none');
            
            // Reset form
            form.reset();
            
            // Redirect to home page after 2 seconds
            setTimeout(() => {
                window.location.href = '/';
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

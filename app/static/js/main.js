document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-fade flash alerts
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function() {
                alert.remove();
            }, 600);
        }, 5000);
    });

    // AJAX Subtask Toggling
    const subtaskCheckboxes = document.querySelectorAll('.subtask-toggle');
    subtaskCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('click', function() {
            const subtaskId = this.dataset.id;
            const isChecked = this.classList.contains('checked');
            
            // Optimistic UI updates
            this.classList.toggle('checked');
            const subtaskTitle = document.getElementById(`subtask-title-${subtaskId}`);
            if (subtaskTitle) {
                subtaskTitle.classList.toggle('text-decoration-line-through');
                subtaskTitle.classList.toggle('text-muted');
            }

            // AJAX call to flask endpoint
            fetch(`/subtask/${subtaskId}/toggle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Update main task progress bar
                    const progressBar = document.getElementById('task-progress-bar');
                    const progressPercentText = document.getElementById('task-progress-percent');
                    
                    if (progressBar && progressPercentText) {
                        progressBar.style.width = `${data.completion_percentage}%`;
                        progressPercentText.textContent = `${data.completion_percentage}% Completed`;
                    }
                    
                    // Update task status badge if it exists
                    const statusBadge = document.getElementById('task-status-badge');
                    if (statusBadge) {
                        statusBadge.textContent = data.task_status;
                        // Dynamically update class for badge
                        statusBadge.className = 'badge bg-secondary'; // simple fallback
                        if (data.task_status === 'Completed') {
                            statusBadge.className = 'badge bg-success';
                        } else if (data.task_status === 'In Progress') {
                            statusBadge.className = 'badge bg-info text-dark';
                        }
                    }
                } else {
                    // Revert UI if server action failed
                    revertUI(this, subtaskId);
                }
            })
            .catch(error => {
                console.error('Error toggling subtask:', error);
                revertUI(this, subtaskId);
            });
        });
    });

    function revertUI(checkboxElement, subtaskId) {
        checkboxElement.classList.toggle('checked');
        const subtaskTitle = document.getElementById(`subtask-title-${subtaskId}`);
        if (subtaskTitle) {
            subtaskTitle.classList.toggle('text-decoration-line-through');
            subtaskTitle.classList.toggle('text-muted');
        }
        alert('Could not update subtask. Please refresh and try again.');
    }
});

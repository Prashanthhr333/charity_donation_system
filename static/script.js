document.getElementById('donationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const donationData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        amount: document.getElementById('amount').value,
        cause: document.getElementById('cause').value
    };

    try {
        const response = await fetch('/donate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(donationData)
        });

        const result = await response.json();
        if (response.ok) {
            showNotification(`${result.message}\nTransaction ID: ${result.transaction_id}`, 'success');
            document.getElementById('donationForm').reset();
            loadDonations();
        } else {
            showNotification('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showNotification('Error submitting donation: ' + error, 'error');
    }
});

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    // Trigger animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

async function loadDonations() {
    try {
        const response = await fetch('/donations');
        const donations = await response.json();
        
        const donationsList = document.getElementById('donationsList');
        donationsList.innerHTML = '';
        
        donations.forEach((donation, index) => {
            const donationElement = document.createElement('div');
            donationElement.className = 'donation-item' + (index === 0 ? ' new' : '');
            donationElement.innerHTML = `
                <div class="donation-header">
                    <span class="donation-name">${donation.name}</span>
                    <span class="donation-amount">₹${donation.amount.toLocaleString('en-IN')}</span>
                </div>
                <div class="donation-details">
                    <span class="donation-cause">${donation.cause}</span>
                    <span class="donation-date">${donation.date}</span>
                </div>
                <div class="donation-transaction">
                    <small class="text-muted">Transaction ID: ${donation.transaction_id}</small>
                    <button class="delete-btn" onclick="deleteDonation(${donation.id}, this)">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            donationsList.appendChild(donationElement);
        });
    } catch (error) {
        console.error('Error loading donations:', error);
        showNotification('Error loading donations: ' + error, 'error');
    }
}

async function deleteDonation(donationId, button) {
    if (!confirm('Are you sure you want to delete this donation?')) {
        return;
    }

    try {
        const response = await fetch(`/delete_donation/${donationId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            const donationItem = button.closest('.donation-item');
            donationItem.style.transform = 'translateX(100%)';
            donationItem.style.opacity = '0';
            
            setTimeout(() => {
                donationItem.remove();
                showNotification('Donation deleted successfully', 'success');
            }, 300);
        } else {
            const data = await response.json();
            showNotification('Error: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Error deleting donation: ' + error, 'error');
    }
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        transform: translateX(150%);
        transition: transform 0.3s ease;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .notification.show {
        transform: translateX(0);
    }

    .notification.success {
        background-color: var(--success);
    }

    .notification.error {
        background-color: var(--danger);
    }
`;
document.head.appendChild(style);

// Load donations when page loads
document.addEventListener('DOMContentLoaded', loadDonations);

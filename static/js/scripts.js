document.addEventListener('DOMContentLoaded', function() {
    let alertQueue = [];

    function showNotification(message, type) {
        // Limit the number of notifications
        const maxAlerts = 3;

        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.role = 'alert';
        notification.innerHTML = `<span>${message}</span>`;

        // Add the new notification to the queue
        alertQueue.push(notification);
        document.getElementById('notifications').appendChild(notification);

        // Remove the oldest alert if we exceed the maxAlerts
        if (alertQueue.length > maxAlerts) {
            const oldestAlert = alertQueue.shift();
            $(oldestAlert).alert('close');
        }

        setTimeout(() => {
            $(notification).alert('close');
        }, 5000);
    }

    function handleResponse(response) {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.message || 'Unknown error');
            });
        }
        return response.json();
    }

    // View Chain
    document.getElementById('view-chain').addEventListener('click', function() {
        fetch('/chain')
            .then(handleResponse)
            .then(data => {
                document.getElementById('chain-output').textContent = JSON.stringify(data, null, 2);
                showNotification('Blockchain fetched successfully!', 'success');
            })
            .catch(error => {
                console.error('Error fetching blockchain:', error);
                showNotification('Error fetching blockchain: ' + error.message, 'danger');
            });
    });

    // New Transaction
    document.getElementById('transaction-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const sender = document.getElementById('sender').value;
        const recipient = document.getElementById('recipient').value;
        const amount = parseFloat(document.getElementById('amount').value);

        fetch('/transactions/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sender, recipient, amount })
        })
        .then(handleResponse)
        .then(data => {
            document.getElementById('transaction-output').textContent = JSON.stringify(data, null, 2);
            showNotification('Transaction created successfully!', 'success');
        })
        .catch(error => {
            console.error('Error creating transaction:', error);
            showNotification('Error creating transaction: ' + error.message, 'danger');
        });
    });

    // Mine Block
    document.getElementById('mine-block').addEventListener('click', function() {
        fetch('/mine')
            .then(handleResponse)
            .then(data => {
                document.getElementById('mining-output').textContent = JSON.stringify(data, null, 2);
                showNotification('Block mined successfully!', 'success');
            })
            .catch(error => {
                console.error('Error mining block:', error);
                showNotification('Error mining block: ' + error.message, 'danger');
            });
    });

    // Register Node
    document.getElementById('register-node-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const nodeAddress = document.getElementById('node-address').value;

        fetch('/nodes/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nodes: [nodeAddress] })
        })
        .then(handleResponse)
        .then(data => {
            document.getElementById('nodes-output').textContent = JSON.stringify(data, null, 2);
            showNotification('Node registered successfully!', 'success');
        })
        .catch(error => {
            console.error('Error registering node:', error);
            showNotification('Error registering node: ' + error.message, 'danger');
        });
    });

    // Resolve Nodes
    document.getElementById('resolve-nodes').addEventListener('click', function() {
        fetch('/nodes/resolve')
            .then(handleResponse)
            .then(data => {
                document.getElementById('nodes-output').textContent = JSON.stringify(data, null, 2);
                showNotification('Nodes resolved successfully!', 'success');
            })
            .catch(error => {
                console.error('Error resolving nodes:', error);
                showNotification('Error resolving nodes: ' + error.message, 'danger');
            });
    });
});

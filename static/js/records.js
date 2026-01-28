let filterBtn = document.getElementById('filterBtn');
let resetBtn = document.getElementById('resetBtn');
let exportBtn = document.getElementById('exportBtn');
let tableBody = document.getElementById('tableBody');
let usersList = document.getElementById('usersList');

let allRecords = [];
let registeredUsers = [];

// Load data on page load
window.addEventListener('DOMContentLoaded', () => {
    loadRegisteredUsers();
    updateStatistics();
});

// Load registered users
async function loadRegisteredUsers() {
    try {
        let response = await fetch('/api/get_registered_users');
        let data = await response.json();
        
        if (data.success) {
            registeredUsers = data.users;
            displayUsers();
            populateUserFilter();
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Display users
function displayUsers() {
    usersList.innerHTML = '';
    
    if (registeredUsers.length === 0) {
        usersList.innerHTML = '<p>No registered users yet</p>';
        return;
    }
    
    registeredUsers.forEach(user => {
        let userCard = document.createElement('div');
        userCard.className = 'user-card';
        userCard.innerHTML = `
            <strong>${user.name}</strong>
            <div style="color: #666; font-size: 0.9em; margin-top: 5px;">
                ID: ${user.user_id}
            </div>
        `;
        usersList.appendChild(userCard);
    });
}

// Populate user filter dropdown
function populateUserFilter() {
    let userFilter = document.getElementById('userFilter');
    userFilter.innerHTML = '<option value="">All Users</option>';
    
    registeredUsers.forEach(user => {
        let option = document.createElement('option');
        option.value = user.user_id;
        option.textContent = user.name;
        userFilter.appendChild(option);
    });
}

// Update statistics
async function updateStatistics() {
    try {
        let response = await fetch('/api/attendance_report');
        let data = await response.json();
        
        if (data.success) {
            allRecords = data.report;
            
            // Total records
            document.getElementById('totalRecords').textContent = allRecords.length;
            
            // Total users
            document.getElementById('totalUsers').textContent = registeredUsers.length;
            
            // Today's attendance
            let today = new Date().toISOString().split('T')[0];
            let todayRecords = allRecords.filter(record => record.date === today);
            document.getElementById('todayAttendance').textContent = todayRecords.length;
        }
    } catch (error) {
        console.error('Error updating statistics:', error);
    }
}

// Filter records
filterBtn.addEventListener('click', async () => {
    let startDate = document.getElementById('startDate').value;
    let endDate = document.getElementById('endDate').value;
    let userId = document.getElementById('userFilter').value;
    let action = document.getElementById('actionFilter').value;
    
    try {
        let url = '/api/attendance_report';
        let params = new URLSearchParams();
        
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        let response = await fetch(url);
        let data = await response.json();
        
        if (data.success) {
            let filteredRecords = data.report;
            
            // Apply additional filters
            if (userId) {
                filteredRecords = filteredRecords.filter(r => r.user_id === userId);
            }
            
            if (action) {
                filteredRecords = filteredRecords.filter(r => r.action === action);
            }
            
            updateTable(filteredRecords);
        }
    } catch (error) {
        console.error('Error filtering records:', error);
    }
});

// Reset filters
resetBtn.addEventListener('click', () => {
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    document.getElementById('userFilter').value = '';
    document.getElementById('actionFilter').value = '';
    
    updateTable(allRecords);
});

// Update table
function updateTable(records) {
    tableBody.innerHTML = '';
    
    if (records.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No records found</td></tr>';
        return;
    }
    
    // Sort by date and time (newest first)
    records.sort((a, b) => {
        let dateA = new Date(a.timestamp);
        let dateB = new Date(b.timestamp);
        return dateB - dateA;
    });
    
    records.forEach(record => {
        let row = document.createElement('tr');
        
        let badgeClass = record.action === 'punch-in' ? 'success' : 'info';
        
        row.innerHTML = `
            <td>${record.date}</td>
            <td>${record.time}</td>
            <td>${record.name}</td>
            <td>${record.user_id}</td>
            <td><span class="badge badge-${badgeClass}">${record.action}</span></td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Export to CSV
exportBtn.addEventListener('click', async () => {
    try {
        let response = await fetch('/api/attendance_report');
        let data = await response.json();
        
        if (data.success) {
            let records = data.report;
            
            if (records.length === 0) {
                alert('No records to export');
                return;
            }
            
            // Create CSV content
            let csv = 'Date,Time,Name,User ID,Action\n';
            
            records.forEach(record => {
                csv += `${record.date},${record.time},${record.name},${record.user_id},${record.action}\n`;
            });
            
            // Create download link
            let blob = new Blob([csv], { type: 'text/csv' });
            let url = window.URL.createObjectURL(blob);
            let a = document.createElement('a');
            a.href = url;
            a.download = `attendance_report_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
    } catch (error) {
        console.error('Error exporting records:', error);
        alert('Error exporting records: ' + error.message);
    }
});

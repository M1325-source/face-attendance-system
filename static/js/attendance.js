let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let captureBtn = document.getElementById('captureBtn');
let startCamera = document.getElementById('startCamera');
let punchInBtn = document.getElementById('punchInBtn');
let punchOutBtn = document.getElementById('punchOutBtn');
let identificationResult = document.getElementById('identificationResult');
let message = document.getElementById('message');

let stream = null;
let selectedAction = 'punch-in';

// Action button handlers
punchInBtn.addEventListener('click', () => {
    selectedAction = 'punch-in';
    punchInBtn.classList.add('active');
    punchOutBtn.classList.remove('active');
});

punchOutBtn.addEventListener('click', () => {
    selectedAction = 'punch-out';
    punchOutBtn.classList.add('active');
    punchInBtn.classList.remove('active');
});

// Start camera
startCamera.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            } 
        });
        video.srcObject = stream;
        captureBtn.disabled = false;
        startCamera.disabled = true;
        showMessage('Camera started successfully', 'success');
    } catch (error) {
        showMessage('Error accessing camera: ' + error.message, 'error');
    }
});

// Capture and mark attendance
captureBtn.addEventListener('click', async () => {
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    let context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Get image data
    let imageData = canvas.toDataURL('image/jpeg');
    
    // Disable button to prevent multiple submissions
    captureBtn.disabled = true;
    showMessage('Processing face recognition...', 'info');
    
    try {
        let response = await fetch('/api/mark_attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageData,
                action: selectedAction
            })
        });
        
        let data = await response.json();
        
        if (data.success) {
            // Show identification result
            document.getElementById('userName').textContent = data.name;
            document.getElementById('userId').textContent = data.user_id;
            document.getElementById('confidence').textContent = data.confidence + '%';
            document.getElementById('actionType').textContent = data.action.toUpperCase();
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
            
            identificationResult.style.display = 'block';
            showMessage(data.message, 'success');
            
            // Stop camera
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                video.srcObject = null;
                startCamera.disabled = false;
            }
        } else {
            showMessage(data.message, 'error');
            captureBtn.disabled = false;
        }
    } catch (error) {
        showMessage('Error marking attendance: ' + error.message, 'error');
        captureBtn.disabled = false;
    }
});

function showMessage(msg, type) {
    message.textContent = msg;
    message.className = 'message ' + type;
    message.style.display = 'block';
    
    // Auto hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            message.style.display = 'none';
        }, 5000);
    }
}

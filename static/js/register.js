let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let captureBtn = document.getElementById('captureBtn');
let registerBtn = document.getElementById('registerBtn');
let retakeBtn = document.getElementById('retakeBtn');
let startCamera = document.getElementById('startCamera');
let capturedImageDiv = document.getElementById('capturedImage');
let preview = document.getElementById('preview');
let message = document.getElementById('message');

let stream = null;
let capturedImageData = null;

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

// Capture image
captureBtn.addEventListener('click', () => {
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    let context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Get image data
    capturedImageData = canvas.toDataURL('image/jpeg');
    
    // Show preview
    preview.src = capturedImageData;
    capturedImageDiv.style.display = 'block';
    registerBtn.style.display = 'inline-block';
    
    // Stop camera
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        startCamera.disabled = false;
        captureBtn.disabled = true;
    }
    
    showMessage('Face captured! Review and click Register User', 'info');
});

// Retake photo
retakeBtn.addEventListener('click', () => {
    capturedImageDiv.style.display = 'none';
    registerBtn.style.display = 'none';
    capturedImageData = null;
    startCamera.click();
});

// Register user
registerBtn.addEventListener('click', async () => {
    let name = document.getElementById('name').value.trim();
    let userId = document.getElementById('user_id').value.trim();
    
    if (!name || !userId) {
        showMessage('Please fill in all required fields', 'error');
        return;
    }
    
    if (!capturedImageData) {
        showMessage('Please capture your face first', 'error');
        return;
    }
    
    // Disable button to prevent double submission
    registerBtn.disabled = true;
    showMessage('Registering user...', 'info');
    
    try {
        let response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                user_id: userId,
                image: capturedImageData
            })
        });
        
        let data = await response.json();
        
        if (data.success) {
            showMessage(data.message, 'success');
            // Reset form after 2 seconds
            setTimeout(() => {
                document.getElementById('registrationForm').reset();
                capturedImageDiv.style.display = 'none';
                registerBtn.style.display = 'none';
                capturedImageData = null;
                registerBtn.disabled = false;
            }, 2000);
        } else {
            showMessage(data.message, 'error');
            registerBtn.disabled = false;
        }
    } catch (error) {
        showMessage('Error registering user: ' + error.message, 'error');
        registerBtn.disabled = false;
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

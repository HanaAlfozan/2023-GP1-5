// camera_capture.js
document.addEventListener('DOMContentLoaded', () => {
    const captureButton = document.getElementById('capture-button');
    const capturedImage = document.getElementById('captured-image');

    captureButton.addEventListener('click', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const mediaStreamTrack = stream.getVideoTracks()[0];
            const imageCapture = new ImageCapture(mediaStreamTrack);

            const blob = await imageCapture.takePhoto();
            const formData = new FormData();
            formData.append('image', blob, 'image.jpg');

            // Send the captured image to the server for processing
            const response = await fetch('/age_estimator/capture/', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                const ageGroup = data.age_group;
                // Display the age group or take further actions
            } else {
                console.error('Image capture failed.');
            }
        } catch (error) {
            console.error('Error capturing image:', error);
        }
    });
});

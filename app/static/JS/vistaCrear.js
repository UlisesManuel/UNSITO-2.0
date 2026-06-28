function previewImage(event) {
    const file = event.target.files[0];
    const container = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
            
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            container.classList.remove('hidden');
        }
        reader.readAsDataURL(file);
    } else {
        container.classList.add('hidden');
    }
}
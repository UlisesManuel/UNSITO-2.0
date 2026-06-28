function previewImage(event) {
    const file = event.target.files[0];
    const imagePreview = document.getElementById('image-preview');
    const previewLabel = document.getElementById('preview-label');     
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            previewLabel.textContent = "Vista previa de la nueva portada elegida:";
        }
        reader.readAsDataURL(file);
    }
}
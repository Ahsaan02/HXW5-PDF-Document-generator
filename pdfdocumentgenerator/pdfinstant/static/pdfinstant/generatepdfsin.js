document.addEventListener('DOMContentLoaded', function() {
    var uploadBox = document.querySelector('.upload-box');
    var fileInput = document.getElementById('csvFile');
    var uploadBtn = document.querySelector('.upload-btn');

    uploadBtn.addEventListener('click', function() {
        fileInput.click();
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadBox.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadBox.addEventListener(eventName, () => uploadBox.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadBox.addEventListener(eventName, () => uploadBox.classList.remove('dragover'), false);
    });

    uploadBox.addEventListener('drop', function(e) {
        fileInput.files = e.dataTransfer.files;
        uploadForm.submit();
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            uploadForm.submit();
        }
    });

    var uploadForm = document.querySelector('.upload-form');
});

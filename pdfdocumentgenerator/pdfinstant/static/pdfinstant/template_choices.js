document.addEventListener('DOMContentLoaded', () => {
    const radios = document.querySelectorAll('input[type="radio"][name="template"]');
    radios.forEach(radio => {
        radio.addEventListener('change', () => {
            radios.forEach(radio => radio.closest('.responsive-box').classList.remove('selected'));
            radio.closest('.responsive-box').classList.add('selected');
        });
    });

    const generatePdfBtn = document.getElementById('generatePdfBtn');
    const modal = document.getElementById('pdfActionModal');
    const span = document.getElementsByClassName("close")[0];
    const emailPdfsBtn = document.getElementById('emailPdfs');
    const downloadZipBtn = document.getElementById('downloadZip');
    const pdfForm = document.getElementById('pdfForm');

    generatePdfBtn.onclick = function() {
        modal.style.display = "block";
    }

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    function removeActionInput() {
        const existingActionInput = pdfForm.querySelector('input[name="action"]');
        if (existingActionInput) {
            pdfForm.removeChild(existingActionInput);
        }
    }

    emailPdfsBtn.addEventListener('click', () => {
        removeActionInput();

        const emailActionInput = document.createElement('input');
        emailActionInput.setAttribute('type', 'hidden');
        emailActionInput.setAttribute('name', 'action');
        emailActionInput.setAttribute('value', 'emailPdfs');
        pdfForm.appendChild(emailActionInput);

        pdfForm.submit();
    });

    downloadZipBtn.addEventListener('click', () => {
        removeActionInput();

        pdfForm.submit();
    });
});
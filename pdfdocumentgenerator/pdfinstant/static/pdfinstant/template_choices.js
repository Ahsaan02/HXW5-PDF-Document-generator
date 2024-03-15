
document.addEventListener('DOMContentLoaded', () => {
    const radios = document.querySelectorAll('input[type="radio"][name="template"]');
    radios.forEach(radio => {
        radio.addEventListener('change', () => {
            radios.forEach(radio => radio.closest('.responsive-box').classList.remove('selected'));
            radio.closest('.responsive-box').classList.add('selected');
        });
    });
});
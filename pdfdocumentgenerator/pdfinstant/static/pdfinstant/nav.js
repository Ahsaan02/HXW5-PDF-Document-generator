var hamburgercheck = document.getElementById('hamburgernav');
hamburgercheck.addEventListener('change', hamburgernav);


function hamburgernav() {
    var pages = document.getElementById('pages');
        pages.style.marginTop = '270px';

        if (!hamburgercheck.checked){
            pages.style.marginTop = '0px';
        }
}

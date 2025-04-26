let nav_toggler = document.getElementById('nav-toggler'); 
let [list_toggler, chevron_toggler] = nav_toggler.children;

nav_toggler.onclick = (event) => {
    list_toggler.classList.toggle('hidden');
    chevron_toggler.classList.toggle('hidden');
}
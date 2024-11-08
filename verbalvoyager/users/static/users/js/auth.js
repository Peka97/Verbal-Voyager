let auth_btn = document.getElementById('auth-btn');
let sign_up_btn = document.getElementById('sign-up-btn');

let auth_row = document.getElementById('auth-row');
let sign_up_row = document.getElementById('sign-up-row');

console.dir(auth_btn);
console.dir(sign_up_btn);
console.dir(auth_row);
console.dir(sign_up_row);

auth_btn.onclick = (event) => {
    event.preventDefault();
    auth_btn.classList.add('active');
    sign_up_btn.classList.remove('active');
    auth_row.classList.remove('d-none');
    sign_up_row.classList.add('d-none');
}

sign_up_btn.onclick = (event) => {
    event.preventDefault();
    auth_btn.classList.remove('active');
    sign_up_btn.classList.add('active');
    sign_up_row.classList.remove('d-none');
    auth_row.classList.add('d-none');
}
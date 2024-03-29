/* Pagination */ 
function prev_paginator_handler(event) {
    next_btn.classList.remove('disabled')

    let curr_page = Number(Array.from(document.getElementsByClassName('page-item active'))[0].id.split('_')[1])
    if (curr_page > 1) {
        let new_page = curr_page - 1 
        if (new_page == 1){
            prev_btn.classList.add('disabled')
        }
        else {
            prev_btn.classList.remove('disabled')
        }
        pages[new_page - 1].classList.add('watched');
        alertsHide();
        update_paginator_by_number(new_page);
    }
}

function next_paginator_handler(event) {
    prev_btn.classList.remove('disabled')

    let curr_page = Number(Array.from(document.getElementsByClassName('page-item active'))[0].id.split('_')[1])
    if (curr_page < max_page) {
        let new_page = curr_page + 1 
        if (new_page == max_page){
            next_btn.classList.add('disabled')
        }
        else {
            next_btn.classList.remove('disabled')
        }
        pages[new_page - 1].classList.add('watched');
        alertsHide();
        update_paginator_by_number(new_page);
    }   
}

function update_paginator_by_number(number) {
    pages.forEach(el => {
        if (el.id == `page_${number}`){
            el.classList.add('active')
        }
        else {
            el.classList.remove('active');
        }
    })
    words.forEach(el => {
        if (el.id == `word_check_${number}`){
            el.parentElement.classList.remove('hidden');
        }
        else {
            el.parentElement.classList.add('hidden')
        }
    })
}

function paginator_handler(event) {
    pages.forEach(el => {
        el.classList.remove('active');
    })
    event.target.parentElement.classList.add('active');
    let curr_word = Number(String(event.target.parentElement.id).split('_')[1]);
    if (curr_word == 1 ) {
        prev_btn.classList.add('disabled')
        next_btn.classList.remove('disabled')
    }
    else if (curr_word == max_page) {
        next_btn.classList.add('disabled')
        prev_btn.classList.remove('disabled')
    }
    else {
        prev_btn.classList.remove('disabled')
        next_btn.classList.remove('disabled')

    }
    words.forEach(el => {
        if (el.id == `word_check_${curr_word}`){
            el.parentElement.classList.remove('hidden');
        }
        else {
            el.parentElement.classList.add('hidden')
        }
    })
    alertsHide();
}

function checkAnswer() {
    let curr_page = Number(Array.from(document.getElementsByClassName('page-item active'))[0].id.split('_')[1]);
    let word = document.getElementById(`word_check_${curr_page}`);
    let user_input = String(word.children[1].value).toLowerCase();
    let translate = String(word.children[1].id).toLowerCase();
    console.log(user_input + '' + translate)
    if (user_input == translate) {
        console.log('Правильно!')
        alert_success.classList.remove('hidden');
        alert_danger.classList.add('hidden');
        check_words[word.id] = true;
    }
    else {
        alert_success.classList.add('hidden');
        alert_danger.classList.remove('hidden');
    }
    let check = check_all_words_true();
    if (check) {
        done_btn.parentElement.parentElement.classList.remove('hidden')
        document.getElementById('step_4').classList.remove('active');
        document.getElementById('step_4').classList.add('step-complete');
        document.getElementById('alert-done').classList.remove('hidden');
    }
}

function alertsHide() {
    alert_danger.classList.add('hidden');
    alert_success.classList.add('hidden');
}

function fill_check_words() {
    words.forEach(el => {
        check_words[el.id] = false;
    })   
}

function check_all_words_true() {
    for (key in check_words) {
        if (check_words[key] != true) {
            return false;
        }
    }
    return true;
}

document.getElementById('page_1').classList.add('active', 'watched');

let words = Array.from(document.getElementsByClassName('word_check'));
let paginator = Array.from(document.getElementsByClassName('pagination'));
let prev_btn = document.getElementById('prev_btn');
let next_btn = document.getElementById('next_btn');
let pages = Array.from(paginator[0].children).slice(1, -1);
let max_page = Number(Array.from(paginator[0].children).slice(-2)[0].id.split('_')[1]);
let alert_success = document.getElementById('alert-success');
let alert_danger = document.getElementById('alert-danger');
let check_words = {}

document.getElementById('btn-check').onclick = (event) => {
    checkAnswer();
}
prev_btn.onclick = (event) => {prev_paginator_handler(event)};
pages.forEach(el => {
    el.onclick = (event) => {paginator_handler(event)};
});
next_btn.onclick = (event) => {next_paginator_handler(event)};


/* On start */
document.getElementById('word_check_1').parentElement.classList.remove('hidden');
document.getElementById('page_1').classList.add('active', 'watched');
document.getElementById('step_1').classList.add('bg-success', 'text-light');
document.getElementById('step_2').classList.add('bg-success', 'text-light');
document.getElementById('step_3').classList.add('bg-success', 'text-light');
fill_check_words();

const done_btn = document.getElementById('done-btn')

done_btn.onclick = (event) => {
    let token = document.getElementsByName('csrfmiddlewaretoken')[0].defaultValue
    let url = 'http://127.0.0.1:8000/exercises/update'
    let ex_id = window.location.href.split('/').slice(-2, -1)[0]
    let step = window.location.href.split('/').slice(-1)[0]

    fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': token,
            },
            body: JSON.stringify({
                'exercise_id': ex_id,
                'step' : step,
                "value": pages.length,
            })
        }
    ).then(response => {
        if (response.status != 200) {
            console.log('Не удалось отправить данные');
            event.preventDefault();
        }
    })
}

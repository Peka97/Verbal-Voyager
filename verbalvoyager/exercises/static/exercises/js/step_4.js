import { showToast } from './modules/toast_notification.js';
import { toNextStep } from './modules/next_step.js';
import { pagination, updatePagination } from './modules/pagination.js';
import { send_points } from './modules/send_points.js';

pagination.forEach(el => {
    el.onclick = (event) => {
        updatePagination(event);
    };
});

<<<<<<< HEAD
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
            el.classList.remove('hidden');
        }
        else {
            el.classList.add('hidden')
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
            el.classList.remove('hidden');
        }
        else {
            el.classList.add('hidden')
        }
    })
}

function checkAnswer() {
    let curr_page = Number(Array.from(document.getElementsByClassName('page-item active'))[0].id.split('_')[1]);
    let word = document.getElementById(`word_check_${curr_page}`);
    let user_input = String(word.children[1].children[0].value).toLowerCase();
    let translate = String(word.children[1].children[0].id).toLowerCase();
    console.log('Ввод пользователя: ' + user_input)
=======

function checkAnswer() {
    let curr_page = Number(Array.from(document.getElementsByClassName('page-item active'))[0].id.split('_')[1]);
    let word = document.getElementById(`word_${curr_page}`);
    let user_input = String(word.children[1].children[0].value).toLowerCase();
    let translate = String(word.children[1].children[0].id).toLowerCase();
>>>>>>> origin/dev

    if (user_input == translate) {
        check_words[word.id] = true;
 
        if (!checkAllAnswersTrue()) {
            showToast('Правильно! Переходи к следующему слову.');
        }
    }
    else {
        showToast('Неправильно, подумай ещё раз.');
        if (points > 1) {
            points--;
        }
    }
    
    if (checkAllAnswersTrue()) {
        showToast('Упражнение завершено! Переходи по кнопке в Личный кабинет');
        send_points('words', points);
        done_btn.parentElement.classList.remove('hidden');
        toNextStep(4);
    }
}

function fillCheckWords() {
    words.forEach(el => {
        check_words[el.id] = false;
    })   
}

function checkAllAnswersTrue() {
    for (let key in check_words) {
        if (check_words[key] != true) {
            return false;
        }
    }
    return true;
}

let words = [...document.getElementsByClassName('word__block')];
let points = words.length;
words[0].classList.remove('hidden');
let check_words = {};
let input_fields = [...document.getElementsByClassName('word__check')];
document.getElementById('step_1').classList.add('step-complete');
document.getElementById('step_2').classList.add('step-complete');
document.getElementById('step_3').classList.add('step-complete');


input_fields.forEach( (el) => set_keypress_event(el));

function set_keypress_event (el) {
    el.addEventListener('keypress', function (e) {
        var key = e.which || e.keyCode;
        
        if (key === 13) { // код клавиши Enter
            toastTrigger.click();
        }});
};


/* On start */
<<<<<<< HEAD
document.getElementById('word_check_1').classList.remove('hidden');
=======
document.getElementById('word_1').classList.remove('hidden');
>>>>>>> origin/dev
document.getElementById('page_1').classList.add('active', 'watched');
fillCheckWords();

const done_btn = document.getElementById('done-btn');
const toastTrigger = document.getElementById('liveToastBtn');
toastTrigger.addEventListener('click', () => {
    checkAnswer();
})

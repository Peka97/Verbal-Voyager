import { showToast } from './modules/toast_notification.js';
import { toNextStep } from './modules/next_step.js';
import { pagination, updatePagination } from './modules/pagination.js';
import { send_points } from './modules/send_points.js';

pagination.forEach(el => {
    el.onclick = (event) => {
        updatePagination(event);
        checkAllWordsWatched(event);
    };
});
let words = [...document.getElementsByClassName('word__block')];
let points = words.length;
words[0].classList.add('watched');

// Код для подсказок рядом с названием шага упражнения.
// let popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
// let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
//     return new bootstrap.Popover(popoverTriggerEl);
// });

function checkAllWordsWatched (event) {
    let current_word_block = document.querySelector('div.word__block:not(.hidden)');
    current_word_block.classList.add('watched');

    for (let i=0; i < words.length; i++) {
        if (!words[i].classList.contains('watched')) {
            return false;
        }
    }
<<<<<<< HEAD

    document.body.scrollIntoView({behavior: "smooth",});
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
        update_paginator_by_number(new_page);
        checkAllPagesWatched();
    }

    document.body.scrollIntoView({behavior: "smooth",});
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
        if (el.id == `word_${number}`){
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
    event.target.parentElement.classList.add('active', 'watched');
    checkAllPagesWatched();
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
        if (el.id == `word_${curr_word}`){
            el.classList.remove('hidden');
        }
        else {
            el.classList.add('hidden')
        }
    })
}

function checkAllPagesWatched() {
    result = true
    pages.forEach(el => {
        if (Array.from(el.classList).includes('watched') == false) {
            result = false
        }
    })

    if (result == true) {
        glow.classList.remove('disabled')
        stars.classList.remove('disabled')

        toastLiveExample.attributes.getNamedItem('data-bs-delay').nodeValue = '10000'
        toastBody.innerText = 'Запомнил слова? Тогда переходи к следующему шагу!'
        const toast = new bootstrap.Toast(toastLiveExample)
        toast.show()

        document.getElementById('step_1').classList.remove('active', 'step-active')
        document.getElementById('step_1').classList.add('step-complete')
        document.getElementById('step_2').classList.remove('step-future', 'disabled')
        document.getElementById('step_2').classList.add('next-btn', 'active')

        send_points()
    }
}

document.getElementById('page_1').classList.add('active', 'watched')

let words = Array.from(document.getElementsByClassName('word__block'))
let paginator = Array.from(document.getElementsByClassName('pagination'))
let pages = Array.from(paginator[0].children).slice(1, -1)
let points = words.length

const max_page = Number(Array.from(paginator[0].children).slice(-2)[0].id.split('_')[1])
const prev_btn = document.getElementById('prev_btn')
const next_btn = document.getElementById('next_btn')
const next_step = document.getElementById('step_2')

prev_btn.onclick = (event) => {prev_paginator_handler(event)}
pages.forEach(el => {
    el.onclick = (event) => {paginator_handler(event)}
})
next_btn.onclick = (event) => {next_paginator_handler(event)}

function send_points() {
    console.log('Отправка баллов...')
    let token = document.getElementsByName('csrfmiddlewaretoken')[0].defaultValue
    
    let ex_id = window.location.href.split('/').slice(-2, -1)[0]
    let step_num = window.location.href.split('/').slice(-1)[0]
    let url = `https://verbal-voyager.ru/exercises/update/${ex_id}/step_${step_num}`

    fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': token,
            },
            body: JSON.stringify({
                'value': points
            })
        }
    ).then(response => {
        console.log(response.status)
        if (response.status != 200) {
            console.log('Не удалось отправить баллы');
        }
        else {
            console.log('Баллы отправлены')
        }
    })
}

var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl)
})

const toastLiveExample = document.getElementById('liveToast')
const toastBody = document.getElementById('toast-body')

const stars = document.getElementById('step_2').children[1]
const glow = document.getElementById('step_2').children[2]
=======
    showToast('Запомнил слова? Тогда переходи к следующему шагу!');
    send_points('words', points);
    toNextStep(1);
    return true;
}
>>>>>>> origin/dev

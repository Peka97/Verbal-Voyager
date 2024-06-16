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

    if (user_input == translate) {
        console.log(user_input + ' == ' + translate)
        
        if (toastTrigger) {
            toastLiveExample.attributes.getNamedItem('data-bs-delay').nodeValue = '10000'
            toastBody.innerText = 'Правильно! Переходи к следующему слову.'
            const toast = new bootstrap.Toast(toastLiveExample)
            toast.show()
          }
        check_words[word.id] = true;
    }
    else {
        console.log(user_input + ' != ' + translate)

        toastLiveExample.attributes.getNamedItem('data-bs-delay').nodeValue = '10000'
        toastBody.innerText = 'Неправильно, подумай ещё раз.'
        const toast = new bootstrap.Toast(toastLiveExample)
        toast.show()

        if (points > 1) {
            points--;
        }
    }

    let check = check_all_words_true();
    
    if (check) {
        done_btn.parentElement.classList.remove('hidden')
        document.getElementById('step_4').classList.remove('active');
        document.getElementById('step_4').classList.add('step-complete');
        
        toastLiveExample.attributes.getNamedItem('data-bs-delay').nodeValue = '10000'
        toastBody.innerText = 'Упражнение завершено! Переходи по кнопке в Личный кабинет'
        const toast = new bootstrap.Toast(toastLiveExample)
        toast.show()

        send_points()
    }
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

document.getElementById('page_1').classList.add('active', 'watched');

let words = Array.from(document.getElementsByClassName('word_check'));
let paginator = Array.from(document.getElementsByClassName('pagination'));
let prev_btn = document.getElementById('prev_btn');
let next_btn = document.getElementById('next_btn');
let pages = Array.from(paginator[0].children).slice(1, -1);
let max_page = Number(Array.from(paginator[0].children).slice(-2)[0].id.split('_')[1]);
let check_words = {}
let input_field = document.getElementsByClassName('word__check')[0]
let input_fields = document.getElementsByClassName('word__check')
let points = words.length
const step_1 = document.getElementById('step_1').classList.add('step-complete')
const step_2 = document.getElementById('step_2').classList.add('step-complete')
const step_3 = document.getElementById('step_3').classList.add('step-complete')


Array.from(input_fields).forEach( (el) => set_keypress_event(el))

function set_keypress_event (el) {
    el.addEventListener('keypress', function (e) {
        var key = e.which || e.keyCode;
        
        if (key === 13) { // код клавиши Enter
            toastTrigger.click();
        }});
};

prev_btn.onclick = (event) => {prev_paginator_handler(event)};
pages.forEach(el => {
    el.onclick = (event) => {paginator_handler(event)};
});
next_btn.onclick = (event) => {next_paginator_handler(event)};


/* On start */
document.getElementById('word_check_1').classList.remove('hidden');
document.getElementById('page_1').classList.add('active', 'watched');
fill_check_words();

const done_btn = document.getElementById('done-btn')

const toastTrigger = document.getElementById('liveToastBtn')
const toastLiveExample = document.getElementById('liveToast')
const toastBody = document.getElementById('toast-body')
if (toastTrigger) {
    toastTrigger.addEventListener('click', () => {
      const toast = new bootstrap.Toast(toastLiveExample)
      checkAnswer()
  
      toast.show()
    })
  }


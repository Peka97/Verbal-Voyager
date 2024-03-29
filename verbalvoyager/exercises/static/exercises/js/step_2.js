/* Pagination */ 
function prevPaginatorHandler(event) {
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
        // pages[new_page - 1].classList.add('watched');
        updatePaginatorByNumber(new_page);
        // checkAllPagesWatched();
    }
}

function nextPaginatorHandler(event) {
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
        // pages[new_page - 1].classList.add('watched');
        updatePaginatorByNumber(new_page);
        // checkAllPagesWatched();
    }   
}

function updatePaginatorByNumber(number) {
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

function paginatorHandler(event) {
    pages.forEach(el => {
        el.classList.remove('active');
    })
    event.target.parentElement.classList.add('active');
    // checkAllPagesWatched();
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

function wordCheckHandlers() {
    let curr_page = Number(Array.from(document.getElementsByClassName('page-item active'))[0].id.split('_')[1])

    let translates = Array.from(document.getElementById(`word_check_${curr_page}`).children).slice(1, )
    translates.forEach(el => {
        let btn = Array.from(el.children)[0]
        let flag = Array.from(btn.classList).includes('answer')
        btn.onclick = (event) => {
            if (flag) {
                let page_obj = document.getElementById(`page_${curr_page}`)
                
                alert_danger.classList.add('hidden')
                alert_success.classList.remove('hidden')
                page_obj.classList.add('watched');

                checkAllPagesWatched();
            }
            else {
                alert_danger.classList.remove('hidden')
                alert_success.classList.add('hidden')
            }
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
        document.getElementById('step_2').classList.remove('bg-warning', 'active')
        document.getElementById('step_2').classList.add('step-complete')
        document.getElementById('step_3').classList.remove('disabled')
        document.getElementById('step_3').classList.add('active', 'step_active', 'ramka-5')
        document.getElementById('main-alert').classList.remove('hidden')
    }
}

function alertsHide() {
    alert_danger.classList.add('hidden')
    alert_success.classList.add('hidden')
}

/* Vars */
let words = Array.from(document.getElementsByClassName('word'))
let paginator = Array.from(document.getElementsByClassName('pagination'))
let pages = Array.from(paginator[0].children).slice(1, -1)
let max_page = Number(Array.from(paginator[0].children).slice(-2)[0].id.split('_')[1])
const prev_btn = document.getElementById('prev_btn')
const next_btn = document.getElementById('next_btn')
const alert_success = document.getElementById('alert-success');
const alert_danger = document.getElementById('alert-danger');
const next_step = document.getElementById('step_3')

/* Handlers */
prev_btn.onclick = (event) => {
    alertsHide();
    prevPaginatorHandler(event);
    wordCheckHandlers();
}
pages.forEach(el => {
    el.onclick = (event) => {
        alertsHide();
        paginatorHandler(event);
        wordCheckHandlers();
    }
})
next_btn.onclick = (event) => {
    alertsHide();
    nextPaginatorHandler(event);
    wordCheckHandlers();
}

next_step.onclick = (event) => {
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
        console.dir(response.status)
        if (response.status != 200) {
            console.log('Ошибка отправки данных на сервер');
            event.preventDefault();
        }
    })
}

/* On start */
document.getElementById('page_1').classList.add('active', 'watched');
document.getElementById('step_1').classList.add('step-complete', 'text-light')
wordCheckHandlers();



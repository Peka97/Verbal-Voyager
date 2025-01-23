import { showToast } from '/static/pages/js/modules/toast_notification.js';
import { toNextStep } from './modules/next_step.js';
import { pagination, updatePagination } from './modules/pagination.js';
import { send_points } from './modules/send_points.js';
import { logging } from './modules/logging.js';

pagination.forEach(el => {
    el.onclick = (event) => {
        updatePagination(event);
    };
});


function checkAnswer() {
    let curr_page = Number(Array.from(document.getElementsByClassName('page-item active'))[0].id.split('_')[1]);
    let word = document.getElementById(`word_${curr_page}`);
    let input_el = word.children[1].children[0]
    let user_input = String(input_el.value).toLowerCase();
    let translate = String(input_el.id).toLowerCase();

    if (user_input === translate) {
        check_words[word.id] = true;
        input_el.classList.add('correct');
        input_el.classList.remove('wrong');
        logging(user_input, translate, 'correct');
 
        if (!checkAllAnswersTrue()) {
            showToast('Правильно! Переходи к следующему слову.');
        }
    }
    else {
        showToast('Неправильно, подумай ещё раз.');
        input_el.classList.remove('correct');
        input_el.classList.add('wrong');
        logging(user_input, translate, 'wrong');

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
        if (check_words[key] !== true) {
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
document.getElementById('word_1').classList.remove('hidden');
document.getElementById('page_1').classList.add('active', 'watched');
fillCheckWords();

const done_btn = document.getElementById('done-btn');
const toastTrigger = document.getElementById('liveToastBtn');
toastTrigger.addEventListener('click', () => {
    checkAnswer();
})

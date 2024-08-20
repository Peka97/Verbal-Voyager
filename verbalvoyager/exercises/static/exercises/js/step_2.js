import { showToast } from './modules/toast_notification.js';
import { toNextStep } from './modules/next_step.js';
import { pagination, updatePagination } from './modules/pagination.js';
import { send_points } from './modules/send_points.js';

pagination.forEach(el => {
    el.onclick = (event) => {
        updatePagination(event);
        updateWordCheckHandlers;
        checkAllWordsWatched(event);
    };
});
document.getElementById('step_1').classList.add('step-complete')
let words = [...document.getElementsByClassName('word__block')];
let points = words.length;
// const toastLiveExample = document.getElementById('liveToast');
// const toastBody = document.getElementById('toast-body');
updateWordCheckHandlers();

// Код для подсказок рядом с названием шага упражнения.
// let popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
// let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
//     return new bootstrap.Popover(popoverTriggerEl);
// });

function updateWordCheckHandlers() {
    let curr_page = Number(Array.from(document.getElementsByClassName('page-item active'))[0].id.split('_')[1])
    // let translates = Array.from(document.getElementById(`word_${curr_page}`).children).slice(1, )
    let translates = [... document.getElementsByClassName('word__block')]

    translates.forEach(el => {
        let btns_div = [...el.children].slice(1, )

        btns_div.forEach(btn_div => {
            let btn = btn_div.firstElementChild
            
            btn.onclick = () => {
                if ([...btn.classList].includes('answer')) {
                    console.log('answer')
                    let current_word_block = document.querySelector('div.word__block:not(.hidden)');
                    current_word_block.classList.add('watched');
    
                    if (!checkAllWordsWatched()) {
                        console.log('Не все слова просмотрены')
                        showToast('Правильно! Переходи к следующему слову.');
                    };
                }
                else {
                    console.log('Не answer')
                    showToast('Неверно, подумай ещё раз.');
    
                    if (points > 1) {
                        points--;
                    }
                }
            }        
        })
    })
}

function checkAllWordsWatched (event) {
    for (let i=0; i < words.length; i++) {
        if (!words[i].classList.contains('watched')) {
            return false;
        }
    }

    showToast('Запомнил слова? Тогда переходи к следующему шагу!');
    send_points('words', points);
    toNextStep(2);
    return true;
}
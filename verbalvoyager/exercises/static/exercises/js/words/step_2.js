import { showToast } from '/static/pages/js/modules/toast_notification.js';
import { toNextStep } from '../modules/next_step.js';
import { pagination, updatePagination } from '../modules/pagination.js';
import { send_points } from '../modules/send_points.js';

pagination.forEach(el => {
    el.onclick = (event) => {
        updatePagination(event);
        updateWordCheckHandlers();
        checkAllWordsWatched(event);
    };
});
let words = [...document.getElementsByClassName('word__block')];
let points = words.length;

updateWordCheckHandlers();

let wordBlocks = [... document.getElementsByClassName('word__block')]

function updateWordCheckHandlers() {
    let curr_page = Number(Array.from(document.getElementsByClassName('page-item active'))[0].id.split('_')[1])
    let translates = [...document.getElementById(`word_${curr_page}`).lastElementChild.children]

    translates.forEach(el => {
        let btn = el.firstElementChild
        
        btn.onclick = () => {
            if ([...btn.classList].includes('answer')) {
                let current_word_block = document.querySelector('div.word__block:not(.hidden)');
                current_word_block.classList.add('watched');

                if (!checkAllWordsWatched()) {
                    showToast('Правильно! Переходи к следующему слову.');
                };
            }
            else {
                if (!btn.classList.contains('wrong')) {
                    btn.classList.add('wrong');
                }

                showToast('Неверно, подумай ещё раз.');

                if (points > 1) {
                    points--;
                }
            }
        }        
    })
}


function checkAllWordsWatched (event) {
    for (let i=0; i < words.length; i++) {
        if (!words[i].classList.contains('watched')) {
            return false;
        }
    }

    showToast('Запомнил слова? Тогда переходи к следующему шагу!');
    toNextStep(2);
    send_points('words', points);
    return true;
}
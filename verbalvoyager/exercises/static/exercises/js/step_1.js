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
    showToast('Запомнил слова? Тогда переходи к следующему шагу!');
    send_points('words', points);
    toNextStep(1);
    return true;
}
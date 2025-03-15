import { showToast } from '/static/pages/js/modules/toast_notification.js';
import { toNextStep } from '../modules/next_step.js';
import { send_points } from '../modules/send_points.js';

document.getElementById('step_1').classList.add('step-complete')
document.getElementById('step_2').classList.add('step-complete')
const dropItems = document.getElementById('translates')
new Sortable(dropItems, {
  animation: 150,
  ghostClass: 'ghost',
  chosenClass: "chosen",
  dragClass: "sortable-drag"
});
let points = [... document.getElementsByClassName('word')].length;
const toastTrigger = document.getElementById('liveToastBtn');

if (toastTrigger) {
  toastTrigger.addEventListener('click', () => {
    checkAnswer();
  })
}

// Код для подсказок рядом с названием шага упражнения.
// let popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
// let popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
//     return new bootstrap.Popover(popoverTriggerEl);
// });

function checkAnswer (event) {
    let words = document.getElementById('words').children
    let trans = document.getElementById('translates').children

    for (let i = 0; i < words.length; i++) {
        if (words[i].id.slice(-1) !== trans[i].id.slice(-1)) {
            showToast('Неверно, подумай ещё раз.');

            if (points > 1) {
                points--;
            }
            return;
        }
    }
    
    showToast('Запомнил слова? Тогда переходи к следующему шагу!');
    toNextStep(3);
    send_points('words', points);
    }

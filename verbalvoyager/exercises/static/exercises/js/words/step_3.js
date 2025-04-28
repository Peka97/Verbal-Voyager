import { showToast } from '/static/pages/js/modules/toast_notification.js';
import { toNextStep } from '../modules/next_step.js';
import { send_points } from '../modules/send_points.js';

const dropItems = document.getElementById('translates')
new Sortable(dropItems, {
  animation: 150,
  swap : true,
  swapClass : "swap-highlight",
  ghostClass: "ghost",
  chosenClass: "chosen",
  dragClass: "sortable-drag",
  // handle: ".drag-handle",
});

let points = [... document.getElementsByClassName('word')].length;
const toastTrigger = document.getElementById('liveToastBtn');

if (toastTrigger) {
  toastTrigger.addEventListener('click', () => {
    checkAnswer();
  })
}

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

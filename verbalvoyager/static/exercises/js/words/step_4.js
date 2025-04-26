import { showToast } from '/static/pages/js/modules/toast_notification.js';
import { toNextStep } from '../modules/next_step.js';
import { pagination, updatePagination } from '../modules/pagination.js';
import { send_points } from '../modules/send_points_fix.js';
import { logging } from '../modules/logging.js';

document.getElementById('step_1').classList.add('step-complete')
document.getElementById('step_2').classList.add('step-complete')
document.getElementById('step_3').classList.add('step-complete')

pagination.forEach(el => {
    el.onclick = (event) => {
        updatePagination(event);
    };
});

const dropItems = [...document.querySelectorAll('.letter-container')];
dropItems.forEach(el => {
    new Sortable(el, {
        animation: 150,
        swap : true,
        swapClass : "swap-highlight",
        ghostClass: "ghost",
        chosenClass: "chosen",
        dragClass: "sortable-drag",
    });
})

let points = [... document.querySelectorAll('.word__block')].length;
const toastTrigger = document.getElementById('liveToastBtn');

if (toastTrigger) {
  toastTrigger.addEventListener('click', () => {
    checkAnswer();
  })
}

function checkAllWordsCorrect() {
    const wordBlockElements = [...document.querySelectorAll(".word__block")];

    for (let i in wordBlockElements) {
        if (!wordBlockElements[i].classList.contains('correct')) {
            return false;
        }
    }
    
    return true;
}

function getUserInput(letterElements) {
    return [...letterElements].map(element => element.innerText.replace(/\n/g, '')).join("")
}

function checkAnswer () {
    let currentWordBlockElement = document.querySelector(".word__block:not(.hidden)");
    const translateContainerElement = currentWordBlockElement.querySelector(".translate-container");
    const translate = translateContainerElement.dataset['word'];
    const letterContainerElements = translateContainerElement.children;

    let userInput;

    if (letterContainerElements.length > 1) {
        userInput = [...letterContainerElements].map(
            element => getUserInput(element.children)
        ).join(" ")
    } else {
        userInput = getUserInput(letterContainerElements);
    }

    if (userInput.toLowerCase() !== translate.toLowerCase()) {
        logging(userInput.toLowerCase(), translate.toLowerCase(), 'wrong');
        showToast('Неверно, подумай ещё раз.');

        translateContainerElement.classList.remove("correct");
        translateContainerElement.classList.add("wrong");

        if (points > 1) {
            points--;
        }
        return;

    } else {
        logging(userInput.toLowerCase(), translate.toLowerCase(), 'correct');

        translateContainerElement.classList.remove("wrong");
        translateContainerElement.classList.add("correct");
        currentWordBlockElement.classList.add('correct');
    }

    if (checkAllWordsCorrect() === true) {
        showToast('Запомнил слова? Тогда переходи к следующему шагу!');
        toNextStep(4);
        send_points('words', points);
    }
}

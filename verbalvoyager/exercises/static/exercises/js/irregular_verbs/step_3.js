import { showToast } from "/static/pages/js/modules/toast_notification.js";
import { pagination, updatePagination } from "../modules/pagination.js";
import { send_points } from "../modules/send_points.js";

pagination.forEach((el) => {
	el.onclick = (event) => {
		updatePagination(event);
	};
});
document.getElementById("step_1").classList.add("step-complete");
let words = [...document.getElementsByClassName("word__block")];
let points = words.length;

let wordRows = [...document.getElementsByClassName("word__block")];
let allWords = Array();

wordRows.forEach((wordRow) => {
	[...wordRow.children].forEach((wordCol) => {
		allWords.push(wordCol.innerText.replace(/\s+/g, ""));
	});
});

function getRandomWordId() {
	let idx = Math.floor(Math.random() * 3);
	return idx;
}

function shuffle(array) {
	var currentIndex = array.length,
		temporaryValue,
		randomIndex;

	while (0 !== currentIndex) {
		randomIndex = Math.floor(Math.random() * currentIndex);
		currentIndex -= 1;

		temporaryValue = array[currentIndex];
		array[currentIndex] = array[randomIndex];
		array[randomIndex] = temporaryValue;
	}

	return array;
}

function getRandomWords(exclude) {
	let wordsVariants = allWords.slice();
	wordsVariants.splice(wordsVariants.indexOf(exclude), 1);
	return wordsVariants.slice(0, 3);
}

function insertDropdownInWordRows() {
	for (let i = 0; i < wordRows.length; i++) {
		let currentWordRow = wordRows[i];
		let RandomWordIndexOne = getRandomWordId();
		let RandomWordIndexTwo;

		do {
			RandomWordIndexTwo = getRandomWordId();
		} while (RandomWordIndexOne === RandomWordIndexTwo);

		let choosenRandomWordOne = currentWordRow.children[RandomWordIndexOne];
		let choosenRandomWordTwo = currentWordRow.children[RandomWordIndexTwo];

		let currentWordOne = choosenRandomWordOne.innerText.replace(/\s+/g, "");
		let currentWordTwo = choosenRandomWordTwo.innerText.replace(/\s+/g, "");

		let wordVariantsOne = getRandomWords(currentWordOne);
		let wordVariantsTwo = getRandomWords(currentWordTwo);

		wordVariantsOne.push(currentWordOne);
		wordVariantsTwo.push(currentWordTwo);

		wordVariantsOne = shuffle(wordVariantsOne);
		wordVariantsTwo = shuffle(wordVariantsTwo);

		choosenRandomWordOne.innerHTML = `
        <div class="word__main menu">
            <div class="item" data-key="${currentWordOne}">
                <a href="#" class="menu-word-link">
                    <span class="word-rus">choose a word</span>
                    <svg viewBox="0 0 360 360" xml:space="preserve">
                        <g id="SVGRepo_iconCarrier">
                        <path id="XMLID_225_" d="M325.607,79.393c-5.857-5.857-15.355-5.858-21.213,0.001l-139.39,139.393L25.607,79.393 c-5.857-5.857-15.355-5.858-21.213,0.001c-5.858,5.858-5.858,15.355,0,21.213l150.004,150c2.813,2.813,6.628,4.393,10.606,4.393 s7.794-1.581,10.606-4.394l149.996-150C331.465,94.749,331.465,85.251,325.607,79.393z"></path>
                        </g>
                    </svg>
                </a>
                <div class="dropdown submenu">
                    <div class="submenu-item">
                        <a class="submenu-word-link" href="#">${wordVariantsOne[0]}</a>
                    </div>
                    <div class="submenu-item">
                        <a class="submenu-word-link" href="#">${wordVariantsOne[1]}</a>
                    </div>
                    <div class="submenu-item">
                        <a class="submenu-word-link" href="#">${wordVariantsOne[2]}</a>
                    </div>
                    <div class="submenu-item">
                        <a class="submenu-word-link" href="#">${wordVariantsOne[3]}</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
		choosenRandomWordTwo.innerHTML = `
        <div class="word__main menu">
            <div class="item" data-key="${currentWordTwo}">
                <a href="#" class="menu-word-link">
                    <span class="word-rus">choose a word</span>
                    <svg viewBox="0 0 360 360" xml:space="preserve">
                        <g id="SVGRepo_iconCarrier">
                        <path id="XMLID_225_" d="M325.607,79.393c-5.857-5.857-15.355-5.858-21.213,0.001l-139.39,139.393L25.607,79.393 c-5.857-5.857-15.355-5.858-21.213,0.001c-5.858,5.858-5.858,15.355,0,21.213l150.004,150c2.813,2.813,6.628,4.393,10.606,4.393 s7.794-1.581,10.606-4.394l149.996-150C331.465,94.749,331.465,85.251,325.607,79.393z"></path>
                        </g>
                    </svg>
                </a>
                <div class="dropdown submenu">
                    <div class="submenu-item">
                        <a class="submenu-word-link" href="#">${wordVariantsTwo[0]}</a>
                    </div>
                    <div class="submenu-item">
                        <a class="submenu-word-link" href="#">${wordVariantsTwo[1]}</a>
                    </div>
                    <div class="submenu-item">
                        <a class="submenu-word-link" href="#">${wordVariantsTwo[2]}</a>
                    </div>
                    <div class="submenu-item">
                        <a class="submenu-word-link" href="#">${wordVariantsTwo[3]}</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        `;
	}
}

wordRows.forEach((wordRow) => {
	wordRow.addEventListener("click", (event) => {
		event.preventDefault();

		let el = event.target;
		const menu = el.parentElement.parentElement.parentElement.parentElement;
		const key = el.parentElement.parentElement.parentElement.dataset.key.toLowerCase();
		const chosen = el.firstChild.data.toLowerCase();

		if (key != chosen) {
			menu.classList.remove("correct");
			menu.classList.add("wrong");
			if (points > 1) {
				points--;
			}
		} else {
			menu.firstElementChild.firstElementChild.firstElementChild.innerText = key;
			menu.classList.remove("wrong");
			menu.classList.add("correct");
		}

		allWordsCorrect();
	});
});

function allWordsCorrect() {
	let menus = [...document.getElementsByClassName("menu")];

	for (let i = 0; i < menus.length; i++) {
		if (!menus[i].classList.contains("correct")) {
			return false;
		}
	}

	send_points("irregular_verbs", points);
	showToast("Упражнение завершено! Переходи в Личный кабинет.");
	// toNextStep(2)
}

insertDropdownInWordRows();

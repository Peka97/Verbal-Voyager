import { showToast } from "/static/pages/js/modules/toast_notification.js";
import { toNextStep } from "../modules/next_step.js";
import { pagination, updatePagination } from "../modules/pagination.js";
import { send_points } from "../modules/send_points_fix.js";

pagination.forEach((el) => {
	el.onclick = (event) => {
		updatePagination(event);
		checkAllWordsWatched(event);
	};
});

let allWordsWatched = false;
let words = [...document.getElementsByClassName("word__block")];
let points = words.length;
words[0].classList.add("watched");
words[0].classList.remove("hidden");

function checkAllWordsWatched(event) {
	let current_word_block = document.querySelector("div.word__block:not(.hidden)");
	current_word_block.classList.add("watched");

	for (let i = 0; i < words.length; i++) {
		if (!words[i].classList.contains("watched")) {
			return false;
		}
	}
	if (!allWordsWatched) {
		showToast("Запомнил слова? Тогда переходи к следующему шагу!");
		toNextStep(1);
		allWordsWatched = true;
		send_points("words", points);
	}

	return true;
}

const allAudio = [...document.getElementsByClassName("sound__wrap")];
allAudio.forEach((block) => {
	block.firstElementChild.addEventListener("click", (e) => {
		let audio = block.lastElementChild;
		if (audio.paused) {
			audio.play();
		} else {
			audio.pause();
		}
	});
});

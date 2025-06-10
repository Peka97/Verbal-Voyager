document.addEventListener("DOMContentLoaded", function () {
	// Инициализация Sortable для каждого предложения
	document.querySelectorAll(".sentence-task").forEach((task) => {
		const sortableEl = task.querySelector(".sortable-words");
		// const feedbackEl = task.querySelector(".sentence-feedback");

		new Sortable(sortableEl, {
			animation: 150,
			swap: true,
			swapClass: "swap-highlight",
			ghostClass: "sortable-ghost",
			chosenClass: "sortable-chosen",
			onEnd: checkSentenceOrder,
		});

		function checkSentenceOrder() {
			const wordTiles = sortableEl.querySelectorAll(".word-tile");
			let allCorrect = true;

			wordTiles.forEach((tile, index) => {
				const correctPos = parseInt(tile.dataset.correctPosition);
				if (index === correctPos) {
					tile.classList.add("correct-position");
				} else {
					tile.classList.remove("correct-position");
					allCorrect = false;
				}
			});

			// if (allCorrect) {
			// 	feedbackEl.textContent = "Правильно! Предложение собрано верно.";
			// 	feedbackEl.className = "sentence-feedback correct";
			// } else {
			// 	feedbackEl.textContent = "Продолжайте собирать предложение...";
			// 	feedbackEl.className = "sentence-feedback incorrect";
			// }
		}

		// Первоначальная проверка
		shuffleAllSortableWords();
		checkSentenceOrder();
	});
});

function shuffleAllSortableWords() {
	document.querySelectorAll(".sortable-words").forEach((container) => {
		// Получаем все элементы для перемешивания (исключая элементы Sortable.js)
		const items = Array.from(container.children).filter(
			(el) => !el.classList.contains("sortable-ghost") && !el.classList.contains("sortable-chosen")
		);

		// Перемешиваем массив
		for (let i = items.length - 1; i > 0; i--) {
			const j = Math.floor(Math.random() * (i + 1));
			container.insertBefore(items[j], items[i]);
		}

		// Обновляем позиции всех элементов после перемешивания
		updatePositionsAfterShuffle(container);
	});
}

/**
 * Обновляет визуальные позиции элементов после перемешивания
 */
function updatePositionsAfterShuffle(container) {
	Array.from(container.children).forEach((item, index) => {
		// Пропускаем служебные элементы Sortable.js
		if (item.classList.contains("sortable-ghost") || item.classList.contains("sortable-chosen")) return;

		// Добавляем анимацию перемещения
		item.style.transition = "transform 0.3s ease";
		item.style.transform = "translate(0, 0)";
	});
}

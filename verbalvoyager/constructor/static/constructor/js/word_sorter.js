document.addEventListener("DOMContentLoaded", function () {
	console.log("DOM fully loaded and parsed");
	const words = document.querySelectorAll(".word");
	const dropzones = document.querySelectorAll(".words-dropzone");

	words.forEach((word) => {
		word.addEventListener("dragstart", handleDragStart);
		word.addEventListener("dragend", handleDragEnd);
	});

	dropzones.forEach((zone) => {
		zone.addEventListener("dragover", handleDragOver);
		zone.addEventListener("dragenter", handleDragEnter);
		zone.addEventListener("dragleave", handleDragLeave);
		zone.addEventListener("drop", handleDrop);
	});

	function handleDragStart(e) {
		e.dataTransfer.setData("text/plain", e.target.dataset.wordId);
		e.target.classList.add("dragging");
	}

	function handleDragEnd(e) {
		e.target.classList.remove("dragging");
	}

	function handleDragOver(e) {
		e.preventDefault();
	}

	function handleDragEnter(e) {
		e.preventDefault();
		e.target.classList.add("drag-over");
	}

	function handleDragLeave(e) {
		e.target.classList.remove("drag-over");
	}

	function handleDrop(e) {
		e.preventDefault();
		e.target.classList.remove("drag-over");

		const wordId = e.dataTransfer.getData("text/plain");
		const draggedWord = document.querySelector(`.word[data-word-id="${wordId}"]`);
		const targetCategoryId = e.target.closest(".category-words").dataset.categoryId;

		if (draggedWord) {
			// Удаляем слово из предыдущего места
			draggedWord.remove();

			// Добавляем в новую категорию
			e.target.appendChild(draggedWord);

			// Проверяем правильность категории
			if (draggedWord.dataset.categoryId === targetCategoryId) {
				draggedWord.classList.add("correct");
				draggedWord.classList.remove("incorrect");
			} else {
				draggedWord.classList.add("incorrect");
				draggedWord.classList.remove("correct");
			}
		}
	}
});

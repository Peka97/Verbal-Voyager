import { showToast } from "/static/pages/js/modules/toast_notification.js";

let currentModal;
let isEditMode = false;
let originalContents = {};
let hasChanges = false;

document.addEventListener("DOMContentLoaded", function () {
	// Получаем элементы
	const openBtnElements = document.querySelectorAll(".open-modal-btn");
	const closeBtnElements = document.querySelectorAll(".close-modal");
	const editBtnElements = document.querySelectorAll(".edit-modal");
	const saveBtnElements = document.querySelectorAll(".save-modal");

	// Открытие модального окна
	openBtnElements.forEach((btn) => {
		btn.addEventListener("click", function (event) {
			document.body.classList.add("body-no-scroll");
			const id = event.target.parentElement.id.split("_")[1];
			const modal = document.getElementById(`lesson_${id}_PlanModal`);
			currentModal = modal;
			currentModal.classList.remove("hidden");
		});
	});

	// Закрытие модального окна
	closeBtnElements.forEach((btn) => {
		btn.addEventListener("click", function () {
			onModalClose();
		});
	});

	// Редактирование плана урока
	editBtnElements.forEach((btn) => {
		btn.addEventListener("click", function (event) {
			toggleEditMode();
		});
	});

	// Сохранение плана урока
	saveBtnElements.forEach((btn) => {
		btn.addEventListener("click", function () {
			saveChanges();
		});
	});

	// Закрытие при клике вне окна
	window.addEventListener("click", function (event) {
		if (currentModal && event.target === currentModal) {
			onModalClose();
		}
	});
});

function toggleEditMode() {
	isEditMode = !isEditMode;

	if (isEditMode) {
		enableEditing();
	}
}

function enableEditing() {
	currentModal.querySelector("i.edit-modal").classList.add("hidden");
	currentModal.querySelector("i.save-modal").classList.remove("hidden");
	currentModal.classList.add("edit-mode");
	hasChanges = false;
	originalContents = {};

	// Сохраняем оригинальное содержимое
	currentModal.querySelectorAll(".aims-list li").forEach((li, index) => {
		originalContents[`aim_${index}`] = li.textContent;
	});

	originalContents.theme = currentModal.querySelector(".theme-badge").textContent;
	originalContents.materials = currentModal.querySelector(".materials-section .info-card p").textContent;
	originalContents.processes = currentModal.querySelector(".materials-section .info-card:last-child p").textContent;

	// Заменяем на поля ввода
	replaceWithInputFields();

	// Добавляем кнопки для управления целями и словами
	addManagementButtons();
}

function sendUpdateToServer(lesson_plan_id, dataToSend) {
	const siteName = window.location.href.split("/").slice(0, 3).join("/");
	let url = `${siteName}/lesson_plan/json/update/${lesson_plan_id}/`;
	let token = document.getElementsByName("csrfmiddlewaretoken")[0].defaultValue;

	if (!token) {
		console.log("Couldn't find token");
		return;
	}

	let data = {
		method: "POST",
		headers: {
			Accept: "application/json",
			"Content-Type": "application/json",
			"X-CSRFToken": token,
		},
		body: JSON.stringify(dataToSend),
	};

	fetch(url, data).then((resp) => {
		if (resp.ok) {
			hasChanges = false;
			showToast("План урока успешно обновлён.");
			return;
		} else {
			resp.json().then((data) => {
				console.dir(data.errors);
				const errors = Object.entries(data.errors)
					.map(([key, value]) => `${value}`)
					.join(".</br>");

				showToast(
					`
					Ошибка обновления плана урока. Код ${resp.status}.</br>
					Ошибки: ${errors}
					`
				);
			});
		}
	});
}

function exitEditMode(keepChanges) {
	currentModal.querySelector("i.save-modal").classList.add("hidden");
	currentModal.querySelector("i.edit-modal").classList.remove("hidden");
	currentModal.classList.remove("edit-mode");
	// currentModal.classList.add("hidden");

	if (!keepChanges) {
		// Восстанавливаем оригинальное содержимое
		restoreOriginalContents();
	} else {
		// При сохранении тоже нужно очистить кнопки удаления
		cleanUpDeleteButtons();
	}
	// Удаляем все добавленные кнопки
	removeManagementButtons();
	// Восстанавливаем оригинальные стили
	restoreOriginalStyle();
	// currentModal = undefined;
	isEditMode = false;
}

// Новая функция для очистки кнопок удаления
function cleanUpDeleteButtons() {
	// Очищаем кнопки удаления у целей
	currentModal.querySelectorAll(".aims-list li").forEach((li) => {
		const deleteBtn = li.querySelector(".delete-item-btn");
		if (deleteBtn) deleteBtn.remove();
	});

	// Очищаем кнопки удаления у слов
	currentModal.querySelectorAll(".word-tag").forEach((word) => {
		const deleteBtn = word.querySelector(".delete-item-btn");
		if (deleteBtn) deleteBtn.remove();
	});
}

function removeManagementButtons() {
	// Удаляем кнопки добавления целей
	const addAimButtons = currentModal.querySelectorAll(".add-aim-button");
	addAimButtons.forEach((btn) => btn.remove());

	// Удаляем кнопки добавления слов
	const addWordButtons = currentModal.querySelectorAll(".add-word-button");
	addWordButtons.forEach((btn) => btn.remove());

	// Удаляем кнопки удаления
	const deleteButtons = currentModal.querySelectorAll(".delete-item-btn");
	deleteButtons.forEach((btn) => btn.remove());
}

function replaceWithInputFields() {
	// Заменяем цели на input
	currentModal.querySelectorAll(".aims-list li").forEach((li, index) => {
		const input = document.createElement("input");
		input.type = "text";
		input.className = "edit-field";
		input.value = li.textContent;
		input.addEventListener("input", () => (hasChanges = true));
		li.innerHTML = "";
		li.appendChild(input);
	});

	// Заменяем тему на input
	const themeBadge = currentModal.querySelector(".theme-badge");
	const themeInput = document.createElement("input");
	themeInput.type = "text";
	themeInput.className = "edit-field";
	themeInput.value = themeBadge.textContent;
	themeInput.addEventListener("input", () => (hasChanges = true));
	themeBadge.innerHTML = "";
	themeBadge.appendChild(themeInput);

	// Заменяем материалы на textarea
	const materialsCard = currentModal.querySelector(".materials-list p");
	const materialsInput = document.createElement("textarea");
	materialsInput.className = "edit-area";
	materialsInput.value = materialsCard.textContent;
	materialsInput.addEventListener("input", () => (hasChanges = true));
	materialsCard.innerHTML = "";
	materialsCard.appendChild(materialsInput);

	// Заменяем процессы на textarea
	const processesCard = currentModal.querySelector(".process-list p");
	const processesInput = document.createElement("textarea");
	processesInput.className = "edit-area";
	processesInput.value = processesCard.textContent;
	processesInput.addEventListener("input", () => (hasChanges = true));
	processesCard.innerHTML = "";
	processesCard.appendChild(processesInput);
}

function addManagementButtons() {
	// Добавляем кнопки удаления и добавления для основных целей
	addAimManagementButtons(".main-aims", "Добавить");

	// Добавляем кнопки удаления и добавления для подзадач
	addAimManagementButtons(".subsidiary-aims", "Добавить");

	// Добавляем кнопки удаления и добавления для новых слов
	addWordManagementButtons();
}

function addAimManagementButtons(selector, addButtonText) {
	const aimSection = currentModal.querySelector(selector);
	const aimsList = aimSection.querySelector(".aims-list");

	// Добавляем крестики к существующим целям
	aimsList.querySelectorAll("li").forEach((li) => {
		addDeleteButton(li, () => {
			li.remove();
			hasChanges = true;
		});
	});

	// Добавляем кнопку добавления новой цели
	const addButton = document.createElement("button");
	addButton.className = "add-aim-button";
	addButton.textContent = addButtonText;
	addButton.addEventListener("click", () => {
		const newLi = document.createElement("li");
		const input = document.createElement("input");
		input.type = "text";
		input.className = "edit-field";
		input.addEventListener("input", () => (hasChanges = true));

		newLi.appendChild(input);
		addDeleteButton(newLi, () => {
			newLi.remove();
			hasChanges = true;
		});

		aimsList.appendChild(newLi);
		input.focus();
		hasChanges = true;
	});

	aimSection.appendChild(addButton);
}

function addWordManagementButtons() {
	const wordsCloud = currentModal.querySelector(".words-cloud");

	// Добавляем крестики к существующим словам
	wordsCloud.querySelectorAll(".word-tag").forEach((word) => {
		addDeleteButton(word, () => {
			word.remove();
			hasChanges = true;
		});
	});

	// Создаем контейнер для слов (без кнопки)
	const wordsContainer = document.createElement("div");
	wordsContainer.className = "words-container";

	// Переносим все слова в контейнер
	const wordTags = Array.from(wordsCloud.querySelectorAll(".word-tag"));
	wordTags.forEach((word) => {
		wordsContainer.appendChild(word);
	});

	// Очищаем wordsCloud и добавляем сначала контейнер со словами, потом кнопку
	wordsCloud.innerHTML = "";
	wordsCloud.appendChild(wordsContainer);

	// Добавляем кнопку добавления нового слова
	const addButton = document.createElement("button");
	addButton.className = "add-word-button";
	addButton.textContent = "Добавить";
	addButton.addEventListener("click", () => {
		const newWord = document.createElement("span");
		newWord.className = "word-tag";

		const input = document.createElement("input");
		input.type = "text";
		input.className = "edit-field word-input";
		input.addEventListener("input", () => (hasChanges = true));

		newWord.appendChild(input);
		addDeleteButton(newWord, () => {
			newWord.remove();
			hasChanges = true;
		});

		// Добавляем новое слово в контейнер слов
		wordsContainer.appendChild(newWord);
		input.focus();
		hasChanges = true;
	});

	wordsCloud.appendChild(addButton);
}

function addDeleteButton(element, onClick) {
	const deleteBtn = document.createElement("span");
	deleteBtn.className = "delete-item-btn";
	deleteBtn.innerHTML = "&times;";
	deleteBtn.addEventListener("click", (e) => {
		e.stopPropagation();
		onClick();
	});
	element.appendChild(deleteBtn);
}

function restoreOriginalContents() {
	// Восстанавливаем цели (удаляем input и кнопки удаления)
	currentModal.querySelectorAll(".aims-list li").forEach((li, index) => {
		if (li.querySelector("input")) {
			li.textContent = originalContents[`aim_${index}`] || "";
		}
		const deleteBtn = li.querySelector(".delete-item-btn");
		if (deleteBtn) deleteBtn.remove();
	});

	// Восстанавливаем слова (удаляем input и кнопки удаления)
	currentModal.querySelectorAll(".word-tag").forEach((word, index) => {
		if (word.querySelector("input")) {
			word.textContent = originalContents[`word_${index}`] || "";
		}
		const deleteBtn = word.querySelector(".delete-item-btn");
		if (deleteBtn) deleteBtn.remove();
	});

	// Восстанавливаем тему
	const themeBadge = currentModal.querySelector(".theme-badge");
	if (themeBadge.querySelector("input")) {
		themeBadge.textContent = originalContents.theme;
	}

	// Восстанавливаем материалы
	const materialsCard = currentModal.querySelector(".materials-list p");
	if (materialsCard.querySelector("textarea")) {
		materialsCard.textContent = originalContents.materials;
	}

	// Восстанавливаем процессы
	const processesCard = currentModal.querySelector(".process-list p");
	if (processesCard.querySelector("textarea")) {
		processesCard.textContent = originalContents.processes;
	}
}

function restoreOriginalStyle() {
	currentModal.querySelectorAll(".edit-field").forEach((input) => {
		input.classList.remove("edit-field");
	});

	currentModal.querySelectorAll(".edit-area").forEach((textarea) => {
		textarea.classList.remove("edit-area");
	});
}

function saveChanges() {
	if (!hasChanges) {
		if (confirm("Нет изменений для сохранения. Хотите выйти из режима редактирования?")) {
			exitEditMode(false);
			return;
		}
	}

	// Удаляем все пустые поля слов перед сохранением и убираем кнопки удаления
	currentModal.querySelectorAll(".word-tag").forEach((word) => {
		const deleteBtn = word.querySelector(".delete-item-btn");
		word.removeChild(deleteBtn);
		const input = word.querySelector("input");
		if (input && !input.value.trim()) {
			word.remove();
		}
	});

	// Собираем текущие значения
	const currentValues = {
		theme:
			currentModal.querySelector(".theme-badge input")?.value || currentModal.querySelector(".theme-badge").textContent,
		main_aims: [],
		subsidiary_aims: [],
		new_vocabulary: [],
		materials:
			currentModal.querySelector(".materials-list p textarea")?.value ||
			currentModal.querySelector(".materials-list p").textContent,
		processes:
			currentModal.querySelector(".process-list p textarea")?.value ||
			currentModal.querySelector(".process-list p").textContent,
	};

	// Собираем основные цели
	currentModal.querySelectorAll(".main-aims .aims-list li").forEach((li) => {
		const deleteBtn = li.querySelector(".delete-item-btn");
		li.removeChild(deleteBtn);

		const input = li.querySelector("input");
		if (input && !input.value.trim()) {
			li.remove();
		} else {
			const value = input?.value || li.textContent;
			currentValues.main_aims.push(value);
		}
	});

	// Собираем подзадачи
	currentModal.querySelectorAll(".subsidiary-aims .aims-list li").forEach((li) => {
		const deleteBtn = li.querySelector(".delete-item-btn");
		li.removeChild(deleteBtn);

		const input = li.querySelector("input");
		if (input && !input.value.trim()) {
			li.remove();
		} else {
			const value = input?.value || li.textContent;
			currentValues.subsidiary_aims.push(value);
		}
	});

	// Собираем новые слова
	currentModal.querySelectorAll(".word-tag").forEach((word) => {
		const value = word.querySelector("input")?.value || word.textContent;
		console.dir(word);
		if (value.trim()) {
			currentValues.new_vocabulary.push(value);
		}
	});

	// Обновляем DOM с новыми значениями
	updateContent(currentValues);

	// Отправляем на сервер
	const lessonPlanDID = currentModal.id.split("_")[1];
	sendUpdateToServer(lessonPlanDID, currentValues);

	// Выходим из режима редактирования
	exitEditMode(true);
}

function updateContent(values) {
	// Обновляем цели
	currentModal.querySelectorAll(".main-aims .aims-list li").forEach((li, index) => {
		li.textContent = values.main_aims[index];
	});

	currentModal.querySelectorAll(".subsidiary-aims .aims-list li").forEach((li, index) => {
		li.textContent = values.subsidiary_aims[index];
	});

	// Обновляем тему
	currentModal.querySelector(".theme-badge").textContent = values.theme;

	// Обновляем слова
	const wordsCloud = currentModal.querySelector(".words-cloud");
	wordsCloud.innerHTML = "";
	values.new_vocabulary.forEach((word) => {
		const wordTag = document.createElement("span");
		wordTag.className = "word-tag";
		wordTag.textContent = word;
		wordsCloud.appendChild(wordTag);
	});

	// Обновляем материалы
	currentModal.querySelector(".materials-list p").textContent = values.materials;

	// Обновляем процессы
	currentModal.querySelector(".process-list p").textContent = values.processes;
}

function onModalClose() {
	if (isEditMode && hasChanges) {
		if (confirm("У вас есть несохранённые изменения. Закрыть без сохранения?")) {
			exitEditMode(false); // Сбросить изменения
			currentModal.classList.add("hidden");
			currentModal = undefined;
		}
	} else {
		exitEditMode(false);
		currentModal.classList.add("hidden");
		currentModal = undefined;
		document.body.classList.remove("body-no-scroll");
	}
}

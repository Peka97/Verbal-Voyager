import { processSentence } from "/static/constructor/js/compromise.js";

const state = {
	selectedItems: [],
	exerciseTypes: {},
};

document.addEventListener("DOMContentLoaded", function () {
	const autocompleteWordsInput = document.querySelector(".autocomplete-input");
	const dropdown = document.querySelector(".autocomplete-dropdown");
	const selectedItemsContainer = document.querySelector(".selected-items");
	const itemElements = [...dropdown.querySelectorAll(".autocomplete-item")];
	const exerciseTypes = [...document.querySelectorAll(".exercise-tile")];
	const data = itemElements.map((item) => ({
		id: item.dataset.id,
		name: item.textContent.trim(),
	}));

	// Инициализация данных для конструктора
	if (window.lessonData) {
		document.getElementById("constructor-name").value = window.lessonData.constructorName;
		document.getElementById("lesson-title").value = window.lessonData.title;
		document.getElementById("lesson-description").value = window.lessonData.description;

		// Загрузка выбранных слов
		window.lessonData.wordIds.forEach((wordId) => {
			const wordItem = document.querySelector(`.autocomplete-item[data-id="${wordId}"]`);
			if (wordItem) addSelectedWord(wordItem);
		});

		// Загрузка структуры упражнений
		if (window.lessonData.structure) {
			window.lessonData.structure.forEach((module) => {
				addModuleToStructure(module);
			});
		}
	}

	exerciseTypes.forEach((item) => {
		state.exerciseTypes[item.dataset.id] = {
			name: item.dataset.name,
			description: item.dataset.description,
		};
	});

	// 1. Выбор слов
	initAutocompleteWords();

	// 2. Модальное окно для выбора упражнений
	const modal = initModal();

	// 3. Выбор типа упражнения
	addTileHandlers();

	// 4. Сортировка упражнений
	initSortable();

	// 5. Сохранение набора
	addSaveLessonHandlers();

	// Helpers

	function initAutocompleteWords() {
		// Обработчик ввода текста
		autocompleteWordsInput.addEventListener("input", function () {
			const searchTerm = this.value.toLowerCase();

			if (searchTerm.length === 0) {
				dropdown.classList.remove("show");
				return;
			}

			const filteredItems = data
				.filter(
					(item) =>
						!state.selectedItems.some((selected) => selected.id === item.id) &&
						item.name.toLowerCase().includes(searchTerm)
				)
				.sort((a, b) => {
					const aIsExact = a.name.toLowerCase() === searchTerm;
					const bIsExact = b.name.toLowerCase() === searchTerm;
					if (aIsExact && !bIsExact) return -1;
					if (!aIsExact && bIsExact) return 1;
					return a.name.localeCompare(b.name);
				})
				.slice(0, 10);

			renderDropdown(filteredItems);
		});

		// Обработчик клика вне поля ввода
		document.addEventListener("click", function (e) {
			if (!e.target.closest(".autocomplete-container")) {
				dropdown.classList.remove("show");
			}
		});

		// Обработчик фокуса на поле ввода
		autocompleteWordsInput.addEventListener("focus", function () {
			// Скрываем изначальные элементы при фокусе
			dropdown.innerHTML = "";
			if (this.value.length > 0) {
				dropdown.classList.add("show");
			}
		});

		// Рендер выпадающего списка
		function renderDropdown(items) {
			dropdown.innerHTML =
				items.length === 0
					? '<div class="autocomplete-item">No results found</div>'
					: items
							.map(
								(item) => `
                    <div class="autocomplete-item" data-id="${item.id}">
                        ${item.name}
                        ${
													item.name.toLowerCase() === autocompleteWordsInput.value.toLowerCase()
														? '<span class="exact-match-badge"></span>'
														: ""
												}
                    </div>
                `
							)
							.join("");

			if (items.length > 0) {
				dropdown.classList.add("show");
			} else {
				dropdown.classList.remove("show");
			}
		}

		// Делегирование событий для выбора элементов
		dropdown.addEventListener("click", function (e) {
			const itemElement = e.target.closest(".autocomplete-item");
			if (!itemElement) return;

			const id = itemElement.dataset.id;
			const name = itemElement.textContent.trim();

			// Проверяем, не добавлен ли уже этот элемент
			if (!state.selectedItems.some((item) => item.id === id)) {
				state.selectedItems.push({ id, name });
				renderSelectedItems();
				autocompleteWordsInput.value = "";
				dropdown.classList.remove("show");
				autocompleteWordsInput.focus();
			}
		});

		// Рендер выбранных элементов
		function renderSelectedItems() {
			selectedItemsContainer.innerHTML = state.selectedItems
				.map(
					(item) => `
                <div class="selected-tag">
                    ${item.name}
                    <button type="button" class="remove-word" data-id="${item.id}">&times;</button>
                </div>
            `
				)
				.join("");

			// Обработчики удаления
			document.querySelectorAll(".selected-tag button").forEach((button) => {
				button.addEventListener("click", function (e) {
					e.stopPropagation();
					const id = this.dataset.id;
					state.selectedItems = state.selectedItems.filter((item) => item.id !== id);
					renderSelectedItems();
				});
			});
		}
	}

	function initModal() {
		const modal = document.getElementById("module-modal");
		const addBtn = document.getElementById("add-module-btn");
		const closeBtn = document.querySelector(".close");

		// Открытие модального окна
		addBtn.addEventListener("click", function () {
			if (state.selectedItems.length === 0) {
				alert("Сначала выберите слова для изучения!");
				return;
			}
			modal.style.display = "block";
		});

		// Закрытие модального окна
		closeBtn.addEventListener("click", function () {
			modal.style.display = "none";
		});

		// Закрытие при клике вне окна
		window.addEventListener("click", function (e) {
			if (e.target === modal) {
				modal.style.display = "none";
			}
		});

		return modal;
	}

	function addTileHandlers() {
		document.querySelectorAll(".exercise-tile").forEach((tile) => {
			tile.addEventListener("click", function () {
				const typeId = this.dataset.id;
				const typeCode = this.dataset.code;
				const typeData = state.exerciseTypes[typeId];

				// Определяем, куда добавлять новый модуль (в корень или в выбранный раздел)
				const targetList = document.querySelector(".sortable-active") || document.getElementById("module-list");

				const li = document.createElement("li");
				li.dataset.id = typeId;
				li.dataset.type = typeCode;

				console.log(typeCode);

				// В зависимости от типа создаем разный контент
				renderModuleContent(li, typeCode, typeData);

				addModuleHandlers(li, typeCode, typeData);

				targetList.appendChild(li);
				modal.style.display = "none";
			});
		});
	}

	function renderModuleContent(li, typeCode, typeData) {
		switch (typeCode) {
			case "section":
				const sectionId = `section-${Date.now()}`;
				li.dataset.sectionId = sectionId;
				li.innerHTML = `
                        <div class="module-content">
                            <div class="module-header">
                                <strong>${typeData.name}</strong>
                                <span class="section-title">Новый раздел</span>
                                <div class="module-actions">
                                    <button class="edit-module">✏️</button>
                                    <button class="remove-exercise">×</button>
                                </div>
                            </div>
                            <ul class="nested-module-list" data-section-id="${sectionId}"></ul>
                        </div>
                        <div class="edit-form" style="display: none;">
                            <input type="text" class="edit-section-title" placeholder="Название раздела">
                            <button class="save-edit">Сохранить</button>
                            <button class="cancel-edit">Отмена</button>
                        </div>
                    `;
				initNestedSortable(li.querySelector(".nested-module-list"));

				break;

			case "text":
				li.innerHTML = `
                    <div class="module-content">
                        <div class="module-header">
                            <strong>${typeData.name}</strong>
                            <div class="module-actions">
                                <button class="edit-module">✏️</button>
                                <button class="remove-exercise">×</button>
                            </div>
                        </div>
                        <div class="text-preview"></div>
                    </div>
                    <div class="edit-form" style="display: none;">
                        <textarea class="edit-text-content" placeholder="Введите текст..."></textarea>
                        <button class="save-edit">Сохранить</button>
                        <button class="cancel-edit">Отмена</button>
                    </div>
                `;
				break;

			case "video_url":
				li.innerHTML = `
                    <div class="module-content">
                        <div class="module-header">
                            <strong>${typeData.name}</strong>
                            <div class="module-actions">
                                <button class="edit-module">✏️</button>
                                <button class="remove-exercise">×</button>
                            </div>
                        </div>
                        <div class="video-preview"></div>
                    </div>
                    <div class="edit-form" style="display: none;">
                        <input type="url" class="edit-video-url" placeholder="https://youtube.com/...">
                        <button class="save-edit">Сохранить</button>
                        <button class="cancel-edit">Отмена</button>
                    </div>
                `;
				break;

			case "document":
				li.innerHTML = `
						<div class="module-content">
							<div class="module-header">
								<strong>${typeData.name}</strong>
								<div class="module-actions">
									<button class="edit-module">✏️</button>
									<button class="remove-exercise">×</button>
								</div>
							</div>
							<div class="document-preview"></div>
						</div>
						<div class="edit-form" style="display: none;">
							<div class="form-group">
								<label>Название документа:</label>
								<input type="text" class="edit-document-name" placeholder="Введите название">
							</div>
							<div class="form-group">
								<label>Файл документа:</label>
								<input type="file" class="edit-document-file">
							</div>
							<button class="save-edit">Сохранить</button>
							<button class="cancel-edit">Отмена</button>
						</div>
    					`;
				break;
			case "word_sorter":
				li.innerHTML = `
						<div class="module-content">
							<div class="module-header">
								<strong>${typeData.name}</strong>
								<div class="module-actions">
									<button class="edit-module">✏️</button>
									<button class="remove-exercise">×</button>
								</div>
							</div>
							<div class="word-sorter-preview">
								<p>Категории не заданы</p>
							</div>
						</div>
						<div class="edit-form" style="display: none;">
							<div class="categories-container">
								<h4>Категории:</h4>
								<div class="categories-list"></div>
								<button type="button" class="add-category-btn">+ Добавить категорию</button>
							</div>
							<div class="words-assignment">
								<h4>Распределение слов:</h4>
								<div class="words-list"></div>
							</div>
							<button class="save-edit">Сохранить</button>
							<button class="cancel-edit">Отмена</button>
						</div>
					`;
				break;

			case "sentence_builder":
				li.innerHTML = `
						<div class="module-content">
							<div class="module-header">
								<strong>${typeData.name}</strong>
								<div class="module-actions">
									<button class="edit-module">✏️</button>
									<button class="remove-exercise">×</button>
								</div>
							</div>
							<div class="sentence-builder-preview">
								<p>Предложения не заданы</p>
							</div>
						</div>
						<div class="sentence-builder edit-form" style="display: none;">
							<div class="sentence-source-toggle">
								<label>
									<input type="radio" name="sentence_source_${Date.now()}" value="manual" checked>
									Задать вручную
								</label>
								<label>
									<input type="radio" name="sentence_source_${Date.now()}" value="database">
									Загрузить из базы данных
								</label>
							</div>
							
							<div class="manual-sentences-container">
								<h4>Ручной ввод предложений:</h4>
								<div class="sentences-list"></div>
								<button type="button" class="add-sentence-btn">+ Добавить предложение</button>
							</div>
							
							<div class="database-sentences-container" style="display: none;">
								<h4>Примеры из базы данных:</h4>
								<div class="database-examples-list"></div>
								<button type="button" class="load-examples-btn">Загрузить примеры</button>
							</div>
							
							<button class="save-edit">Сохранить</button>
							<button class="cancel-edit">Отмена</button>
						</div>
					`;
				break;

			default: // Стандартные упражнения
				li.innerHTML = `
						<div class="module-content">
							<div class="module-header">
								<strong>${typeData.name}</strong>
								<small>${typeData.description}</small>
							</div>
							<button class="remove-exercise">×</button>
						</div>
					`;
				li.draggable = true;
		}
	}

	function addModuleHandlers(li, typeCode, typeData) {
		const moduleContent = li.querySelector(".module-content");
		const editForm = li.querySelector(".edit-form");

		// Общие обработчики для всех типов
		li.querySelector(".remove-exercise")?.addEventListener("click", function (e) {
			e.stopPropagation();
			li.remove();
		});
		li.querySelector(".cancel-edit")?.addEventListener("click", () => {
			moduleContent.style.display = "block";
			editForm.style.display = "none";
		});

		switch (typeCode) {
			case "section":
				addSectionHandlers(li);
				break;
			case "sentence_builder":
				addSentenceBuilderHandlers(li);
				break;
			case "word_sorter":
				addWordSorterHandlers(li);
				break;
			case "text":
				addTextHandlers(li, moduleContent, editForm);
				break;
			case "video_url":
				addVideoUrlHandlers(li, moduleContent, editForm);
				break;
			case "document":
				addDocumentHandlers(li, moduleContent, editForm);
				break;
		}
	}

	function addSectionHandlers(li) {
		const editBtn = li.querySelector(".edit-module");
		const saveBtn = li.querySelector(".save-edit");
		const cancelBtn = li.querySelector(".cancel-edit");
		const title = li.querySelector(".section-title");
		const editForm = li.querySelector(".edit-form");
		const editInput = editForm?.querySelector(".edit-section-title");

		if (editBtn && saveBtn && cancelBtn && title && editForm && editInput) {
			// Редактирование
			editBtn.addEventListener("click", () => {
				editInput.value = title.textContent;
				editForm.style.display = "block";
			});

			// Сохранение
			saveBtn.addEventListener("click", () => {
				title.textContent = editInput.value;
				editForm.style.display = "none";
			});

			// Отмена
			cancelBtn.addEventListener("click", () => {
				editForm.style.display = "none";
			});
		}
	}

	function addSentenceBuilderHandlers(li) {
		const moduleContent = li.querySelector(".module-content");
		const editForm = li.querySelector(".edit-form");
		const preview = li.querySelector(".sentence-builder-preview");
		const manualContainer = li.querySelector(".manual-sentences-container");
		const dbContainer = li.querySelector(".database-sentences-container");
		const toggleRadios = li.querySelectorAll(".sentence-source-toggle input[type='radio']");

		// Восстановление сохраненных данных
		let sentences;
		try {
			sentences = JSON.parse(li.dataset.sentences || "[]");
		} catch (e) {
			console.error("Error parsing sentences", e);
		}

		// Переключение между режимами ввода
		toggleRadios.forEach((radio) => {
			radio.addEventListener("change", function () {
				if (this.value === "manual") {
					manualContainer.style.display = "block";
					dbContainer.style.display = "none";
				} else {
					manualContainer.style.display = "none";
					dbContainer.style.display = "block";
					li.querySelector(".database-examples-list").innerHTML = "";
				}
			});
		});
		// Функция проверки, содержит ли предложение хотя бы одно выбранное слово
		function containsSelectedWords(originalSentence) {
			let isValid;
			let sentence;

			if (state.selectedItems.length === 0) {
				isValid = false;
				sentence = originalSentence;
			} else {
				const selectedWords = state.selectedItems.map((item) => item.name.toLowerCase());
				const result = processSentence(originalSentence, selectedWords);

				isValid = result.found;
				sentence = result.processedSentence;
			}

			return {
				found: isValid,
				sentence: sentence,
			};
		}

		// Функция рендера списка предложений
		function renderSentencesList() {
			const container = li.querySelector(".sentences-list");
			container.innerHTML = "";

			console.dir(sentences);

			sentences.forEach((sentence, index) => {
				const sentenceEl = document.createElement("div");
				sentenceEl.className = "sentence-item";

				const { found: isValid, sentence: processedSentence } = containsSelectedWords(sentence);

				console.dir(sentence);
				console.dir(processedSentence);
				console.dir(isValid);

				sentence = processedSentence;

				sentenceEl.innerHTML = `
					<textarea class="sentence-input" placeholder="Введите предложение..." 
						${!isValid ? 'style="border-color: red;"' : ""}>${sentence}</textarea>
					<button type="button" class="remove-sentence-btn" data-index="${index}">×</button>
					${!isValid ? '<div class="error-message">Предложение не содержит выбранных слов</div>' : ""}
				`;

				container.appendChild(sentenceEl);

				// Обработчик изменения текста предложения
				sentenceEl.querySelector(".sentence-input").addEventListener("input", function () {
					sentences[index] = this.value;
					const { found: isValidNow, sentence: newSentenceText } = containsSelectedWords(this.value);

					if (isValidNow) {
						this.value = newSentenceText;
						this.style.borderColor = "";
						const errorMsg = sentenceEl.querySelector(".error-message");
						if (errorMsg) errorMsg.remove();
					} else {
						this.style.borderColor = "red";
						if (!sentenceEl.querySelector(".error-message")) {
							const errorMsg = document.createElement("div");
							errorMsg.className = "error-message";
							errorMsg.textContent = "Предложение не содержит выбранных слов";
							sentenceEl.appendChild(errorMsg);
						}
					}
				});

				// Обработчик удаления предложения
				sentenceEl.querySelector(".remove-sentence-btn").addEventListener("click", function () {
					sentences.splice(index, 1);
					renderSentencesList();
				});
			});
		}
		// Добавление нового предложения
		li.querySelector(".add-sentence-btn")?.addEventListener("click", function () {
			const newSentenceEl = document.createElement("div");
			newSentenceEl.className = "sentence-item";
			newSentenceEl.innerHTML = `
				<textarea class="sentence-input" placeholder="Введите предложение..."></textarea>
				<button type="button" class="remove-sentence-btn">×</button>
			`;

			li.querySelector(".sentences-list").appendChild(newSentenceEl);

			// Focus the new textarea
			const textarea = newSentenceEl.querySelector(".sentence-input");
			textarea.focus();

			// Handle changes to the new sentence
			textarea.addEventListener("input", function () {
				const { found, sentence: newSentenceText } = containsSelectedWords(this.value);

				if (found) {
					// if (!sentences.includes(newSentenceText)) {
					// 	console.dir("PUSH");
					// 	sentences.push(newSentenceText);
					// }
					this.style.borderColor = "";
					newSentenceEl.querySelector(".error-message")?.remove();
				} else {
					this.style.borderColor = "red";
					if (!newSentenceEl.querySelector(".error-message")) {
						const errorMsg = document.createElement("div");
						errorMsg.className = "error-message";
						errorMsg.textContent = "Предложение не содержит выбранных слов";
						newSentenceEl.appendChild(errorMsg);
					}
				}
			});

			// Handle removal
			newSentenceEl.querySelector(".remove-sentence-btn").addEventListener("click", function () {
				const text = textarea.value.trim();
				if (text) {
					sentences = sentences.filter((s) => s !== text);
				}
				newSentenceEl.remove();
			});
		});

		// Загрузка примеров из базы данных
		li.querySelector(".load-examples-btn")?.addEventListener("click", async function () {
			if (state.selectedItems.length === 0) {
				alert("Сначала выберите слова для изучения!");
				return;
			}

			const wordIds = state.selectedItems.map((item) => item.id);
			const examplesList = li.querySelector(".database-examples-list");
			examplesList.innerHTML = "<p>Загрузка примеров...</p>";

			try {
				const response = await fetch(`/constructor/word-examples/?word_ids=${wordIds.join(",")}`, {
					headers: {
						"X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
					},
				});
				const data = await response.json();

				if (data.examples?.length > 0) {
					examplesList.innerHTML = "";

					data.examples.forEach((example) => {
						const exampleEl = document.createElement("div");
						exampleEl.className = "example-item";
						exampleEl.innerHTML = `
                        <label>
                            <input type="checkbox" class="example-checkbox" data-text="${example.text}">
                            <div class="example-text">${example.text}</div>
                            <div class="example-translation">${example.translation || ""}</div>
                        </label>
                    `;
						examplesList.appendChild(exampleEl);
					});

					// Add button to confirm selection
					const addSelectedBtn = document.createElement("button");
					addSelectedBtn.type = "button";
					addSelectedBtn.className = "add-selected-examples-btn";
					addSelectedBtn.textContent = "Добавить выбранные";
					examplesList.appendChild(addSelectedBtn);

					addSelectedBtn.addEventListener("click", function () {
						const checkedExamples = [...examplesList.querySelectorAll(".example-checkbox:checked")];
						if (checkedExamples.length === 0) {
							alert("Выберите хотя бы один пример!");
							return;
						}

						checkedExamples.forEach((checkbox) => {
							let text = checkbox.dataset.text;

							const checkWordsContain = containsSelectedWords(text, state.selectedItems);
							const found = checkWordsContain.found;
							const newSentenceText = checkWordsContain.sentence;

							// const { found, newSentenceText } = ;
							console.log(`Original text: ${text}`);
							console.log(`Checked text: ${newSentenceText}`);
							console.log(!sentences.includes(text));
							console.log(!sentences.includes(newSentenceText));
							console.log(found);

							if (sentences.includes(text) && !sentences.includes(newSentenceText)) {
								// delete sentences[sentences.findIndex(sentences)];
							}

							if (!sentences.includes(text) && !sentences.includes(newSentenceText) && found) {
								text = newSentenceText;
								sentences.push(text);
							}
						});

						// Switch to manual view with loaded examples
						renderSentencesList();
						manualContainer.style.display = "block";
						dbContainer.style.display = "none";
						li.querySelector(".sentence-source-toggle input[value='manual']").checked = true;
					});
				} else {
					examplesList.innerHTML = "<p>Примеры не найдены</p>";
				}
			} catch (error) {
				console.error("Error loading examples:", error);
				examplesList.innerHTML = "<p>Ошибка загрузки примеров</p>";
			}
		});

		// Редактирование модуля
		li.querySelector(".edit-module").addEventListener("click", function () {
			moduleContent.style.display = "none";
			editForm.style.display = "block";
			console.dir(sentences);

			// Восстанавливаем выбранные предложения
			renderSentencesList();
		});

		// Сохранение модуля
		li.querySelector(".save-edit").addEventListener("click", function () {
			const sentencesListElements = document.querySelector(".sentence-builder").querySelectorAll(".sentence-item");
			if (li.querySelectorAll(".error-message").length > 0) {
				alert("Некоторые предложения не содержат выбранных слов. Пожалуйста, исправьте или удалите их.");
				return;
			}
			sentencesListElements.forEach((el) => {
				const text = el.querySelector(".sentence-input").value;
				if (text.length > 0 && !sentences.includes(text)) {
					sentences.push(text);
				}
			});
			// Проверяем, что все предложения содержат выбранные слова
			// const allValid = sentences.every((s) => containsSelectedWords(s));

			// if (!allValid) {
			// alert("Некоторые предложения не содержат выбранных слов. Пожалуйста, исправьте или удалите их.");
			// return;
			// }
			console.dir(sentences);

			// Сохраняем предложения
			li.dataset.sentences = JSON.stringify(sentences);

			// Обновляем превью
			preview.innerHTML = `
			<h4>Количество предложений: ${sentences.length}</h4>
			<ul>
				${sentences
					.slice(0, 3)
					.map((s) => `<li>${s}</li>`)
					.join("")}
				${sentences.length > 3 ? `<li>...и еще ${sentences.length - 3}</li>` : ""}
			</ul>
		`;

			moduleContent.style.display = "block";
			editForm.style.display = "none";
		});

		// Отмена редактирования
		li.querySelector(".cancel-edit").addEventListener("click", function () {
			moduleContent.style.display = "block";
			editForm.style.display = "none";
		});

		// Initial render if there are saved sentences
		if (sentences.length > 0) {
			preview.innerHTML = `
            <h4>Количество предложений: ${sentences.length}</h4>
            <ul>
                ${sentences
									.slice(0, 3)
									.map((s) => `<li>${s}</li>`)
									.join("")}
                ${sentences.length > 3 ? `<li>...и еще ${sentences.length - 3}</li>` : ""}
            </ul>
        `;
		}
	}

	function addWordSorterHandlers(li) {
		const moduleContent = li.querySelector(".module-content");
		const editForm = li.querySelector(".edit-form");
		const categoriesList = li.querySelector(".categories-list");
		const wordsList = li.querySelector(".words-list");
		const addCategoryBtn = li.querySelector(".add-category-btn");
		const preview = li.querySelector(".word-sorter-preview");

		// Глобальные переменные для этого модуля
		let wordAssignments = {};

		// Функция сохранения текущих назначений
		const saveAssignments = () => {
			const assignments = [];
			wordsList.querySelectorAll(".word-item").forEach((wordEl) => {
				const wordId = wordEl.dataset.id;
				const categoryId = wordEl.querySelector("select").value;
				if (categoryId) {
					assignments.push({ word_id: wordId, category_id: categoryId });
				}
			});
			li.dataset.assignments = JSON.stringify(assignments);
			wordAssignments = assignments.reduce((acc, item) => {
				acc[item.word_id] = item.category_id;
				return acc;
			}, {});
		};

		// Функция восстановления назначений
		const restoreAssignments = () => {
			try {
				const saved = JSON.parse(li.dataset.assignments || "[]");
				wordAssignments = saved.reduce((acc, item) => {
					acc[item.word_id] = item.category_id;
					return acc;
				}, {});
			} catch (e) {
				console.error("Error parsing assignments", e);
				wordAssignments = {};
			}
		};

		// Инициализация - сразу восстанавливаем сохраненные данные
		restoreAssignments();

		// Заполняем словами из выбранных
		const populateWords = () => {
			wordsList.innerHTML = "";
			state.selectedItems.forEach((word) => {
				const wordEl = document.createElement("div");
				wordEl.className = "word-item";
				wordEl.dataset.id = word.id;
				wordEl.textContent = word.name;

				const select = document.createElement("select");
				select.className = "category-select";

				// Опция по умолчанию
				const defaultOption = document.createElement("option");
				defaultOption.value = "";
				defaultOption.textContent = "Не выбрано";
				select.appendChild(defaultOption);

				// Добавляем категории
				categoriesList.querySelectorAll(".category-item").forEach((category) => {
					const option = document.createElement("option");
					option.value = category.dataset.id;
					option.textContent = category.querySelector("input").value;
					select.appendChild(option);
				});

				// Восстанавливаем сохраненный выбор
				if (wordAssignments[word.id]) {
					select.value = wordAssignments[word.id];
				}

				wordEl.appendChild(select);
				wordsList.appendChild(wordEl);

				// Обработчик изменения выбора
				select.addEventListener("change", () => {
					if (select.value) {
						wordAssignments[word.id] = select.value;
					} else {
						delete wordAssignments[word.id];
					}
				});
			});
		};

		// Добавление категории
		addCategoryBtn.addEventListener("click", () => {
			const categoryId = `cat_${Date.now()}`;
			const categoryEl = document.createElement("div");
			categoryEl.className = "category-item";
			categoryEl.dataset.id = categoryId;

			categoryEl.innerHTML = `
						<input type="text" placeholder="Название категории">
						<button type="button" class="remove-category-btn">×</button>
					`;

			categoryEl.querySelector(".remove-category-btn").addEventListener("click", () => {
				// Удаляем назначения для удаляемой категории
				Object.keys(wordAssignments).forEach((wordId) => {
					if (wordAssignments[wordId] === categoryId) {
						delete wordAssignments[wordId];
					}
				});
				categoryEl.remove();
				populateWords();
			});

			// Обновление списков при изменении названия категории
			categoryEl.querySelector("input").addEventListener("input", populateWords);

			categoriesList.appendChild(categoryEl);
			populateWords();
		});

		// Восстановление сохраненных категорий
		try {
			const savedCategories = JSON.parse(li.dataset.categories || "[]");
			savedCategories.forEach((cat) => {
				const categoryEl = document.createElement("div");
				categoryEl.className = "category-item";
				categoryEl.dataset.id = cat.id;

				categoryEl.innerHTML = `
							<input type="text" placeholder="Название категории" value="${cat.name}">
							<button type="button" class="remove-category-btn">×</button>
						`;

				categoryEl.querySelector(".remove-category-btn").addEventListener("click", () => {
					// Удаляем назначения для удаляемой категории
					Object.keys(wordAssignments).forEach((wordId) => {
						if (wordAssignments[wordId] === cat.id) {
							delete wordAssignments[wordId];
						}
					});
					categoryEl.remove();
					populateWords();
				});

				categoryEl.querySelector("input").addEventListener("input", populateWords);
				categoriesList.appendChild(categoryEl);
			});
		} catch (e) {
			console.error("Error parsing saved categories", e);
		}
		// Обработчик сохранения модуля
		li.querySelector(".save-edit").addEventListener("click", () => {
			// Сохраняем текущие назначения
			const assignments = Object.keys(wordAssignments).map((wordId) => ({
				word_id: wordId,
				category_id: wordAssignments[wordId],
			}));
			li.dataset.assignments = JSON.stringify(assignments);

			// Сохраняем категории
			const categories = [];
			categoriesList.querySelectorAll(".category-item").forEach((category) => {
				categories.push({
					id: category.dataset.id,
					name: category.querySelector("input").value,
				});
			});
			li.dataset.categories = JSON.stringify(categories);

			// Обновляем превью
			preview.innerHTML = `
						<h4>Категории (${categories.length}):</h4>
						<ul>
							${categories.map((cat) => `<li>${cat.name}</li>`).join("")}
						</ul>
						<h4>Слов для распределения: ${assignments.length}/${state.selectedItems.length}</h4>
					`;

			moduleContent.style.display = "block";
			editForm.style.display = "none";
		});

		// Первоначальное заполнение слов
		populateWords();

		// Редактирование модуля
		li.querySelector(".edit-module")?.addEventListener("click", () => {
			moduleContent.style.display = "none";
			editForm.style.display = "block";
			populateWords();
		});

		// Сохранение модуля
		li.querySelector(".save-edit")?.addEventListener("click", () => {
			// Собираем данные о категориях
			const categories = [];
			categoriesList.querySelectorAll(".category-item").forEach((category) => {
				categories.push({
					id: category.dataset.id,
					name: category.querySelector("input").value,
				});
			});

			// Собираем распределение слов
			const assignments = [];
			wordsList.querySelectorAll(".word-item").forEach((word) => {
				const wordId = word.dataset.id;
				const categoryId = word.querySelector("select").value;
				if (categoryId) {
					assignments.push({
						word_id: wordId,
						category_id: categoryId,
					});
				}
			});

			// Обновляем превью
			preview.innerHTML = `
						<h4>Категории (${categories.length}):</h4>
						<ul>
							${categories.map((cat) => `<li>${cat.name}</li>`).join("")}
						</ul>
						<h4>Слов для распределения: ${assignments.length}/${state.selectedItems.length}</h4>
					`;

			moduleContent.style.display = "block";
			editForm.style.display = "none";

			// Сохраняем данные в элемент
			li.dataset.categories = JSON.stringify(categories);
			li.dataset.assignments = JSON.stringify(assignments);
		});

		// Отмена редактирования
		li.querySelector(".cancel-edit")?.addEventListener("click", () => {
			moduleContent.style.display = "block";
			editForm.style.display = "none";
		});
	}

	function addTextHandlers(li, moduleContent, editForm) {
		const textPreview = li.querySelector(".text-preview");
		const textInput = li.querySelector(".edit-text-content");

		li.querySelector(".edit-module")?.addEventListener("click", () => {
			moduleContent.style.display = "none";
			editForm.style.display = "block";
			textInput.value = textPreview.textContent;
		});

		li.querySelector(".save-edit")?.addEventListener("click", () => {
			moduleContent.style.display = "block";
			editForm.style.display = "none";
			textPreview.textContent = textInput.value;
		});
	}
	function addVideoUrlHandlers(li, moduleContent, editForm) {
		const videoPreview = li.querySelector(".video-preview");
		const urlInput = li.querySelector(".edit-video-url");

		li.querySelector(".edit-module")?.addEventListener("click", () => {
			moduleContent.style.display = "none";
			editForm.style.display = "block";
			urlInput.value = videoPreview.dataset.url || "";
		});

		li.querySelector(".save-edit")?.addEventListener("click", () => {
			moduleContent.style.display = "block";
			editForm.style.display = "none";
			const url = urlInput.value;
			videoPreview.dataset.url = url; // Сохраняем URL в data-атрибут
			videoPreview.innerHTML = url ? `<p>Видео: ${url}</p>` : "";
		});
	}
	function addDocumentHandlers(li, moduleContent, editForm) {
		const docPreview = li.querySelector(".document-preview");
		const nameInput = li.querySelector(".edit-document-name");
		const fileInput = li.querySelector(".edit-document-file");

		li.querySelector(".edit-module")?.addEventListener("click", () => {
			moduleContent.style.display = "none";
			editForm.style.display = "block";
		});

		li.querySelector(".save-edit")?.addEventListener("click", () => {
			moduleContent.style.display = "block";
			editForm.style.display = "none";
			const fileName = fileInput.files[0]?.name || "";
			const docName = nameInput.value.trim();
			docPreview.textContent = docName
				? fileName
					? `${docName} (${fileName})`
					: docName
				: fileName || "Документ не выбран";
		});
	}

	function initSortable() {
		// Общие настройки для всех Sortable
		const commonSortableOptions = {
			animation: 150,
			ghostClass: "sortable-ghost",
			handle: ".module-header, .module-content",
			draggable: "li",
			group: {
				name: "nested-modules",
				pull: true,
				put: true,
			},
			fallbackOnBody: true,
			swapThreshold: 0.65,
		};

		// Основной список
		new Sortable(document.getElementById("module-list"), {
			...commonSortableOptions,
			onStart: function () {
				document.querySelectorAll(".nested-module-list").forEach((list) => {
					list.classList.add("sortable-active");
				});
			},
			onEnd: function () {
				document.querySelectorAll(".nested-module-list").forEach((list) => {
					list.classList.remove("sortable-active");
				});
			},
		});

		// Инициализация существующих вложенных списков
		document.querySelectorAll(".nested-module-list").forEach((list) => {
			initNestedSortable(list);
		});
	}

	function initNestedSortable(listElement) {
		new Sortable(listElement, {
			animation: 150,
			ghostClass: "sortable-ghost",
			group: {
				name: "nested-modules",
				pull: true,
				put: true,
			},
			handle: ".module-header",
			onAdd: function (evt) {
				// Обновляем parentId при перемещении элемента
				evt.item.dataset.parentId = evt.to.closest("[data-section-id]")?.dataset.sectionId;
			},
		});
	}

	function addSaveLessonHandlers() {
		document.getElementById("save-order").addEventListener("click", async function () {
			const formData = new FormData();

			const constructorName = document.getElementById("constructor-name").value;
			const lessonTitle = document.getElementById("lesson-title").value;
			const lessonDescription = document.getElementById("lesson-description").value;

			if (!constructorName || !lessonTitle) {
				alert("Заполните обязательные поля!");
				return;
			}

			if (state.selectedItems.length === 0) {
				alert("Выберите хотя бы одно слово!");
				return;
			}

			const data = {
				name: constructorName,
				title: lessonTitle,
				description: lessonDescription,
				word_ids: state.selectedItems.map((item) => item.id),
				structure: [],
			};

			function processModule(el) {
				const moduleData = {
					type_name: el.dataset.type,
					config: {},
					children: [],
				};

				// Заполняем конфиг в зависимости от типа
				switch (el.dataset.type) {
					case "section":
						moduleData.config.title = el.querySelector(".section-title")?.textContent || "";
						break;
					case "text":
						moduleData.config.content = el.querySelector(".text-preview")?.textContent || "";
						break;
					case "document":
						const nameInput = el.querySelector(".edit-document-name");
						const fileInput = el.querySelector(".edit-document-file");
						if (nameInput) moduleData.document_name = nameInput.value;
						if (fileInput?.files[0]) {
							formData.append(`document_${data.structure.length}`, fileInput.files[0]);
						}
						break;
					case "word_sorter":
						moduleData.config = {
							categories: JSON.parse(el.dataset.categories || "[]"),
							assignments: JSON.parse(el.dataset.assignments || "[]"),
						};
						break;
				}

				// Обрабатываем вложенные модули
				if (el.dataset.type === "section") {
					const nestedList = el.querySelector(".nested-module-list");
					if (nestedList) {
						nestedList.querySelectorAll("li").forEach((child) => {
							moduleData.children.push(processModule(child));
						});
					}
				}

				return moduleData;
			}

			const structure = [];
			document.querySelectorAll("#module-list > li").forEach((module) => {
				structure.push(processModule(module));
			});

			formData.append(
				"data",
				JSON.stringify({
					name: constructorName,
					title: lessonTitle,
					description: lessonDescription,
					word_ids: state.selectedItems.map((item) => item.id),
					structure: structure,
				})
			);

			// Добавляем файлы, если они есть
			document.querySelectorAll('input[type="file"]').forEach((input, index) => {
				if (input.files.length > 0) {
					formData.append(`document_${index}`, input.files[0]);
				}
			});

			try {
				const url =
					window.INITIAL_DATA && window.INITIAL_DATA.isEdit
						? `/constructor/edit/${window.INITIAL_DATA.constructorId}/`
						: "/constructor/create/";

				const response = await fetch(url, {
					method: "POST",
					body: formData,
					headers: {
						"X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
					},
				});

				const result = await response.json();

				if (result.status === "success") {
					window.location.href = result.redirect_url;
				} else {
					alert(result.message || "Произошла ошибка при сохранении");
				}
			} catch (error) {
				console.error("Error:", error);
				alert("Произошла ошибка при сохранении");
			}
		});
	}
});

import { initEditMode } from "/static/constructor/js/edit.js";

const state = {
	selectedItems: [],
	exerciseTypes: {},
};

document.addEventListener("DOMContentLoaded", function () {
	const input = document.querySelector(".autocomplete-input");
	const dropdown = document.querySelector(".autocomplete-dropdown");
	const selectedItemsContainer = document.querySelector(".selected-items");
	const itemElements = [...dropdown.querySelectorAll(".autocomplete-item")];
	const exerciseTypes = [...document.querySelectorAll(".exercise-tile")];
	const data = itemElements.map((item) => ({
		id: item.dataset.id,
		name: item.textContent.trim(),
	}));

	// Проверка режима редактирования
	if (window.EDIT_MODE && typeof initEditMode === "function") {
		initEditMode(window.LESSON_DATA);
	}

	// Инициализация данных для редактирования
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

	// Обработчик ввода текста
	input.addEventListener("input", function () {
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
	input.addEventListener("focus", function () {
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
													item.name.toLowerCase() === input.value.toLowerCase()
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
			input.value = "";
			dropdown.classList.remove("show");
			input.focus();
		}
	});

	// Рендер выбранных элементов
	function renderSelectedItems() {
		selectedItemsContainer.innerHTML = state.selectedItems
			.map(
				(item) => `
                <div class="selected-tag">
                    ${item.name}
                    <button type="button" data-id="${item.id}">&times;</button>
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

	// 1. Выбор слов
	document.querySelectorAll(".word-tag").forEach((tag) => {
		tag.addEventListener("click", function () {
			const wordId = this.dataset.word;

			if (this.classList.contains("selected")) {
				this.classList.remove("selected");
				state.selectedItems = state.selectedItems.filter((id) => id !== wordId);
			} else {
				this.classList.add("selected");
				state.selectedItems.push(wordId);
			}

			document.getElementById("selected-words-count").textContent = state.selectedItems.length;
		});
	});

	// 2. Модальное окно для выбора упражнений
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
	// 3. Выбор типа упражнения
	document.querySelectorAll(".exercise-tile").forEach((tile) => {
		tile.addEventListener("click", function () {
			const typeId = this.dataset.id;
			const typeCode = this.dataset.code;
			const typeData = state.exerciseTypes[typeId];
			const typeName = typeData.name.toLowerCase();

			// Определяем, куда добавлять новый модуль (в корень или в выбранный раздел)
			const targetList = document.querySelector(".sortable-active") || document.getElementById("module-list");

			const li = document.createElement("li");
			li.dataset.id = typeId;
			li.dataset.type = typeCode;

			// В зависимости от типа создаем разный контент
			switch (typeName) {
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

				case "video url": // оставляем как есть
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

				default: // Стандартные упражнения
					li.innerHTML = `
                    <div class="module-content">
                        <div>
                            <strong>${typeData.name}</strong>
                            <small>${typeData.description}</small>
                        </div>
                        <button class="remove-exercise">×</button>
                    </div>
                `;
			}

			// Общие обработчики для всех типов
			li.querySelector(".remove-exercise")?.addEventListener("click", function (e) {
				e.stopPropagation();
				li.remove();
			});

			// Обработчики для секций
			if (typeName === "section") {
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

			// Обработчики для специальных модулей
			if (["text", "video url", "document"].includes(typeName)) {
				const moduleContent = li.querySelector(".module-content");
				const editForm = li.querySelector(".edit-form");

				// Находим элементы для каждого типа модуля
				if (typeName === "text") {
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

				if (typeName === "video url") {
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

				if (typeName === "document") {
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

				// Общий обработчик отмены для всех типов
				li.querySelector(".cancel-edit")?.addEventListener("click", () => {
					moduleContent.style.display = "block";
					editForm.style.display = "none";
				});
			}

			targetList.appendChild(li);
			modal.style.display = "none";

			// Инициализируем Sortable для новой секции
			if (typeName === "section") {
				initNestedSortable(li.querySelector(".nested-module-list"));
			}
		});
	});

	// 4. Сортировка упражнений
	function initSortable() {
		// Общие настройки для всех Sortable
		const commonSortableOptions = {
			animation: 150,
			ghostClass: "sortable-ghost",
			handle: ".module-header",
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

	// Инициализируем Sortable при загрузке страницы
	initSortable();

	// 5. Сохранение набора
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
});

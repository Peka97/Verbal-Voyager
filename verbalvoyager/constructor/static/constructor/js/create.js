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
	const state = {
		selectedItems: [],
		exerciseTypes: {},
	};

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
			console.log("Выбранные слова:", state.selectedItems);
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
			const typeId = this.dataset.id; // оставляем как есть (числовой ID)
			const typeData = state.exerciseTypes[typeId];
			const typeName = typeData.name.toLowerCase(); // для удобства сравнения

			const li = document.createElement("li");
			li.dataset.id = typeId; // сохраняем числовой ID
			li.dataset.type = typeName; // добавляем атрибут с именем типа

			// В зависимости от типа создаем разный контент
			switch (
				typeName // сравниваем по имени типа
			) {
				case "section":
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

			// Обработчики только для специальных модулей
			if (["section", "text", "video url", "document"].includes(typeName)) {
				// Обработчик редактирования
				li.querySelector(".edit-module").addEventListener("click", function () {
					const content = li.querySelector(".module-content");
					const editForm = li.querySelector(".edit-form");
					content.style.display = "none";
					editForm.style.display = "block";

					switch (typeName) {
						case "section":
							editForm.querySelector(".edit-section-title").value = li.querySelector(".section-title").textContent;
							break;
						case "text":
							editForm.querySelector(".edit-text-content").value = li.querySelector(".text-preview").textContent;
							break;
						case "video url":
							editForm.querySelector(".edit-video-url").value = li.querySelector(".video-preview").dataset.url || "";
							break;
					}
				});

				// Обработчик сохранения
				li.querySelector(".save-edit").addEventListener("click", function () {
					const content = li.querySelector(".module-content");
					const editForm = li.querySelector(".edit-form");
					content.style.display = "block";
					editForm.style.display = "none";

					switch (typeName) {
						case "section":
							li.querySelector(".section-title").textContent = editForm.querySelector(".edit-section-title").value;
							break;
						case "text":
							li.querySelector(".text-preview").textContent = editForm.querySelector(".edit-text-content").value;
							break;
						case "video url":
							const url = editForm.querySelector(".edit-video-url").value;
							li.querySelector(".video-preview").dataset.url = url;
							li.querySelector(".video-preview").innerHTML = url ? `<p>Видео: ${url}</p>` : "";
							break;
						case "document":
							const docNameInput = editForm.querySelector(".edit-document-name");
							const docFileInput = editForm.querySelector(".edit-document-file");
							const docName = docNameInput.value.trim();
							const fileName = docFileInput.files[0] ? docFileInput.files[0].name : "";

							if (docFileInput.files[0]) {
								li.querySelector(".document-preview").textContent = docName ? `${docName} (${fileName})` : fileName;
							} else if (docName) {
								li.querySelector(".document-preview").textContent = docName;
							} else {
								li.querySelector(".document-preview").textContent = "Документ не выбран";
							}
							break;
					}
				});

				// Обработчик отмены
				li.querySelector(".cancel-edit").addEventListener("click", function () {
					li.querySelector(".module-content").style.display = "block";
					li.querySelector(".edit-form").style.display = "none";
				});
			}

			document.getElementById("module-list").appendChild(li);
			modal.style.display = "none";
		});
	});

	// 4. Сортировка упражнений
	new Sortable(document.getElementById("module-list"), {
		animation: 150,
		ghostClass: "sortable-ghost",
	});

	// 5. Сохранение набора
	document.getElementById("save-order").addEventListener("click", async function () {
		try {
			const formData = new FormData();
			const exercises = [];

			// Собираем данные о модулях
			document.querySelectorAll("#module-list li").forEach((li, index) => {
				const typeId = li.dataset.id;
				const typeName = li.dataset.type;
				const exerciseData = {
					type_id: typeId,
					type_name: typeName,
				};

				if (typeName === "document") {
					const nameInput = li.querySelector(".edit-document-name");
					exerciseData.document_name = nameInput ? nameInput.value.trim() : "";

					const fileInput = li.querySelector(".edit-document-file");
					if (fileInput && fileInput.files[0]) {
						formData.append(`document_${index}`, fileInput.files[0]);
					}
				}

				exercises.push(exerciseData);
			});

			formData.append(
				"data",
				JSON.stringify({
					word_ids: state.selectedItems.map((item) => item.id),
					structure: exercises,
				})
			);

			const siteName = window.location.href.split("/").slice(0, 3).join("/");
			const url = `${siteName}/constructor/create/`;
			const token = document.getElementsByName("csrfmiddlewaretoken")[0].defaultValue;

			const response = await fetch(url, {
				method: "POST",
				headers: {
					"X-CSRFToken": token,
				},
				body: formData,
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.message || "Server error");
			}

			const result = await response.json();
			window.location.href = result.redirect_url || "/";
		} catch (error) {
			console.error("Error:", error);
			alert("Ошибка при сохранении: " + error.message);
		}
	});
});

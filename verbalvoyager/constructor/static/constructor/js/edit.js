// Функции специфичные для редактирования
export function initEditMode(lessonData) {
	console.log("Режим редактирования урока", lessonData);

	// 1. Заполняем основные поля
	fillBasicFields(lessonData);

	// 2. Загружаем слова
	loadSelectedWords(lessonData.words);

	// 3. Загружаем структуру
	loadLessonStructure(lessonData.structure);

	// 4. Модифицируем обработчик сохранения
	modifySaveHandler(lessonData);
}

function fillBasicFields(data) {
	document.getElementById("constructor-name").value = data.constructorName || "";
	document.getElementById("lesson-title").value = data.title || "";
	document.getElementById("lesson-description").value = data.description || "";
}

function loadSelectedWords(words) {
	const container = document.querySelector(".selected-items");
	words.forEach((word) => {
		const wordEl = document.createElement("div");
		wordEl.className = "selected-word";
		wordEl.dataset.id = word.id;
		wordEl.innerHTML = `
            ${word.text}
            <span class="remove-word">×</span>
        `;
		container.appendChild(wordEl);
	});
}

function loadLessonStructure(structure) {
	const moduleList = document.getElementById("module-list");

	structure.forEach((module) => {
		const moduleEl = createModuleElement(module);
		moduleList.appendChild(moduleEl);

		// Рекурсивно обрабатываем вложенные модули
		if (module.type_name === "section" && module.children) {
			const nestedList = moduleEl.querySelector(".nested-module-list");
			module.children.forEach((child) => {
				nestedList.appendChild(createModuleElement(child));
			});
		}
	});
}

function createModuleElement(moduleData) {
	const li = document.createElement("li");
	li.className = "module-item";
	li.dataset.type = moduleData.type_name;

	// Генерация HTML для разных типов модулей
	let html = `
        <div class="module-header">
            <span class="module-type">${getModuleTypeName(moduleData.type_name)}</span>
            <button class="remove-module">×</button>
        </div>
        <div class="module-content">
    `;

	// Добавляем специфичный контент
	switch (moduleData.type_name) {
		case "section":
			html += `<h3>${moduleData.config?.title || "Новый раздел"}</h3>`;
			html += `<ul class="nested-module-list"></ul>`;
			break;
		case "text":
			html += `<p>${moduleData.config?.content || ""}</p>`;
			break;
		case "video_url":
			html += `<div class="video-preview">${moduleData.config?.url || ""}</div>`;
			break;
		// ... другие типы модулей
	}

	html += `</div>`;
	li.innerHTML = html;
	return li;
}

function modifySaveHandler(lessonData) {
	const saveBtn = document.getElementById("save-order");
	const originalHandler = saveBtn.onclick;

	saveBtn.onclick = async function () {
		// Дополнительные проверки для редактирования
		if (!validateEditForm()) return;

		// Вызываем оригинальный обработчик
		if (originalHandler) await originalHandler();

		// Дополнительные действия после сохранения
		console.log("Урок успешно обновлён");
	};
}

function validateEditForm() {
	// Специфичные проверки для редактирования
	return true;
}

// Вспомогательные функции
function getModuleTypeName(type) {
	const names = {
		section: "Раздел",
		text: "Текст",
		video_url: "Видео",
		document: "Документ",
	};
	return names[type] || type;
}

document.addEventListener("DOMContentLoaded", function () {
	const sidebar = document.querySelector(".right-sidebar");
	var sections = document.querySelectorAll(".section");
	sections.forEach(function (section) {
		const sectionTitleElement = section.querySelector(".section-title");

		let navItemElement = document.createElement("div");
		navItemElement.classList.add("nav-item");
		navItemElement.dataset.section = section.id;
		navItemElement.textContent = `${section.id.split("_")[1]}. ${sectionTitleElement.textContent}`;

		sidebar.appendChild(navItemElement);
	});

	// Мобильное меню
	document.querySelectorAll(".mobile-toggle").forEach((button) => {
		button.addEventListener("click", function () {
			const sidebar = this.parentElement;
			sidebar.classList.toggle("active");
		});
	});

	// Навигация по разделам
	document.querySelectorAll(".nav-item").forEach((item) => {
		item.addEventListener("click", function () {
			// Удаляем активный класс у всех элементов
			document.querySelectorAll(".nav-item").forEach((i) => {
				i.classList.remove("active");
			});

			// Добавляем активный класс текущему элементу
			this.classList.add("active");

			// Прокручиваем к выбранному разделу
			const sectionId = this.getAttribute("data-section");
			document.getElementById(sectionId).scrollIntoView({
				behavior: "smooth",
			});

			// Обновляем текущий раздел в мобильной версии
			document.querySelectorAll(".current-section").forEach((el) => {
				el.textContent = `Текущий раздел: ${this.textContent}`;
			});
		});
	});

	// Отслеживание текущего раздела при прокрутке
	window.addEventListener("scroll", function () {
		const sections = document.querySelectorAll(".section");
		let currentSection = "";

		sections.forEach((section) => {
			const sectionTop = section.offsetTop;
			const sectionHeight = section.clientHeight;

			if (pageYOffset >= sectionTop - 100) {
				currentSection = section.id;
			}
		});

		if (currentSection) {
			document.querySelectorAll(".nav-item").forEach((item) => {
				item.classList.remove("active");
				if (item.getAttribute("data-section") === currentSection) {
					item.classList.add("active");

					// Обновляем текущий раздел в мобильной версии
					document.querySelectorAll(".current-section").forEach((el) => {
						el.textContent = `Текущий раздел: ${item.textContent}`;
					});
				}
			});
		}
	});
});

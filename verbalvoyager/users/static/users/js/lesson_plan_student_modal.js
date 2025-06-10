let currentModal;
let isEditMode = false;
let originalContents = {};
let hasChanges = false;

document.addEventListener("DOMContentLoaded", function () {
	// Получаем элементы
	const openBtnElements = document.querySelectorAll(".open-modal-btn:not(.empty)");
	const closeBtnElements = document.querySelectorAll(".close-modal");

	// Открытие модального окна
	openBtnElements.forEach((btn) => {
		btn.addEventListener("click", function (event) {
			onModalOpen(event);
		});
	});

	// Закрытие модального окна
	closeBtnElements.forEach((btn) => {
		btn.addEventListener("click", function () {
			onModalClose();
		});
	});

	// Закрытие при клике вне окна
	window.addEventListener("click", function (event) {
		if (currentModal && event.target === currentModal) {
			onModalClose();
		}
	});
});

function onModalOpen(event) {
	document.body.classList.add("body-no-scroll");
	const id = event.target.parentElement.id.split("_")[1];
	const modal = document.getElementById(`lesson_${id}_PlanModal`);
	currentModal = modal;
	currentModal.classList.remove("hidden");
}

function onModalClose() {
	currentModal.classList.add("hidden");
	currentModal = undefined;
	document.body.classList.remove("body-no-scroll");
}

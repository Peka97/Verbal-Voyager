document.addEventListener("DOMContentLoaded", function () {
	const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
	const popoverList = [...popoverTriggerList].map(
		(el) =>
			new bootstrap.Popover(el, {
				trigger: "hover",
				delay: { show: 0, hide: 500 },
			})
	);
});

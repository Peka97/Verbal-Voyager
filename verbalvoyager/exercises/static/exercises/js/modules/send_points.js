export function send_points(ex_type, points) {
	let token = document.getElementsByName("csrfmiddlewaretoken")[0].defaultValue;
	// let exerciseLang = document.getElementById('exercise_lang')

	if (!token) {
		return;
	}

	let url;
	let siteName = window.location.href.split("/").slice(0, 3).join("/");

	if (ex_type === "words") {
		let exerciseId = window.location.href.split("/").slice(-2)[0];
		let stepNum = window.location.href.split("/").slice(-1)[0];
		url = `${siteName}/exercise_result/${ex_type}/${exerciseId}/step_${stepNum}`;
	} else if (ex_type === "dialog") {
		let exerciseId = window.location.href.split("/").slice(-1)[0];
		let stepNum = "1";
		url = `${siteName}/exercise_result/${ex_type}/${exerciseId}/step_${stepNum}`;
	} else if (ex_type === "irregular_verbs") {
		let exerciseId = window.location.href.split("/").slice(-2)[0];
		let stepNum = window.location.href.split("/").slice(-1)[0];
		url = `${siteName}/exercise_result/${ex_type}/${exerciseId}/step_${stepNum}`;
	} else {
		return;
	}

	let data = {
		method: "POST",
		headers: {
			Accept: "application/json",
			"Content-Type": "application/json",
			"X-CSRFToken": token,
		},
		body: JSON.stringify({
			value: points,
		}),
	};

	fetch(url, data)
		.then((resp) => {
			if (!resp.ok) {
				return;
			} else {
				return;
			}
		})
		.catch((err) => {
			return;
		});
}

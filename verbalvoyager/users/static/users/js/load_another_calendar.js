import { renderCalendar } from "/static/event_calendar/js/main.js";

const supervisorMetaElement = document.querySelector("meta#supervisor_role");
const prevCalendarButton = document.querySelector("span#prev_teacher");
const nextCalendarButton = document.querySelector("span#next_teacher");
const eventsContainerElement = document.querySelector("div#events_container");

let currentCalendarTeacherIdData = supervisorMetaElement.dataset["self"];
let currentTeacherIdBackUp = supervisorMetaElement.dataset["self"];
let anotherTeachersCalendarData = supervisorMetaElement.dataset["teachers"];
let teacherIdCyclicIterator = createCyclicIterator(anotherTeachersCalendarData.replace(/[()]/g, "").split(", "));

function createCyclicIterator(array) {
	let currentIndex = 0;

	return {
		next: function () {
			currentIndex = (currentIndex + 1) % array.length;
			return array[currentIndex];
		},
		prev: function () {
			currentIndex = (currentIndex - 1 + array.length) % array.length;
			return array[currentIndex];
		},
		getCurrent: function () {
			return array[currentIndex];
		},
	};
}

prevCalendarButton.addEventListener("click", loadPrevCalendar);
nextCalendarButton.addEventListener("click", loadNextCalendar);

function loadPrevCalendar() {
	currentCalendarTeacherIdData = teacherIdCyclicIterator.prev();

	loadTeacherCalendar(currentCalendarTeacherIdData).then((result) => {
		eventsContainerElement.innerHTML = result.html;
		renderCalendar();
		if (currentCalendarTeacherIdData !== currentTeacherIdBackUp) {
			const calendarTitleElement = document.querySelector("h4.calendar-title");
			calendarTitleElement.innerText = `Календарь ${result.teacherName}`;
			calendarTitleElement.classList.add("calendar-title-updated");
		} else {
			const calendarTitleElement = document.querySelector("h4.calendar-title");
			calendarTitleElement.innerText = "Календарь";
			calendarTitleElement.classList.remove("calendar-title-updated");
		}
	});
}

function loadNextCalendar() {
	currentCalendarTeacherIdData = teacherIdCyclicIterator.next();

	loadTeacherCalendar(currentCalendarTeacherIdData).then((result) => {
		eventsContainerElement.innerHTML = result.html;
		renderCalendar();
		if (currentCalendarTeacherIdData !== currentTeacherIdBackUp) {
			const calendarTitleElement = document.querySelector("h4.calendar-title");
			calendarTitleElement.innerText = `Календарь ${result.teacherName}`;
			calendarTitleElement.classList.add("calendar-title-updated");
		} else {
			const calendarTitleElement = document.querySelector("h4.calendar-title");
			calendarTitleElement.innerText = "Календарь";
			calendarTitleElement.classList.remove("calendar-title-updated");
		}
	});
}

function loadTeacherCalendar(teacherId) {
	const siteName = window.location.href.split("/").slice(0, 3).join("/");
	let url = `${siteName}/event_calendar/json/load_teacher_lessons/${teacherId}`;
	const params = new URLSearchParams({
		start: startDate.toISOString(),
		end: endDate.toISOString(),
		timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
	});
	let data = {
		method: "GET",
		headers: {
			Accept: "application/json",
			"Content-Type": "application/json",
			// 'X-CSRFToken': token,
		},
	};

	return fetch(url, data)
		.then((resp) => resp.json())
		.then((data) => {
			if (data.status === "OK") {
				return { html: data.html, teacherName: data.teacher_name };
			} else {
				return undefined;
			}
		});
}

import { showToast } from '/static/pages/js/modules/toast_notification.js';

const lessonInfoElements = document.querySelectorAll('.lesson-info');
const EventStatusChangerElements = document.querySelectorAll('div.event-card div.event-status-changer');
const checkBoxElements = document.querySelectorAll('input[type="checkbox"][name="task"]');
const sendEventUpdateButtonPanelElement = document.querySelector('div#panel-send-event-update');
const sendEventUpdateButtonElement = document.querySelector('div#btn-send-event-update');
const cancelSendEventUpdateButtonElement = document.querySelector('div#btn-cancel-send-event-update');
let sendingBlock = false;

let sendEventUpdateButtonPanelIsHidden = true;
let dataToSend = {
    lessons: {},
    tasks: {},
};
let dataOld = {
    lessons: {},
    tasks: {},
};

EventStatusChangerElements.forEach((elem) => {
    let iconElements = [...elem.children].filter(el => el.tagName === 'I');
    iconElements[0].addEventListener('click', changeEventPerforming);
    iconElements[1].addEventListener('click', changeEventPayment);
    dataOld.lessons[elem.id] = {
        performing: iconElements[0].attributes.name.value,
        payment: iconElements[1].classList.contains('paid'),
    }
});

checkBoxElements.forEach((checkbox) => {
    checkbox.addEventListener('change', changeCheckbox);
    dataOld.tasks[checkbox.id] = checkbox;
});

sendEventUpdateButtonElement.addEventListener('click', sendEventUpdate);
cancelSendEventUpdateButtonElement.addEventListener('click', cancelSendEventUpdate);

function changeCheckbox(event) {
    if (sendEventUpdateButtonPanelIsHidden) {
        removeHiddenCheckbox();
    }

    let changedCheckbox = event.target;
    dataToSend.tasks[changedCheckbox.id] = changedCheckbox.checked;
}

function removeHiddenCheckbox() {
    sendEventUpdateButtonPanelElement.classList.remove('hidden');

    checkBoxElements.forEach((checkbox) => {
        checkbox.removeEventListener('change', removeHiddenCheckbox);
    });
}

function sendEventUpdate(event) {
    if (sendingBlock) {
        showToast('Данные уже были отправлены ранее. Обновите страницу для отображения актуальной информации и повторите попытку.');
        return;
    }
    let url = "http://127.0.0.1:8000/event_calendar/json/update/"
    let token = document.getElementsByName('csrfmiddlewaretoken')[0].defaultValue;

    if (!token) {
        console.log("Couldn't find token")
        return
    };

    let data = {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': token,
        },
        body: 
            JSON.stringify(dataToSend)
    }

    fetch(url, data).then(resp => {
        if (resp.ok) {
            const eventUpdatedCount = Object.keys(dataToSend.tasks).length + Object.keys(dataToSend.lessons).length
            showToast(`${eventUpdatedCount} событие(-ий) обновлено`);
            sendingBlock = true;
            return resp.json();
        } else {
            showToast(`Ошибка обновления событий. Код ${resp.status}`);
        }
    });
}

function cancelSendEventUpdate() {
    for (let key in dataToSend) {
        if (dataToSend[key] !== dataOld[key]) {
            let checkboxElement = document.querySelector(`input[name="task"][id="${key}"]`);
            checkboxElement.checked = dataOld[key];
        }
    }
}

function changeEventPerforming(event) {
    if (sendEventUpdateButtonPanelIsHidden) {
        removeHiddenCheckbox();
    }

    if (event.target.classList.contains('bi-clock')) {
        event.target.classList.remove("bi-clock");
        event.target.classList.add("bi-check-circle");
        event.target.attributes.name.value = "D";
    } else if (event.target.classList.contains('bi-check-circle')) {
        event.target.classList.remove("bi-check-circle");
        event.target.classList.add("bi-x-circle");
        event.target.attributes.name.value = "C";
    } else if (event.target.classList.contains('bi-x-circle')) {
        event.target.classList.remove("bi-x-circle");
        event.target.classList.add("bi-person-x");
        event.target.attributes.name.value = "M";
    } else {
        event.target.classList.remove("bi-person-x");
        event.target.classList.add("bi-clock");
        event.target.attributes.name.value = "P";
    }

    if (!dataToSend.lessons[event.target.parentElement.id]) {
        dataToSend.lessons[event.target.parentElement.id] = {}
    }
        
    dataToSend.lessons[event.target.parentElement.id].performing = event.target.attributes.name.value
}

function changeEventPayment(event) {
    if (sendEventUpdateButtonPanelIsHidden) {
        removeHiddenCheckbox();
    }
    
    if (event.target.classList.contains("paid")) {
        event.target.classList.remove("paid");
        event.target.classList.add("not-paid");
    } else {
        event.target.classList.add("paid");
        event.target.classList.remove("not-paid");
    }

    if (!dataToSend.lessons[event.target.parentElement.id]) {
        dataToSend.lessons[event.target.parentElement.id] = {}
    }
    
    dataToSend.lessons[event.target.parentElement.id].payment = event.target.classList.contains("paid");
}
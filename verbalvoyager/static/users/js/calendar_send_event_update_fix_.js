import { showToast } from '/static/pages/js/modules/toast_notification.js';

const lessonInfoElements = document.querySelectorAll('.lesson-info');
const EventStatusChangerElements = document.querySelectorAll('div.event-card div.event-status-changer');
const checkBoxElements = document.querySelectorAll('input[type="checkbox"][name="task"]');
const sendEventUpdateButtonPanelElement = document.querySelector('div#panel-send-event-update');
const sendEventUpdateButtonElement = document.querySelector('div#btn-send-event-update');
const cancelSendEventUpdateButtonElement = document.querySelector('div#btn-cancel-send-event-update');

let sendingBlock = false;
let dataToSend = {
    lessons: {},
    tasks: {
        toCreate: {},
        toUpdate: {},
        toDelete: [],
    },
};
let dataOld = {
    lessons: {},
    tasks: {},
};

let iconPerformingStatusElements = [...document.querySelectorAll('i.performing-status')]
let iconPaymentStatusElements = [...document.querySelectorAll('i.payment-status')]

iconPerformingStatusElements.forEach(elem => {
    elem.addEventListener('click', changeEventPerforming);
})

iconPaymentStatusElements.forEach(elem => {
    elem.addEventListener('click', changeEventPayment);
})

EventStatusChangerElements.forEach((elem) => {
    const lessonId = elem.parentElement.id.split('_')[1];
    const currentPerformingStatus = elem.querySelector('i.performing-status');
    const currentPaymentStatus = elem.querySelector('i.payment-status');

    dataOld.lessons[lessonId] = {
        performing: currentPerformingStatus.attributes.name.value,
        payment: currentPaymentStatus.classList.contains('paid'),
    }
});

checkBoxElements.forEach((checkbox) => {
    checkbox.addEventListener('change', changeCheckbox);
    let lessonLabel = checkbox.parentElement.querySelector('label');
    
    let taskName = lessonLabel.innerText.split(' (')[0]
    let taskPoints = lessonLabel.innerText.split(' (')[1][0]

    dataOld.tasks[checkbox.id] = {
        name: taskName,
        points: taskPoints,
        isCompleted: checkbox.checked,
    }
});


sendEventUpdateButtonElement.addEventListener('click', sendEventUpdate);
cancelSendEventUpdateButtonElement.addEventListener('click', cancelSendEventUpdate);

function changeCheckbox(event) {
    let changedCheckbox = event.target;
    const isNewLessonTask = changedCheckbox.parentElement.classList.contains('new-lesson-task');
    const labelCheckboxText = changedCheckbox.parentElement.querySelector('label').innerText;
    const lessonId = changedCheckbox.parentElement.parentElement.parentElement.parentElement.id.split('_')[1];

    let method;
    
    if (isNewLessonTask) {
        method = 'toCreate';
    } else {
        method = 'toUpdate';
    }

    dataToSend.tasks[method][changedCheckbox.id] = {
        name: labelCheckboxText.split(' (')[0],
        points: labelCheckboxText.split(' (')[1][0],
        isCompleted: changedCheckbox.checked,
        createFor: lessonId,
    }

    console.dir(dataToSend);

    
    sendEventUpdatePanelShowCheck()
}

function sendEventUpdate(event) {
    if (sendingBlock) {
        showToast('Данные уже были отправлены ранее. Обновите страницу для отображения актуальной информации и повторите попытку.');
        return;
    }
    const siteName = window.location.href.split('/').slice(0, 3).join('/');
    let url = `${siteName}/event_calendar/json/update/`
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
            const eventUpdatedCount = Object.keys(dataToSend.tasks.toCreate).length + Object.keys(dataToSend.tasks.toUpdate).length + Object.keys(dataToSend.tasks.toDelete).length + Object.keys(dataToSend.lessons).length
            sendingBlock = true;

            showToast(`${eventUpdatedCount} событие(-ий) обновлено`);
            return resp.json();
        } else {
            showToast(`Ошибка обновления событий. Код ${resp.status}`);
        }
    });
}

function cancelSendEventUpdate() {
    for (let key in dataToSend.lessons) {
        let currentdataOld = dataOld.lessons[key];
        let lessonInfoElemtent = document.getElementById(`lesson_${key}`);
    }
}

function changeEventPerforming(event) {
    let iconElement = event.target
    let tooltipElement = event.target.previousElementSibling

    if (iconElement.classList.contains('bi-clock')) {
        iconElement.classList.remove("bi-clock");
        iconElement.classList.add("bi-check-circle");
        iconElement.attributes.name.value = "D";
        tooltipElement.innerText = "Проведён";
    } else if (iconElement.classList.contains('bi-check-circle')) {
        iconElement.classList.remove("bi-check-circle");
        iconElement.classList.add("bi-x-circle");
        iconElement.attributes.name.value = "C";
        tooltipElement.innerText = "Отменён";
    } else if (iconElement.classList.contains('bi-x-circle')) {
        iconElement.classList.remove("bi-x-circle");
        iconElement.classList.add("bi-person-x");
        iconElement.attributes.name.value = "M";
        tooltipElement.innerText = "Пропущен";
    } else {
        iconElement.classList.remove("bi-person-x");
        iconElement.classList.add("bi-clock");
        iconElement.attributes.name.value = "P";
        tooltipElement.innerText = "Запланирован";
    }
    const lessonId = event.target.parentElement.parentElement.parentElement.id.split('_')[1]

    if (!dataToSend.lessons[lessonId]) {
        dataToSend.lessons[lessonId] = {}
    }
        
    dataToSend.lessons[lessonId].performing = event.target.attributes.name.value

    sendEventUpdatePanelShowCheck()
}

function changeEventPayment(event) {
    let iconElement = event.target
    let tooltipElement = event.target.previousElementSibling
    
    if (iconElement.classList.contains("paid")) {
        iconElement.classList.remove("paid");
        iconElement.classList.add("not-paid");
        tooltipElement.innerText = "Не оплачено";
    } else {
        iconElement.classList.add("paid");
        iconElement.classList.remove("not-paid");
        tooltipElement.innerText = "Оплачено";
    }

    const lessonId = iconElement.parentElement.parentElement.parentElement.id.split('_')[1]

    if (!dataToSend.lessons[lessonId]) {
        dataToSend.lessons[lessonId] = {}
    }

    dataToSend.lessons[lessonId].payment = iconElement.classList.contains("paid");

    sendEventUpdatePanelShowCheck()
}

// Add new lesson task
const newTaskButtons = [...document.getElementsByClassName('new-task-button')];
const taskEditButtonElements = [...document.getElementsByClassName('task-edit-icon')];
const taskDeleteButtonElements = [...document.getElementsByClassName('task-delete-icon')];

taskEditButtonElements.forEach(element => {
    element.addEventListener('click', editTask)});

    newTaskButtons.forEach(btn => {
        btn.addEventListener('click', (event) => {
            let tasksContainerElement = event.target.parentElement.parentElement.querySelector('.task-container');

            if (tasksContainerElement.children[1].classList.contains('not-tasks')) {
                tasksContainerElement.children[1].remove()
                let newChecklist = document.createElement('div');
                newChecklist.classList.add('checklist');
                
                tasksContainerElement.insertBefore(newChecklist, tasksContainerElement.querySelector('span.new-task-button'));
            }
        tasksContainerElement.appendChild(getTaskForm('create'))
    });
});

taskDeleteButtonElements.forEach(element => {
    element.addEventListener('click', deleteTask)}
);

function getTaskForm(method) {
    let classNamePrefix;
    if (method === 'create') {
        classNamePrefix = 'new-'
    } else {
        classNamePrefix = 'edit-'
    }

    console.log(classNamePrefix)
    
    const newLessonTaskId = `new_${Date.now()}`

    let checklistElement = document.createElement(
        'div', {id: 'checklist'}
    );
    checklistElement.classList.add(`${classNamePrefix}lesson-task`);
    
    let taskNameInput = document.createElement('input');
    taskNameInput.classList.add(`${classNamePrefix}task-input-name`)
    taskNameInput.type = 'text';
    taskNameInput.placeholder = 'Напиши суть задания'
    taskNameInput.id = newLessonTaskId

    let taskPointsInput = document.createElement('input');
    taskPointsInput.classList.add(`${classNamePrefix}task-input-points`)
    taskPointsInput.type = 'number';
    taskPointsInput.value = 1
    taskPointsInput.min = 1

    let taskSaveIcon = document.createElement('i');
    taskSaveIcon.classList.add('bi', 'bi-clipboard-check');
    taskSaveIcon.addEventListener('click', changeTaskAdderToTask);

    checklistElement.appendChild(taskNameInput);
    checklistElement.appendChild(taskPointsInput);
    checklistElement.appendChild(taskSaveIcon);

    return checklistElement;
}

function changeTaskAdderToTask(event) {
    let currentNewTaskButtonElement = event.target;
    let lessonTaskElement = currentNewTaskButtonElement.parentElement;
    let taskContainerElement = lessonTaskElement.parentElement;
    
    let lessonTaskInputElements = lessonTaskElement.querySelectorAll('input');
    let input = taskContainerInputClean(lessonTaskInputElements);

    if (input.isInputClean) {
        let checklistDivElement;
        if (!taskContainerElement.classList.contains('checklist')) {
            checklistDivElement = taskContainerElement.querySelector('.checklist');
        } else {
            checklistDivElement = taskContainerElement;
        }

        let newTaskDiv = getLessonTaskDiv(lessonTaskInputElements, false);
        let taskId = lessonTaskElement.firstChild.id
        let method;
        console.dir(taskId)

        if (taskId.includes('new_')) {
            console.log('create')
            method = 'toCreate'
        } else {
            console.log('update')
            taskId = newTaskDiv.id
            method = 'toUpdate'
        }
        
        const lessonId = taskContainerElement.parentElement.id.split('_')[1]

        checklistDivElement.appendChild(newTaskDiv.element);

        lessonTaskElement.remove()
        
        dataToSend['tasks'][method][taskId] = {
            name: lessonTaskInputElements[0].value,
            points: lessonTaskInputElements[1].value,
            isCompleted: false,
            createFor: lessonId,
        }

        sendEventUpdatePanelShowCheck()
        
    } else if (input.wrongInput) {
        input.wrongInput.classList.add('new-task-wrong');
    }
}

function taskContainerInputClean(inputCollection) {
    for (let i = 0; i < inputCollection.length; i++) {
        if (!inputCollection[i].value) {
            return {isInputClean: false, wrongInput: inputCollection[i]};
        }
    }
    return {isInputClean: true, wrongInput: undefined};
}

function getLessonTaskDiv(lessonTaskInputElements, isNewLessonTask) {
    const newLessonTaskId = lessonTaskInputElements[0].id

    let lessonTaskDivElement = document.createElement('div');
    lessonTaskDivElement.classList.add('lesson-task');

    if (isNewLessonTask) {
        lessonTaskDivElement.classList.add('new-lesson-task');
    } else {
        lessonTaskDivElement.classList.add('update-lesson-task');
    }

    let taskInputElement = document.createElement('input');
    taskInputElement.type = 'checkbox';
    taskInputElement.name = 'task';
    taskInputElement.id = newLessonTaskId;
    taskInputElement.classList.add('task-input-name');
    taskInputElement.addEventListener('change', changeCheckbox);

    let taskLabelElement = document.createElement('label');
    taskLabelElement.htmlFor = newLessonTaskId;
    taskLabelElement.innerText = `${lessonTaskInputElements[0].value} (${lessonTaskInputElements[1].value} баллов)`;

    let taskEditButtonElement = document.createElement('i');
    taskEditButtonElement.classList.add('bi', 'bi-pen-fill', 'task-edit-icon');
    taskEditButtonElement.addEventListener('click', editTask);

    let taskDeleteButtonElement = document.createElement('i');
    taskDeleteButtonElement.classList.add('bi', 'bi-trash', 'task-delete-icon');
    taskDeleteButtonElement.addEventListener('click', deleteTask);

    lessonTaskDivElement.appendChild(taskInputElement);
    lessonTaskDivElement.appendChild(taskLabelElement);
    lessonTaskDivElement.appendChild(taskEditButtonElement);
    lessonTaskDivElement.appendChild(taskDeleteButtonElement);

    return {id: newLessonTaskId, element: lessonTaskDivElement};
}

function editTask(event) {
    let lessonTaskElement = event.target.parentElement;
    let taskOldNameValue = lessonTaskElement.children[1].innerText.split('(')[0];
    const taskOldId = lessonTaskElement.children[0].id

    removeAllChildren(lessonTaskElement)
    lessonTaskElement.classList.remove('lesson-task');
    lessonTaskElement.classList.add('update-lesson-task');
    let taskForm = getTaskForm();
    taskForm.children[0].value = taskOldNameValue
    taskForm.children[0].id = taskOldId
    lessonTaskElement.replaceWith(taskForm);
}

function removeAllChildren(element) {
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

function deleteTask(event) {
    let lessonTaskElement = event.target.parentElement;
    const lessonTaskId = lessonTaskElement.children[0].id
    lessonTaskElement.remove()
    

    if (lessonTaskId in dataToSend.tasks.toCreate) {
        delete dataToSend.tasks.toCreate[lessonTaskId];
    } else {
        dataToSend.tasks.toDelete.push(lessonTaskId);
    }

    sendEventUpdatePanelShowCheck()
}

function sendEventUpdatePanelShowCheck() {
    const dataToSendCounts = Object.keys(dataToSend.lessons).length +
        Object.keys(dataToSend.tasks.toCreate).length +
        Object.keys(dataToSend.tasks.toUpdate).length +
        Object.keys(dataToSend.tasks.toDelete).length

    if (dataToSendCounts > 0) {
        sendEventUpdateButtonPanelElement.classList.remove('hidden');
        return
    }

    sendEventUpdateButtonPanelElement.classList.add('hidden');
}
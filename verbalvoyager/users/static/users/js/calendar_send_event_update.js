const checkBoxElements = document.querySelectorAll('input[type="checkbox"][name="task"]');
const sendEventUpdateButtonElement = document.querySelector('button#send-event-update')
// console.dir(sendEventUpdateButtonElement);

checkBoxElements.forEach((checkbox) => {
    checkbox.addEventListener('change', removeHiddenCheckbox);
});

function removeHiddenCheckbox(event) {
    sendEventUpdateButtonElement.classList.remove('hidden');

    checkBoxElements.forEach((checkbox) => {
        checkbox.removeEventListener('change', removeHiddenCheckbox);
});
}
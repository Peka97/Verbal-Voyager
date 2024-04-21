document.getElementById('step_1').classList.add('bg-success', 'text-light')
document.getElementById('step_2').classList.add('bg-success', 'text-light')
const alert_success = document.getElementById('alert-success')
const alert_danger = document.getElementById('alert-danger')
const words = Array(5)
const next_step = document.getElementById('step_4')

const tasksListElement = document.querySelector(`.translate__list`);
const taskElements = tasksListElement.querySelectorAll(`.translate__item`);
let points = words.length

const getNextElement = (cursorPosition, currentElement) => {
  const currentElementCoord = currentElement.getBoundingClientRect();
  const currentElementCenter = currentElementCoord.y + currentElementCoord.height / 2;
  
  const nextElement = (cursorPosition < currentElementCenter) ?
    currentElement :
    currentElement.nextElementSibling;
  
  return nextElement;
};

document.getElementById('btn-answer').onclick = (event) => {
    checkAnswer()
}
for (const task of taskElements) {
  task.draggable = true;
}

tasksListElement.addEventListener(`dragstart`, (evt) => {
  evt.target.classList.add(`selected`);
});
tasksListElement.addEventListener(`touchstart`, (evt) => {
  evt.target.classList.add(`selected`);
});

tasksListElement.addEventListener(`dragover`, (evt) => {
  evt.preventDefault();
  
  const activeElement = tasksListElement.querySelector(`.selected`);
  const currentElement = evt.target;
  const isMoveable = activeElement !== currentElement &&
    currentElement.classList.contains(`translate__item`);
    
  if (!isMoveable) {
    return;
  }
  
  const nextElement = getNextElement(evt.clientY, currentElement);
  
  if (
    nextElement && 
    activeElement === nextElement.previousElementSibling ||
    activeElement === nextElement
  ) {
    return;
  }
		
	tasksListElement.insertBefore(activeElement, nextElement);
});

tasksListElement.addEventListener(`touchmove`, (evt) => {
  
});

function move (evt) {
  evt.preventDefault();
  
  const activeElement = tasksListElement.querySelector(`.selected`);
  const currentElement = evt.target;
  const isMoveable = activeElement !== currentElement &&
    currentElement.classList.contains(`translate__item`);
    
  if (!isMoveable) {
    return;
  }
  
  const nextElement = getNextElement(evt.clientY, currentElement);
  
  if (
    nextElement && 
    activeElement === nextElement.previousElementSibling ||
    activeElement === nextElement
  ) {
    return;
  }
	tasksListElement.insertBefore(activeElement, nextElement);
}

tasksListElement.addEventListener(`dragend`, (evt) => {
  evt.target.classList.remove(`selected`);
});
tasksListElement.addEventListener(`touchend`, (evt) => {
  evt.target.classList.remove(`selected`);
});
function checkAnswer() {
    let words = document.getElementById('words-list').children
    let trans = document.getElementById('trans-list').children
    let result = true;

    for (let i = 0; i < words.length; i++) {
        if (words[i].id.slice(-1) != trans[i].id.slice(-1)) {
            result = false;
        }
    }
    
    if (result) {
        alert_danger.classList.add('hidden')
        alert_success.classList.remove('hidden')
        document.getElementById('step_3').classList.remove('bg-warning', 'active')
        document.getElementById('step_3').classList.add('step-complete')
        document.getElementById('step_4').classList.remove('disabled')
        document.getElementById('step_4').classList.add('step-active', 'active', 'ramka-5')
        document.getElementById('main-alert').classList.remove('hidden')
    }
    else {
        alert_danger.classList.remove('hidden')
        alert_success.classList.add('hidden')

        if (points > 1) {
          points--;
        }
    }
}

next_step.onclick = (event) => {
  console.log('POST')
  let token = document.getElementsByName('csrfmiddlewaretoken')[0].defaultValue
  
  let ex_id = window.location.href.split('/').slice(-2, -1)[0]
  let step_num = window.location.href.split('/').slice(-1)[0]
  let url = `https://verbal-voyager.ru/exercises/update/${ex_id}/step_${step_num}`

  fetch(url, {
          method: 'POST',
          headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
              'X-CSRFToken': token,
          },
          body: JSON.stringify({
              'value': points,
          })
      }
  ).then(response => {
      console.log(response.status)
      if (response.status != 200) {
          console.log('Не удалось отправить данные');
      }
      else {
          event.preventDefault();
      }
  })
}

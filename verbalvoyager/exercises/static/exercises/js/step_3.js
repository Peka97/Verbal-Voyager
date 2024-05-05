const step_1 = document.getElementById('step_1').classList.add('step-complete')
const step_2 = document.getElementById('step_2').classList.add('step-complete')
const words = document.getElementsByClassName('word__word')
const next_step = document.getElementById('step_4')

let points = words.length

function send_points() {
  console.log('Отправка баллов...')
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
              'value': points
          })
      }
  ).then(response => {
      console.log(response.status)
      if (response.status != 200) {
          console.log('Не удалось отправить баллы');
      }
      else {
          console.log('Баллы отправлены')
      }
  })
}
function checkAnswer() {
    let words = document.getElementById('words').children
    let trans = document.getElementById('translate').children
    let result = true;

    for (let i = 0; i < words.length; i++) {
        if (words[i].id.slice(-1) != trans[i].id.slice(-1)) {
            result = false;
        }
    }
    
    if (result) {
        glow.classList.remove('disabled')
        stars.classList.remove('disabled')

        toastLiveExample.attributes.getNamedItem('data-bs-delay').nodeValue = '10000'
        toastBody.innerText = 'Верно, так держать! Можешь переходить к следующему шагу.'

        document.getElementById('step_3').classList.remove('bg-warning', 'active')
        document.getElementById('step_3').classList.add('step-complete')
        document.getElementById('step_4').classList.remove('disabled')
        document.getElementById('step_4').classList.add('next-btn', 'active')

        send_points()
    }
    else {
        toastLiveExample.attributes.getNamedItem('data-bs-delay').nodeValue = '10000'
        toastBody.innerText = 'Не верно, подумай ещё.'

        if (points > 1) {
          points--;
        }
    }
}

const dropItems = document.getElementById('translate')
new Sortable(dropItems, {
  animation: 150,
  ghostClass: 'ghost',
  chosenClass: "chosen",
  dragClass: "sortable-drag"
});

const toastTrigger = document.getElementById('liveToastBtn')
const toastLiveExample = document.getElementById('liveToast')
const toastBody = document.getElementById('toast-body')

if (toastTrigger) {
  toastTrigger.addEventListener('click', () => {
    const toast = new bootstrap.Toast(toastLiveExample)
    checkAnswer()

    toast.show()
  })
}

const stars = document.getElementById('step_4').children[1]
const glow = document.getElementById('step_4').children[2]
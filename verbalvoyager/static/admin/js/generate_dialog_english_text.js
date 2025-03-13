document.addEventListener('DOMContentLoaded', function() {
    const TextElement = document.querySelector('#id_text_helptext');

    const GenerateWrapperElement = document.createElement('div');
    GenerateWrapperElement.style.marginLeft = '10px';
    
    const GenerateTitleDivElement = document.createElement('div');
    GenerateTitleDivElement.textContent = 'Генерация диалога: выбери слова, опции и нажми на плюс.';
    
    const GenerateOptionsWrapperElement = document.createElement('div');

    const GenerateButtonElement = document.createElement('a');
    GenerateButtonElement.title = 'Сгенерировать диалог'
    GenerateButtonElement.style.margin = 'auto'

    const GenerateIconElement = document.createElement('img');
    GenerateIconElement.src = '/static/admin/img/icon-addlink.svg'
    GenerateIconElement.width = 20
    GenerateIconElement.height = 20

    const GenerateСounterInput = document.createElement('input');
    GenerateСounterInput.type = 'number';
    GenerateСounterInput.value = 6;
    GenerateСounterInput.min = 1;
    GenerateСounterInput.max = 12;
    GenerateСounterInput.id = 'generate-counter';
    GenerateСounterInput.style.height = 'max-content';
    GenerateСounterInput.style.width = 'max-content';

    const GenerateSelectLevelElement = document.createElement('select');
    const levels = ['Beginner', 'Elementary', 'Pre-intermediate', 'Intermediate', 'Upper-intermediate', 'Advanced', 'Proficiency'];
    levels.forEach(level => {
        const option = document.createElement('option');
        option.value = level.toLowerCase();
        option.text = level;
        GenerateSelectLevelElement.appendChild(option);
    });
    GenerateSelectLevelElement.style.height = 'max-content';
    GenerateSelectLevelElement.style.width = 'max-content';
    GenerateSelectLevelElement.style.margin = '0 10px'

    TextElement.parentNode.firstElementChild.appendChild(GenerateWrapperElement);

    GenerateWrapperElement.appendChild(GenerateTitleDivElement);
    GenerateWrapperElement.appendChild(GenerateOptionsWrapperElement);

    GenerateOptionsWrapperElement.appendChild(GenerateСounterInput);
    GenerateOptionsWrapperElement.appendChild(GenerateSelectLevelElement);
    GenerateOptionsWrapperElement.appendChild(GenerateButtonElement);

    GenerateButtonElement.appendChild(GenerateIconElement);

    GenerateButtonElement.addEventListener('click', SendToGenerateText)

    function SendToGenerateText () {
        GenerateButtonElement.classList.add('disabled-link');

        let Words = Array();
        let WordsElements = [...document.querySelector('#id_words').children];
        
        WordsElements.forEach(wordElement => {
            Words.push(wordElement.value)
        })
        
        if (Words.length > 0) {
            const siteName = window.location.href.split('/').slice(0, 3).join('/');
            let url = `${siteName}/exercises/dialog/json/generate_dialog/english`
            
            fetch(url, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(
                    {
                        'words_ids': Words,
                        'sentences_count': GenerateСounterInput.value,
                        'level': GenerateSelectLevelElement.value
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    const TextAreaElement = document.querySelector('#id_text');
                    TextAreaElement.value = data.result
                    GenerateButtonElement.classList.remove('disabled-link');
                })
                .catch(error => {
                    console.error('Error:', error);
                    GenerateButtonElement.classList.remove('disabled-link');
                })
        } else {
            alert('Пожалуйста, сначала выберите слова и только после этого на генерацию текста.')
            GenerateButtonElement.classList.remove('disabled-link');
        }
        
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();

                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
      }
});
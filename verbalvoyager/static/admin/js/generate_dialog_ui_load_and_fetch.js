const GenerateWrapperElement = document.createElement('div');
    GenerateWrapperElement.classList.add('wrapper__block-generate')
    
    const GenerateTitleDivElement = document.createElement('div');
    GenerateTitleDivElement.classList.add('generate-title');
    GenerateTitleDivElement.textContent = 'Генерация диалога: выбери слова, опции и нажми на иконку под этой надписью.';
    
    const GenerateOptionsWrapperElement = document.createElement('div');

    const GenerateButtonElement = document.createElement('i');
    GenerateButtonElement.classList.add("fa-solid", "fa-file-arrow-down", "button__generate-dialog")
    GenerateButtonElement.title = 'Сгенерировать диалог'
    GenerateButtonElement.style.color = '#FFC400'

    const GenerateСounterInput = document.createElement('input');
    GenerateСounterInput.classList.add('generate-input');
    GenerateСounterInput.type = 'number';
    GenerateСounterInput.value = 6;
    GenerateСounterInput.min = 1;
    GenerateСounterInput.max = 12;
    GenerateСounterInput.id = 'generate-counter';

    const GenerateSelectLevelElement = document.createElement('select');
    GenerateSelectLevelElement.classList.add('generate-select');

    const levels = ['Beginner', 'Elementary', 'Pre-intermediate', 'Intermediate', 'Upper-intermediate', 'Advanced', 'Proficiency'];
    levels.forEach(level => {
        const option = document.createElement('option');
        option.value = level.toLowerCase();
        option.text = level;
        GenerateSelectLevelElement.appendChild(option);
    });

document.addEventListener('DOMContentLoaded', function() {
    const TextElement = document.querySelector('#id_text_helptext');

    TextElement.parentNode.firstElementChild.appendChild(GenerateWrapperElement);

    GenerateWrapperElement.appendChild(GenerateTitleDivElement);
    GenerateWrapperElement.appendChild(GenerateOptionsWrapperElement);

    GenerateOptionsWrapperElement.appendChild(GenerateСounterInput);
    GenerateOptionsWrapperElement.appendChild(GenerateSelectLevelElement);
    GenerateOptionsWrapperElement.appendChild(GenerateButtonElement);

    GenerateButtonElement.addEventListener('click', GenerateButtonClickHandler)
});

function GenerateButtonClickHandler () {
    changeIcons()

    let Words = Array();
    let WordsElements = [...document.querySelector('#id_words').children];
    
    WordsElements.forEach(wordElement => {
        Words.push(wordElement.value)
    })

    SendToGenerateText(
        Words, 
        GenerateСounterInput.value,
        GenerateSelectLevelElement.value
    )
}

function changeIcons() {
    if (GenerateButtonElement.classList.contains('fa-file-arrow-down')) {
        GenerateButtonElement.classList.remove('fa-file-arrow-down')
        GenerateButtonElement.classList.add('fa-circle-notch', 'loader-animation', 'disabled-link');
    } else {
        GenerateButtonElement.classList.remove('fa-circle-notch', 'loader-animation', 'disabled-link');
        GenerateButtonElement.classList.add('fa-file-arrow-down');
    }
}

function SendToGenerateText (wordsIDs, sentencesCount, level) {
    if (wordsIDs.length > 0) {
        const siteName = window.location.href.split('/').slice(0, 3).join('/');
        const lang = window.location.href.split('/')[5].slice(8, -6);
        let url = `${siteName}/exercises/dialog/json/generate_dialog/${lang}`
        
        fetch(url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(
                {
                    'words_ids': wordsIDs,
                    'sentences_count': sentencesCount,
                    'level': level
                }),
            })
            .then(response => response.json())
            .then(data => {
                const TextAreaElement = document.querySelector('#id_text');
                TextAreaElement.value = data.result;
                changeIcons();
                return;
            })
            .catch(error => {
                console.error('Error:', error);
                changeIcons();
                return;
            })
    } else {
        alert('Пожалуйста, сначала выберите слова и только после этого на генерацию текста.');
        changeIcons();
        return;
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
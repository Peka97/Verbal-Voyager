

document.addEventListener('DOMContentLoaded', function() {
    const currentWord = document.getElementById('id_word');
    const wordModelRow = currentWord.parentElement.parentElement.parentElement;

    const LoadAPIDataWrapperElement = document.createElement('div');

    const LoadAPIDataLinkElement = document.createElement('a');
    LoadAPIDataLinkElement.title = 'Заполнить поля'
    LoadAPIDataLinkElement.style.margin = 'auto'

    const LoadAPIDataImageElement = document.createElement('img');
    LoadAPIDataImageElement.src = '/static/admin/img/icon-changelink.svg'
    LoadAPIDataImageElement.width = 20
    LoadAPIDataImageElement.height = 20

    wordModelRow.appendChild(LoadAPIDataWrapperElement)
    LoadAPIDataWrapperElement.appendChild(LoadAPIDataLinkElement)
    LoadAPIDataLinkElement.appendChild(LoadAPIDataImageElement)

    LoadAPIDataLinkElement.addEventListener('click', SendToLoadDataFromAPI)

    function SendToLoadDataFromAPI () {
        const word = currentWord.value;
        const translation = document.getElementById('id_translation').value;
        
        if (word.length > 0) {
            const siteName = window.location.href.split('/').slice(0, 3).join('/');
            let url = `${siteName}/dictionary/json/load_from_api/english`
            let WordID;

            if (window.location.href.indexOf('/change/') > -1) {
                WordID = window.location.href.split('/')[6];
            } 
            
            fetch(url, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(
                    {
                        'word': word,
                        'word_id': WordID,
                        'translation': translation
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data['means']) {
                        alert(`Для слова "${word}" найдены значения:\n${data['means'].join('\n')}.\nИзмените поле с переводом на любое из предложенных.`)
                    } else if (data['error']) {
                        alert(data['error'])
                    } else {
                        document.getElementById('id_prefix').value = data['prefix']
                        document.getElementById('id_speech_code').value = data['speech_code']
                        document.getElementById('id_transcription').value = data['transcription']
                        document.getElementById('id_definition').value = data['definition']
                        document.getElementById('id_examples').value = data['examples']
                        document.getElementById('id_image_url').value = data['image_url']
                        document.getElementById('id_sound_url').value = data['sound_url']
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    LoadAPIDataLinkElement.classList.remove('disabled-link');
                })
        } else {
            alert('Пожалуйста, заполните поле "Слово в оригинале"')
            LoadAPIDataLinkElement.classList.remove('disabled-link');
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
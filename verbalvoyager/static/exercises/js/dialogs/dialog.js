import { showToast } from '/static/pages/js/modules/toast_notification.js';
import { send_points } from '../modules/send_points.js';


let messages = [...document.getElementsByClassName("message")];
let names = document.getElementById("names").dataset;
let words_lenght = document.getElementById("words-length").dataset.wordsLength;
let words = findWords();
const maxWordsInSubmenu = Math.min(words.length, 3)

setOrderInMessageContainer();
insertDropdownInMessages();
fillSubMenuElements();

function findWords() {
    let result = Array();
    for (let index = 1; index <= words_lenght; index++) {
        let element_id = `word_${index}`;
        let element = document.getElementById(element_id)
        result.push(element);
    }
    return result;
}

function setOrderInMessageContainer() {
    let avatars = [...document.getElementsByClassName('avatar-container')]
    for (let i = 0; i < avatars.length; i++) {
        if ((i + 1) % 2 === 0) {
            avatars[i].classList.add('order-2')
        }
}}

function insertDropdownInMessages() {
    messages.forEach(message => {
        let message_text = message.innerText.toLowerCase();

        words.forEach(wordEl => {
            let word = wordEl.dataset["word"]
            const regexStr = `\\b(\\S')?(${word.toLowerCase()})('\\S)?\\b`

            const regex = new RegExp(regexStr, 'g');
            let matches = message_text.matchAll(regex);
            if (matches) {
                let uniquedMatches = new Object();
                matches.forEach(match => {
                    if (uniquedMatches[match[0]] !== 'undefined') {
                        uniquedMatches[match[0]] = match
                    }
                })
                for (let matchKey in uniquedMatches) {
                    let matchWord = uniquedMatches[matchKey][2];

                    let dropDownHTML = `
                        <div class="menu">
                            <div class="item" data-key="${wordEl.dataset['word']}">
                                <a href="#" class="menu-word-link">
                                <span class='word-rus'> ${wordEl.dataset['translation'].toLowerCase()} </span>
                                <svg viewBox="0 0 360 360" xml:space="preserve">
                                    <g id="SVGRepo_iconCarrier">
                                    <path
                                        id="XMLID_225_"
                                        d="M325.607,79.393c-5.857-5.857-15.355-5.858-21.213,0.001l-139.39,139.393L25.607,79.393 c-5.857-5.857-15.355-5.858-21.213,0.001c-5.858,5.858-5.858,15.355,0,21.213l150.004,150c2.813,2.813,6.628,4.393,10.606,4.393 s7.794-1.581,10.606-4.394l149.996-150C331.465,94.749,331.465,85.251,325.607,79.393z"
                                    ></path>
                                    </g>
                                </svg>
                                </a>
                                <div class="dropdown submenu"></div>
                            </div>
                        </div>
                        `
                        message.innerHTML = message.innerHTML.replaceAll(matchWord, dropDownHTML)
                    }
                }
            }
        )
    }
)}


function fillSubMenuElements() {
    let dropDownSubmenu = [...document.getElementsByClassName('dropdown submenu')];

    dropDownSubmenu.forEach(subMenu => {
        const keyWord = subMenu.parentElement.dataset['key'];
        const wordsVariants = getWordsVariants(keyWord)

        for(var i=0;i < wordsVariants.length; i++) {
            let subMenuElement = document.createElement('div')
            subMenuElement.className = 'submenu-item'
            let subMenuWordLink = document.createElement('a')
            subMenuWordLink.className = 'submenu-word-link'
            subMenuWordLink.href = '#'
            subMenuWordLink.value = wordsVariants[i].dataset.translation
            subMenuWordLink.text = wordsVariants[i].dataset.word

            subMenuElement.appendChild(subMenuWordLink)
            subMenu.appendChild(subMenuElement)
        }
    })
}

function getWordsVariants(keyWord) {
    let wordsCopy = shuffle(words.slice())
    let keyWordsElement = document.querySelector(`meta[data-word=${keyWord}]`);
    
    let wordsList = Array();

    for (let wordIdx=0; wordsList.length < maxWordsInSubmenu; wordIdx++) {
        if (wordsCopy[wordIdx] !== keyWordsElement) {
            wordsList.push(wordsCopy[wordIdx])
        }
    }

    wordsList.push(keyWordsElement)
    
    return wordsList;
}

function shuffle(array) {
    var currentIndex = array.length, temporaryValue, randomIndex;
   
    while (0 !== currentIndex) {
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex -= 1;
   
      temporaryValue = array[currentIndex];
      array[currentIndex] = array[randomIndex];
      array[randomIndex] = temporaryValue;
    }
   
    return array;
  }


let word_links = [... document.getElementsByClassName('submenu-word-link')];
let menus = [...document.getElementsByClassName('menu')];
let points = menus.length;
word_links.forEach(word_link => {
    word_link.addEventListener('click', (event) => {
        event.preventDefault();

        let el = event.target
        const menu = el.parentElement.parentElement.parentElement.parentElement
        const key = el.parentElement.parentElement.parentElement.dataset.key.toLowerCase();
        const chosen = el.firstChild.data.toLowerCase();
        
        if (key != chosen) {
            menu.classList.remove('correct');
            menu.classList.add('wrong');
            if (points > 1) {
                points--;
            }
        } else {
            menu.firstElementChild.firstElementChild.firstElementChild.innerText = key
            menu.classList.remove('wrong');
            menu.classList.add('correct');
        }

        allWordsCorrect();
    })
})

function allWordsCorrect() {
    for (let i=0; i < menus.length; i++) {
        if (!menus[i].classList.contains('correct')) {
            return false;
        }
    }

    send_points('dialog', points);
    showToast('Отлично! Теперь прочитай получившийся текст и после возвращайся в личный кабинет.');
}

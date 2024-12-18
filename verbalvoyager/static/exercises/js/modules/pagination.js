export let pagination = [...document.querySelector('ul.pagination').children];
document.getElementById('page_1').classList.add('active');

const prev_btn = document.getElementById('prev_btn');
const next_btn = document.getElementById('next_btn');
const last_page_num = [...document.getElementsByClassName('page-item')].length - 2


export function updatePagination(event) {
    if (event.target.classList.contains('disabled')) {return false};
    
    let current_word_block = document.querySelector('div.word__block:not(.hidden)');
    let page_li = event.target.parentElement;
    let page_num = page_li.id.slice(page_li.id.indexOf('_') + 1);
    let page_items = [... document.getElementsByClassName('page-item')]
    page_items.forEach(el => {
        el.classList.remove('active')
    })
    
    if (isNaN(page_num)) {
        let direction = page_li.id.slice(0,page_li.id.indexOf('_'))
        page_num = current_word_block.id.slice(page_li.id.indexOf('_') + 1)
        if (direction == 'next') {
            page_num++;
        } else {
            page_num--;
        }
        document.getElementById(`page_${page_num}`).classList.add('active')
    } else {
        page_li.classList.add('active')
    }

    if (page_num == 1) {
        next_btn.classList.remove('disabled')
        prev_btn.classList.add('disabled')
    } else if (page_num == last_page_num) {
        next_btn.classList.add('disabled')
        prev_btn.classList.remove('disabled')
    } else {
        prev_btn.classList.remove('disabled')
        next_btn.classList.remove('disabled')
    }

    let new_page = document.getElementById(`word_${page_num}`)
    if (new_page) {
        current_word_block.classList.add('hidden')
        new_page.classList.remove('hidden')
    }    
}


export function showToast (text) {
    const toastDelay = 5000
    const favicon = document.getElementById('favicon');
    // let toastLiveExample = document.getElementById('liveToast');
    // toastLiveExample.attributes.getNamedItem('data-bs-delay').nodeValue = '15000';
    
    // let toastBody = document.getElementById('toast-body');
    // toastBody.innerText = text;
    
    // let toast = new bootstrap.Toast();
    // toast.show();
    let toastContainer = document.getElementById('toast-container')
    const newToastHTML = `
    <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="${toastDelay}">
        <div class="toast-header">
          <img src="${favicon.href}" class="toast__ico rounded me-2" alt="verbal voyager icon">
          <strong class="me-auto">Verbal Voyager</strong>
          <small> Сейчас </small>
          <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Закрыть"></button>
        </div>
        <div class="toast-body" id="toast-body">
          ${text}
        </div>
      </div>`
    const newToastElement = htmlToElement(newToastHTML);
    toastContainer.appendChild(newToastElement);
    const toast = new bootstrap.Toast(newToastElement);
    toast.show();
}

//helper function
function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim();
    template.innerHTML = html;
    return template.content.firstChild;
}


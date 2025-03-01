const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

// Popover Auto Fade
document.addEventListener('shown.bs.popover', (event) => {
    let popoverContentId = event.target.attributes['aria-describedby'].nodeValue
    let popoverContent = document.getElementById(popoverContentId);

    setTimeout(
        () => {
            popoverContent.classList.remove('show')
        }, 3000
    )
})
const viewportHeight = window.innerHeight;

document.addEventListener("scroll", event => {
    if (window.scrollY < viewportHeight) {
        document.body.style.cssText = `--scrollTop: ${window.scrollY}px`
    }
})
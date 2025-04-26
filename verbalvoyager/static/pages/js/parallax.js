document.addEventListener("scroll", event => {
    document.body.style.cssText = `--scrollTop: ${window.scrollY}px`
})
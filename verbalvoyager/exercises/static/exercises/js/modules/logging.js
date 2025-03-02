export function logging(userInput, answer, isCorrect) {
    let token = document.getElementsByName('csrfmiddlewaretoken')[0].defaultValue;
    if (!token) {return};
    let ex_id = window.location.href.split('/').slice(-2)[0];
    let step_num = window.location.href.split('/').slice(-1)[0];

    const siteName = window.location.href.split('/').slice(0, 3).join('/');
    let url = `${siteName}/exercises/logging/${ex_id}/step_${step_num}`;

    let data = {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': token,
        },
        body: JSON.stringify({
            'user_input': userInput,
            'answer': answer,
            'is_correct': isCorrect
        })
    }

    fetch(url, data).then(resp => {
        if (!resp.ok) {
            console.log('Fetching');
            return;
        }
        else {
            console.log(`Status: ${resp.ok}`)
            return;
        }
    }).catch (err => {
        console.log(err)
        return;
    });
}
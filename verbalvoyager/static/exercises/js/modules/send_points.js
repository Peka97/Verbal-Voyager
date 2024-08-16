export function send_points(ex_type, points) {
    let token = document.getElementsByName('csrfmiddlewaretoken')[0].defaultValue;
    if (!token) {return};

    let ex_id = window.location.href.split('/').slice(-2, -1)[0];
    let step_num = window.location.href.split('/').slice(-1)[0];
    if (ex_type === 'words') {
        let url = `https://verbal-voyager.ru/exercises/${ex_type}/update/${ex_id}/step_${step_num}`;
    } else if (ex_type === 'dialog') {
        let url = `https://verbal-voyager.ru/exercises/${ex_type}/update/${ex_id}}`;
    } else {
        return;
    }
    let data = {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-CSRFToken': token,
        },
        body: JSON.stringify({
            'value': points
        })
    }

    fetch(url, data).then(resp => {
        if (!resp.ok) {
            return;
        }
        else {
            return;
        }
    }).catch (err => {
        return;
    });
}
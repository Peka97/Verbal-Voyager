document.addEventListener('DOMContentLoaded', function() {
    const wordsSelect = document.querySelector('select[name=words_old]');

    studentSelect.addEventListener('change', (event) => {
        const currentStudentId = event.target.value;
        const siteName = window.location.href.split('/').slice(0, 3).join('/');

        let url = `${siteName}/event_calendar/json/filter_lessons_by_student/${currentStudentId}`
        fetch(url).then(resp => {
            if (resp.ok) {
                return resp.json();
            }
        }).then(data => {
            const lessonSelect = document.querySelector('select[name=lesson_id]');
            [...lessonSelect].forEach(elem => elem.remove());
            
            console.dir(lessonSelect);

            Object.entries(data).forEach((lesson) => {
                let newOption = document.createElement('option');
                newOption.value = lesson[0];
                newOption.innerText = lesson[1];
                lessonSelect.appendChild(newOption);
            })
            console.dir(lessonSelect);
        });
    })
});
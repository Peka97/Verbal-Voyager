document.addEventListener('DOMContentLoaded', function() {
    const studentSelect = document.querySelector('select[name=student_id]');
    console.dir(studentSelect);
    studentSelect.addEventListener('change', (event) => {
        const currentStudentId = event.target.value;
        console.dir(currentStudentId)

        url = `http://127.0.0.1:8000/event_calendar/json/filter_lessons_by_student/${currentStudentId}`
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
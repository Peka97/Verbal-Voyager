(function($) {
    $(document).ready(function() {
        const studentSelect = $('#id_student');
        const lessonSelect = $('#id_lesson_id');

        studentSelect.change(function() {
            const studentId = $(this).val();
            lessonSelect.empty(); // Очищаем существующие варианты
            lessonSelect.append($('<option value="">---</option>'));

            $.ajax({
                url: '/admin/lesson/lessons/ajax/',
                data: { student_id: studentId },
                dataType: 'json',
                success: function(data) {
                    $.each(data, function(index, lesson) {
                        lessonSelect.append($('<option></option>').attr('value', lesson.id).text(lesson.title));
                    });
                },
                error: function(xhr, status, error) {
                    console.error("Error:", error);
                    lessonSelect.append($('<option value="">Ошибка загрузки уроков</option>'));
                }
            });
        });
    });
})(django.jQuery);
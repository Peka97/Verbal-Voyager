


# TODO: not work
# @pytest.mark.django_db
# def test_english_exercise_result_update(exercise_english_words, student_client):
#     for step_num in range(1, 6):
#         url = reverse(
#             'exercise_result_update',
#             kwargs={
#                 'ex_type': 'words',
#                 'ex_lang': 'english',
#                 'ex_id': exercise_english_words.id,
#                 'step_num': str(step_num)
#             },
#         )
#         headers = {
#                 'Accept': 'application/json',
#                 'Content-Type': 'application/json',
#             }
        
#         data = {
#             'body': {'value': 5}
#             }
        
#         response = student_client.post(url, data, headers=headers)
#         assert response.status_code == 200
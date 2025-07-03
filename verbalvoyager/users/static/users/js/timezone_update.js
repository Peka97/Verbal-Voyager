import { showToast } from "/static/pages/js/modules/toast_notification.js";

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form#timezone_form").lastChild;
  const submitButton = document.getElementById("submit-button");

  form.addEventListener("submit", sendFetchToUpdateTimezone);

  function sendFetchToUpdateTimezone(event) {
    event.preventDefault();
    const selectElement = event.target.parentElement[1];
    const dataToSend = { timezone: selectElement.value };

    const siteName = window.location.href.split("/").slice(0, 3).join("/");
    let url = `${siteName}/users/account/timezone/update/`;
    let token = document.getElementsByName("csrfmiddlewaretoken")[0].defaultValue;

    if (!token) {
      console.log("Couldn't find token");
      return;
    }

    let data = {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": token,
      },
      body: JSON.stringify(dataToSend),
    };

    fetch(url, data).then((resp) => {
      if (resp.ok) {
        showToast(`Часовой пояс обновлён на "${selectElement.value}"`);
        return resp.json();
      } else {
        showToast(`Ошибка обновления часового пояса. Код ${resp.status}`);
      }
    });
  }
});

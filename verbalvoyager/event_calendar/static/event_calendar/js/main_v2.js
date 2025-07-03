import { initStatusHandlers } from "/static/users/js/calendar_send_event_update_v2.js";

(function ($) {
  "use strict";

  // Setup the calendar with the current date
  $(document).ready(function () {
    // Показываем лоадер календаря
    $("#calendar-loader").show();

    // Показываем лоадер событий
    $("#events-loader").show();
    var date = new Date();
    const today = date.getDate();
    const month = date.getMonth() + 1;
    const year = date.getFullYear();

    // Set click handlers
    $(".right-button").click({ date: date }, next_year);
    $(".left-button").click({ date: date }, prev_year);
    $(".month").click({ date: date }, month_click);
    $("#add-button").click({ date: date }, new_event);

    // Set current month as active
    $(".months-row").children().eq(date.getMonth()).addClass("active-month");

    // Initialize calendar and load data
    loadMonthData().then(() => {
      init_calendar(date);
      check_events(today, month, year);
      setTimeout(() => show_events(today, month, year), 1000);
      if (userIsTeacher()) {
        setTimeout(() => initStatusHandlers(), 500);
      }
    });
  });
})(jQuery);

function userIsTeacher() {
  const metaUser = document.querySelector("meta#user_pk");
  return metaUser.dataset["teacher"] === "True";
}

async function loadModals() {
  if (userIsTeacher()) {
    return import("/static/users/js/lesson_plan_teacher_modal.js");
  } else {
    return import("/static/users/js/lesson_plan_student_modal.js");
  }
}

export function renderCalendar() {
  event_data = {
    events: [],
  };
  var date = new Date();
  var today = date.getDate();
  // Set click handlers for DOM elements
  $(".right-button").click({ date: date }, next_year);
  $(".left-button").click({ date: date }, prev_year);
  $(".month").click({ date: date }, month_click);
  $("#add-button").click({ date: date }, new_event);
  // Set current month as active
  $(".months-row").children().eq(date.getMonth()).addClass("active-month");

  init_calendar(date);
  check_events(today, date.getMonth() + 1, date.getFullYear());
  setTimeout(() => show_events(today, month, year), 1000);
  if (userIsTeacher()) {
    setTimeout(() => initStatusHandlers(), 500);
  }
}

// Initialize the calendar by appending the HTML dates
function init_calendar(date) {
  // Показываем лоадер календаря

  $("#calendar-loader").show();

  // Показываем лоадер событий
  $("#events-loader").show();

  $(".tbody").empty();
  $(".event-card").addClass("hidden");

  var calendar_days = $(".tbody");
  var month = date.getMonth();
  var year = date.getFullYear();
  var day_count = days_in_month(month, year);
  var row = $("<tr class='table-row'></tr>");

  // Сохраняем текущую дату до модификаций
  var currentDate = new Date();
  var isCurrentMonth = currentDate.getMonth() === month && currentDate.getFullYear() === year;

  date.setDate(1);
  var first_day = date.getDay();

  loadMonthData()
    .then(() => {
      var empty_card = document.getElementsByName("empty-card")[0];
      empty_card.classList.add("hidden");
      var cards = Array.from(document.getElementsByClassName(`event-card`));
      var event_days = [];
      var re = /^\d{1,2}.\d{1,2}.\d{2,4}$/;

      var cards_warn = get_card_warn();
      var cards_dang = get_card_dang();

      cards.forEach((card) => {
        card.classList.add("hidden");
        var name = card.getAttribute("name");
        if (re.exec(name)) {
          event_days.push(name);
        }
      });

      for (var i = 0; i < 35 + first_day; i++) {
        var day = i - first_day + 1;
        // Пропускаем дни, выходящие за пределы месяца
        if (day > day_count) continue;

        var full_day = `${day}.${month + 1}.${year}`;

        if (i % 7 === 0) {
          calendar_days.append(row);
          row = $("<tr class='table-row'></tr>");
        }

        if (i < first_day || day > day_count) {
          row.append($("<td class='table-date nil'>" + "</td>"));
        } else {
          var curr_date = $("<td class='table-date'>" + day + "</td>");

          // Проверяем, является ли это текущий день текущего месяца
          if (isCurrentMonth && day === currentDate.getDate()) {
            let prevActiveDate = document.querySelector("active-date");

            if (prevActiveDate) {
              prevActiveDate.classList.remove("active-date");
            }
            curr_date.addClass("active-date");
          } else if (!isCurrentMonth && day === 1) {
            let prevActiveDate = document.querySelector("active-date");

            if (prevActiveDate) {
              prevActiveDate.classList.remove("active-date");
            }
            curr_date.addClass("active-date");
          }
          if (event_days.includes(full_day)) {
            curr_date.addClass("event-date");
            if (cards_warn.includes(full_day)) {
              curr_date.addClass("event-date-warn");
            }
            if (cards_dang.includes(full_day)) {
              curr_date.addClass("event-date-dang");
            }
          }

          curr_date.click({ day: day, month: month + 1, year: year }, date_click);
          row.append(curr_date);
        }
      }

      calendar_days.append(row);
      $(".year").text(year);

      // // Автовыбор дня только если это текущий месяц
      // if (isCurrentMonth) {
      // 	setTimeout(() => {
      // 		const todayCell = $(`.table-date:not(.nil):contains('${currentDate.getDate()}'):first`);
      // 		if (todayCell.length) {
      // 			todayCell.click();
      // 		}
      // 	}, 150);
      // }
    })
    .finally(() => {
      // Скрываем лоадер и показываем календарь
      loadModals().then((modal) => modal.modalInit());
      $("#calendar-loader").hide();
    });
}

function get_card_warn() {
  let result = Array();
  let tags_without_warn_class = Array();
  // let dang_tags = [...document.getElementsByClassName('bi-exclamation-octagon')];
  let warn_tags = [...document.getElementsByClassName("bi-exclamation-triangle")];

  // dang_tags.forEach( (tag) => {
  //     tags_without_warn_class.push(tag)
  // })
  warn_tags.forEach((tag) => {
    tags_without_warn_class.push(tag);
  });

  tags_without_warn_class.forEach((tag) => {
    let card = tag.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement;
    let card_date = card.attributes.name.value;
    result.push(card_date);
  });
  return result;
}

function get_card_dang() {
  let result = Array();
  let tags_without_warn_class = Array();
  let dang_tags = [...document.getElementsByClassName("bi-exclamation-octagon")];
  // let warn_tags = [...document.getElementsByClassName('bi-exclamation-triangle')];

  dang_tags.forEach((tag) => {
    tags_without_warn_class.push(tag);
  });
  // warn_tags.forEach( (tag) => {
  //     tags_without_warn_class.push(tag)
  // })

  tags_without_warn_class.forEach((tag) => {
    let card = tag.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement;
    let card_date = card.attributes.name.value;
    result.push(card_date);
  });
  return result;
}

// Get the number of days in a given month/year
function days_in_month(month, year) {
  var monthStart = new Date(year, month, 1);
  var monthEnd = new Date(year, month + 1, 1);
  return (monthEnd - monthStart) / (1000 * 60 * 60 * 24);
}

// Event handler for when a date is clicked
function date_click(event) {
  $(".events-container").show(250);
  $("#dialog").hide(250);
  $(".active-date").removeClass("active-date");
  $(this).addClass("active-date");
  $(".event-card").addClass("hidden");
  var empty_card = document.getElementsByName("empty-card")[0];
  var cards = Array.from(document.getElementsByClassName(`event-card`));
  for (let card in cards.values()) {
    card.classList.add("hidden");
  }
  empty_card.classList.add("hidden");
  show_events(event.data.day, event.data.month, event.data.year);
}

// Event handler for when a month is clicked
function month_click(event) {
  $(".active-month").removeClass("active-month");
  $(this).addClass("active-month");

  var date = new Date();
  let today = date.getDate();
  let month = date.getMonth() + 1;
  let year = date.getFullYear();

  date.setFullYear($(".year").text());
  date.setMonth($(".month").index(this));

  init_calendar(date);

  today = date.getDate();
  check_events(today, month, year);
  setTimeout(() => show_events(today, date.getMonth() + 1, date.getFullYear()), 1000);
  if (userIsTeacher()) {
    setTimeout(() => initStatusHandlers(), 500);
  }
}

function loadMonthData() {
  const userPK = document.getElementById("user_pk").dataset.pk;
  const currentYear = document.querySelector("span.year").textContent
    ? document.querySelector("span.year").textContent
    : new Date().getFullYear();
  const currentMonth = document.querySelector("td.month.active-month").textContent;
  const { startDate, endDate } = getMonthDateRange(currentYear, currentMonth);

  return fetchMonthLessons(userPK, startDate, endDate).then((result) => {
    const eventsContainerElement = document.querySelector("div#events_container");
    eventsContainerElement.innerHTML = result.html;
    return result;
  });
}

function getMonthDateRange(year, monthName) {
  // Преобразуем название месяца в номер (0-11)
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const monthIndex = monthNames.indexOf(monthName);

  if (monthIndex === -1) {
    throw new Error(`Invalid month name: ${monthName}`);
  }

  // Создаем даты в локальном времени пользователя
  const startDate = new Date(year, monthIndex, 1);
  const endDate = new Date(year, monthIndex + 1, 0); // Последний день месяца

  // Устанавливаем время для endDate
  endDate.setHours(23, 59, 59, 999);

  return {
    startDate: startDate.toISOString(),
    endDate: endDate.toISOString(),
  };
}

function fetchMonthLessons(userPK, startDate, endDate) {
  const baseUrl = window.location.href.split("/").slice(0, 3).join("/");
  let url;
  const userIsTeacher = document.querySelector("meta#user_pk").dataset.teacher;
  if (userIsTeacher === "True") {
    url = `${baseUrl}/event_calendar/json/load_teacher_lessons/${userPK}`;
  } else {
    url = `${baseUrl}/event_calendar/json/load_student_lessons/${userPK}`;
  }

  const params = new URLSearchParams({
    start: startDate,
    end: endDate,
  });

  return fetch(`${url}?${params}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then((data) => {
      if (data.status === "OK") {
        return { html: data.html };
      } else {
        throw new Error(data.message || "Invalid response data");
      }
    });
}

// Event handler for when the year right-button is clicked
function next_year(event) {
  $("#dialog").hide(250);
  var date = event.data.date;
  var new_year = date.getFullYear() + 1;
  $("year").html(new_year);
  date.setFullYear(new_year);
  let today = date.getDate();
  let month = date.getMonth() + 1;
  console.log(today, month, new_year);
  init_calendar(date);
  check_events(today, month, new_year);
  setTimeout(() => show_events(today, date.getMonth(), date.getFullYear()), 1000);
  if (userIsTeacher()) {
    setTimeout(() => initStatusHandlers(), 500);
  }
}

// Event handler for when the year left-button is clicked
function prev_year(event) {
  $("#dialog").hide(250);
  var date = event.data.date;
  var new_year = date.getFullYear() - 1;
  $("year").html(new_year);
  date.setFullYear(new_year);
  let today = date.getDate();
  let month = date.getMonth() + 1;
  console.log(today, month, new_year);
  init_calendar(date);
  check_events(today, month, new_year);
  setTimeout(() => show_events(today, date.getMonth(), date.getFullYear()), 1000);
  if (userIsTeacher()) {
    setTimeout(() => initStatusHandlers(), 500);
  }
}

// Event handler for clicking the new event button
function new_event(event) {
  // if a date isn't selected then do nothing
  if ($(".active-date").length === 0) return;
  // remove red error input on click
  $("input").click(function () {
    $(this).removeClass("error-input");
  });
  // empty inputs and hide events
  $("#dialog input[type=text]").val("");
  $("#dialog input[type=number]").val("");
  // $(".events-container").hide(250);
  $("#dialog").show(250);
  // Event handler for cancel button
  $("#cancel-button").click(function () {
    $("#name").removeClass("error-input");
    $("#count").removeClass("error-input");
    $("#dialog").hide(250);
    $(".events-container").show(250);
  });
  // Event handler for ok button
  $("#ok-button")
    .unbind()
    .click({ date: event.data.date }, function () {
      var date = event.data.date;
      var name = $("#name").val().trim();
      var count = parseInt($("#count").val().trim());
      var day = parseInt($(".active-date").html());
      // Basic form validation
      if (name.length === 0) {
        $("#name").addClass("error-input");
      } else if (isNaN(count)) {
        $("#count").addClass("error-input");
      } else {
        $("#dialog").hide(250);
        new_event_json(name, count, date, day);
        date.setDate(day);
        init_calendar(date);
      }
    });
}

// Adds a json event to event_data
function new_event_json(name, count, date, day) {
  var event = {
    occasion: name,
    invited_count: count,
    year: date.getFullYear(),
    month: date.getMonth() + 1,
    day: day,
  };
  event_data["events"].push(event);
}

// Display all events of the selected date in card views
function show_events(day, month, year) {
  var dateStr = `${day}.${month}.${year}`;
  var cards = document.querySelectorAll(`div.event-card[name="${dateStr}"]`);
  var empty_card = document.querySelector('div[name="empty-card"]');

  // Скрываем все карточки событий
  document.querySelectorAll(".event-card").forEach((card) => {
    card.classList.add("hidden");
  });

  if (cards.length > 0) {
    empty_card.classList.add("hidden");
    cards.forEach((card) => {
      card.classList.remove("hidden");
    });
  } else {
    empty_card.classList.remove("hidden");
  }
  // Скрываем лоадер и показываем события
  $("#events-loader").hide();
}

// Checks if a specific date has any events
function check_events(day, month, year) {
  var events = [];
  for (var i = 0; i < event_data["events"].length; i++) {
    var event = event_data["events"][i];
    if (event["day"] === day && event["month"] === month && event["year"] === year) {
      events.push(event);
    }
  }
  return events;
}

// Given data for events in JSON format
var event_data = {
  events: [],
};

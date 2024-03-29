(function($) {

	"use strict";

	// Setup the calendar with the current date
$(document).ready(function(){
    var date = new Date();
    var today = date.getDate();
    // Set click handlers for DOM elements
    $(".right-button").click({date: date}, next_year);
    $(".left-button").click({date: date}, prev_year);
    $(".month").click({date: date}, month_click);
    $("#add-button").click({date: date}, new_event);
    // Set current month as active
    $(".months-row").children().eq(date.getMonth()).addClass("active-month");
    init_calendar(date);
    var events = check_events(today, date.getMonth()+1, date.getFullYear());
    // show_events(today.day, today.month, today.year);
});

// Initialize the calendar by appending the HTML dates
function init_calendar(date) {
    $(".tbody").empty();
    $(".event-card").addClass('hidden');
    
    var calendar_days = $(".tbody");
    var month = date.getMonth();
    var year = date.getFullYear();
    var day_count = days_in_month(month, year);
    var row = $("<tr class='table-row'></tr>");
    var today = date.getDate();
    // Set date to 1 to find the first day of the month
    date.setDate(1);
    var first_day = date.getDay();

    var empty_card = document.getElementsByName('empty-card')[0];
    empty_card.classList.add('hidden');
    var cards = Array.from(document.getElementsByClassName(`event-card`));
    var event_days = Array()
    var re = /^\d{1,2}.\d{1,2}.\d{2,4}$/
    var cards_warn = get_card_warn()

    cards.forEach( (card) => {
        card.classList.add('hidden')
        var name = card.getAttribute('name')

        if (re.exec(name)) {
            event_days.push(name)
        }
    }
    );

    // 35+firstDay is the number of date elements to be added to the dates table
    // 35 is from (7 days in a week) * (up to 5 rows of dates in a month)
    for(var i=0; i<35+first_day; i++) {
        // Since some of the elements will be blank, 
        // need to calculate actual date from index
        var day = i-first_day+1;
        var full_day = `${i-first_day+1}.${month+1}.${year}`
        // If it is a sunday, make a new row
        if(i%7===0) {
            calendar_days.append(row);
            row = $("<tr class='table-row'></tr>");
        }
        // if current index isn't a day in this month, make it blank
        if(i < first_day || day > day_count) {
            var curr_date = $("<td class='table-date nil'>"+"</td>");
            row.append(curr_date);
        }   
        else {
            var curr_date = $("<td class='table-date'>"+day+"</td>");
            var events = check_events(day, month+1, year);
            if(today===day && $(".active-date").length===0) {
                curr_date.addClass("active-date");
                show_events(day, month + 1, year);
            }
            // If this date has any events, style it with .event-date
            if(event_days.includes(full_day) && cards_warn.includes(full_day)) {
                curr_date.addClass("event-date-warn");
            }
            if (event_days.includes(full_day)) {
                curr_date.addClass("event-date");
            }
            
            // Set onClick handler for clicking a date
            curr_date.click({events: events, day: day, month: month + 1, year: year}, date_click);
            row.append(curr_date);
        }
    }
    
    
    // Append the last row and set the current year
    calendar_days.append(row);
    $(".year").text(year);
}

function get_card_warn () {
    let result = Array()
    let tags_without_warn_class = Array()
    let dang_tags = Array.from(document.getElementsByClassName('bi text-danger'))
    let warn_tags = Array.from(document.getElementsByClassName('bi text-warning'))

    dang_tags.forEach( (tag) => {
        tags_without_warn_class.push(tag)
    })
    warn_tags.forEach( (tag) => {
        tags_without_warn_class.push(tag)
    })
    
    tags_without_warn_class.forEach( (tag) => {
        let card = tag.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement
        console.dir(card)
        let card_date = card.attributes.name.value
        result.push(card_date)
    }
    )
    return result
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
    $(".event-card").addClass('hidden');
    var empty_card = document.getElementsByName('empty-card')[0];
    var cards = Array.from(document.getElementsByClassName(`event-card`));
    for (let card in cards.values()) {
        card.classList.add('hidden');
    };
    empty_card.classList.add('hidden');
    show_events(event.data.day, event.data.month, event.data.year );
};

// Event handler for when a month is clicked
function month_click(event) {
    $(".events-container").show(250);
    $("#dialog").hide(250);
    var date = event.data.date;
    $(".active-month").removeClass("active-month");
    $(this).addClass("active-month");
    var new_month = $(".month").index(this);
    date.setMonth(new_month);
    init_calendar(date);
}

// Event handler for when the year right-button is clicked
function next_year(event) {
    $("#dialog").hide(250);
    var date = event.data.date;
    var new_year = date.getFullYear()+1;
    $("year").html(new_year);
    date.setFullYear(new_year);
    init_calendar(date);
}

// Event handler for when the year left-button is clicked
function prev_year(event) {
    $("#dialog").hide(250);
    var date = event.data.date;
    var new_year = date.getFullYear()-1;
    $("year").html(new_year);
    date.setFullYear(new_year);
    init_calendar(date);
}

// Event handler for clicking the new event button
function new_event(event) {
    // if a date isn't selected then do nothing
    if($(".active-date").length===0)
        return;
    // remove red error input on click
    $("input").click(function(){
        $(this).removeClass("error-input");
    })
    // empty inputs and hide events
    $("#dialog input[type=text]").val('');
    $("#dialog input[type=number]").val('');
    // $(".events-container").hide(250);
    $("#dialog").show(250);
    // Event handler for cancel button
    $("#cancel-button").click(function() {
        $("#name").removeClass("error-input");
        $("#count").removeClass("error-input");
        $("#dialog").hide(250);
        $(".events-container").show(250);
    });
    // Event handler for ok button
    $("#ok-button").unbind().click({date: event.data.date}, function() {
        var date = event.data.date;
        var name = $("#name").val().trim();
        var count = parseInt($("#count").val().trim());
        var day = parseInt($(".active-date").html());
        // Basic form validation
        if(name.length === 0) {
            $("#name").addClass("error-input");
        }
        else if(isNaN(count)) {
            $("#count").addClass("error-input");
        }
        else {
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
        "occasion": name,
        "invited_count": count,
        "year": date.getFullYear(),
        "month": date.getMonth()+1,
        "day": day
    };
    event_data["events"].push(event);
}

// Display all events of the selected date in card views
function show_events(day, month, year) {
    var cards = document.getElementsByName(`${day}.${month}.${year}`);
    var empty_card = document.getElementsByName('empty-card')[0];

    // Clear the dates container
    // $(".events-container").empty();
    $(".events-container").show(250);
    // If there are no events for this date, notify the user
    if(cards.length != 0) {
        empty_card.classList.add('hidden');
        cards.forEach( (card) => {
            card.classList.remove('hidden');
        }
        )
    }
    else {
        cards.forEach( (card) => {
            card.classList.add('hidden');
        }
        )
        empty_card.classList.remove('hidden');
        $(empty_card).css({ "border-left": "10px solid #FF1744" });

        // Go through and add each event as a card to the events container
        

        // var event_card = $("<div class='event-card'></div>");
        // var event_name = $("<div class='event-name'>"+events[i]["occasion"]+":</div>");
        // var event_count = $("<div class='event-count'>"+events[i]["invited_count"]+" Invited</div>");
        // if(events[i]["cancelled"]===true) {
        //     $(event_card).css({
        //         "border-left": "10px solid #FF1744"
        //     });
        //     event_count = $("<div class='event-cancelled'>Cancelled</div>");
        // }
        // $(event_card).append(event_name).append(event_count);
        // $(".events-container").append(event_card);
        
    }
}

// Checks if a specific date has any events
function check_events(day, month, year) {
    var events = [];
    for(var i=0; i<event_data["events"].length; i++) {
        var event = event_data["events"][i];
        if(event["day"]===day &&
            event["month"]===month &&
            event["year"]===year) {
                events.push(event);
            }
    }
    return events;
}

// Given data for events in JSON format


var event_data = {
    "events": [
        {"occasion": " Some text ",
        "invited_count": 120,
        "year": 2023,
        "month": 8,
        "day": 23,
        "cancelled": false},
    {
        "occasion": " Repeated Test Event ",
        "invited_count": 120,
        "year": 2023,
        "month": 8,
        "day": 23,
        "cancelled": true
    },
    {
        "occasion": " Repeated Test Event ",
        "invited_count": 120,
        "year": 2020,
        "month": 5,
        "day": 10,
        "cancelled": true
    },
        {
        "occasion": " Repeated Test Event ",
        "invited_count": 120,
        "year": 2020,
        "month": 5,
        "day": 10,
        "cancelled": true
    },
    {
        "occasion": " Repeated Test Event ",
        "invited_count": 120,
        "year": 2020,
        "month": 5,
        "day": 10
    },
        {
        "occasion": " Repeated Test Event ",
        "invited_count": 120,
        "year": 2020,
        "month": 5,
        "day": 10,
        "cancelled": true
    },
    {
        "occasion": " Repeated Test Event ",
        "invited_count": 120,
        "year": 2020,
        "month": 5,
        "day": 10
    },
        {
        "occasion": " Repeated Test Event ",
        "invited_count": 120,
        "year": 2020,
        "month": 5,
        "day": 10,
        "cancelled": true
    },
    {
        "occasion": " Repeated Test Event ",
        "invited_count": 120,
        "year": 2020,
        "month": 5,
        "day": 10
    },
        {
        "occasion": " Repeated Test Event ",
        "invited_count": 120,
        "year": 2020,
        "month": 5,
        "day": 10,
        "cancelled": true
    },
    {
        "occasion": " Repeated Test Event ",
        "invited_count": 120,
        "year": 2020,
        "month": 5,
        "day": 10
    },
    {
        "occasion": " Test Event",
        "invited_count": 120,
        "year": 2020,
        "month": 5,
        "day": 11
    }
    ]
};

const months = [ 
    "January", 
    "February", 
    "March", 
    "April", 
    "May", 
    "June", 
    "July", 
    "August", 
    "September", 
    "October", 
    "November", 
    "December" 
];

})(jQuery);

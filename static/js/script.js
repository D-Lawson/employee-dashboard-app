/*
    jQuery for initialisations
*/

$(document).ready(function () {
    $("#activity-form").hide();
    $('.sidenav').sidenav();
    $('.collapsible').collapsible();
    $("select").formSelect();
    $(".datepicker").datepicker({
        format: "dd mmmm, yyyy",
        yearRange: 3,
        showClearBtn: true,
        i18n: {
            done: "Select"
        }
    });
    $('#add-activity').click(function () {
        $('#activity-form').fadeToggle(800);
    });
});


/*
    Conditional formatting for overdue, due within 1 week, due within 2 weeks
*/

var number = $('.hide').length;
for (let i = 0; i < number; i++) {

    var dateid = `date-target-${[i+1]}`;
    var date = document.getElementById(dateid).innerHTML;
    var varDate = new Date(date);
    var today = new Date();

    Date.prototype.addDays = function (days) {
        var date = new Date(this.valueOf());
        date.setDate(date.getDate() + days);
        return date;
    };

    if (varDate <= today) {
        document.getElementById(`conditional-bg-${[i+1]}`).innerHTML = "warning";
        document.getElementById(`conditional-bg-${[i+1]}`).style.color = "red";
    } else if (varDate < today.addDays(7)) {
        document.getElementById(`conditional-bg-${[i+1]}`).style.color = "red";
    } else if (varDate < today.addDays(14)) {
        document.getElementById(`conditional-bg-${[i+1]}`).style.color = "orange";
    }
}


/*
    Convert completed date to string
*/

var dayFormat = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
};

if (window.location.href.indexOf("history") > -1) {

    var date_number = $('.due-by').length;
    for (let i = 0; i < date_number; i++) {

        let dateValue = document.getElementById(`date-completed-${[i+1]}`).innerHTML;

        let dateConvert = Date.parse(dateValue);

        let dateFinal = new Date(dateConvert).toLocaleDateString('en-GB', dayFormat);

        document.getElementById(`date-completed-${[i+1]}`).innerHTML = 'Date completed:' + ' ' + `<strong>` + dateFinal + `</strong>`;
    }
}
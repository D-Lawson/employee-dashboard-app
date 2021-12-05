/*
    jQuery for initialisations
*/

$(document).ready(function () {
    $( "#activity-form" ).hide();
    $('.sidenav').sidenav();
    $('.collapsible').collapsible();
    $("select").formSelect();
    $(".datepicker").datepicker({
        format: "dd mmmm, yyyy",
        yearRange: 3,
        showClearBtn: true,
        i18n: {done: "Select"}
    });
    $('#add-activity').click(function() {
        $('#activity-form').fadeToggle(800);
    })
    });


/*
    Conditional formatting for overdue, due within 1 week, due within 2 weeks
*/

number = $('.hide').length;
for (i = 0; i < number; i++) {

    var dateid = `date-target-${[i+1]}`;
    var date = document.getElementById(dateid).innerHTML;
    var varDate = new Date(date);
    var today = new Date();

    Date.prototype.addDays = function(days) {
        var date = new Date(this.valueOf());
        date.setDate(date.getDate() + days);
        return date;
    }

    if(varDate <= today) {
        document.getElementById(`conditional-bg-${[i+1]}`).innerHTML = "warning";
        document.getElementById(`conditional-bg-${[i+1]}`).style.color = "red";
        } else if (varDate < today.addDays(7)) {
            document.getElementById(`conditional-bg-${[i+1]}`).style.color = "red";
        } else if (varDate < today.addDays(14)) {
            document.getElementById(`conditional-bg-${[i+1]}`).style.color = "orange";
        }
    }



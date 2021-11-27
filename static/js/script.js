/*
    jQuery for MaterializeCSS initialization
*/

$(document).ready(function () {
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
    });

/*
    Conditional formatting for due in 1 week, due in 2 weeks
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

    if(varDate < today.addDays(7)){
        document.getElementById(`conditional-bg-${[i+1]}`).style.color = "red";
        } else if (varDate < today.addDays(14)) {
            document.getElementById(`conditional-bg-${[i+1]}`).style.color = "orange";
        }
}

/*
    Test for responsive text
*/

length1 = $('.hide').length
for (i = 0; i < length1; i++) {

    get_length = document.getElementsByClassName(`length-size-${[i+1]}`).innerHTML.length;

    if((get_length > 30) && ($(window).width() < 992)){
        document.getElementsByClassName(`length-size-${[i+1]}`).style.fontSize = "x-small";
        } 
}
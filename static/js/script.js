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


number = $('.hide').length
for (i = 0; i < number; i++) {


    var dateid = `date-target-${[i+1]}`
    var date = document.getElementById(dateid).innerHTML;
    var varDate = new Date(date);
    var today = new Date();

    console.log(date)

    Date.prototype.addDays = function(days) {
        var date = new Date(this.valueOf());
        date.setDate(date.getDate() + days);
        return date;
    }

    console.log(varDate)
    console.log(today)

    if(varDate < today.addDays(7)){
        document.getElementById(`conditional-bg-${[i+1]}`).style.color = "red";
        } else if (varDate < today.addDays(14)) {
            document.getElementById(`conditional-bg-${[i+1]}`).style.color = "orange";
        }

}


/**
 * Created by peyton on 2/18/16.
 */
function updateTimer() {
    $.ajax({
        'url': '/get_timer_tick',
        success: function (time) {
            $("#timerText").text(pad(Math.floor(time / 3600), 2) + ":" + pad(Math.floor((time % 3600) / 60), 2) + ":" + pad(time % 60, 2))

        }
    })
}
function pad(n, width) {
    var n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join('0') + n;
}
function hide_and_approve(subject) {
    var my_content = document.getElementById(subject).innerHTML;
    var tick = document.getElementById("approved");
    var approve = tick.insertRow(tick.rows.length);
    approve.innerHTML = my_content;
    approve.deleteCell(4);
}

function delete_row(subject)
{
    document.getElementById("to_approve");
    var i = subject.parentNode.parentNode.rowIndex;
    document.getElementById("to_approve").deleteRow(i);
}

function register(subject)
{
    var my_content = document.getElementById(subject).innerHTML;
    var tick = document.getElementById("enrolled");
    var enroll = tick.insertRow(tick.rows.length);
    enroll.innerHTML = my_content;
    enroll.deleteCell(4);
}

function delete_subject(subject)
{
    document.getElementById("all");
    var i = subject.parentNode.parentNode.rowIndex;
    document.getElementById("all").deleteRow(i);
}

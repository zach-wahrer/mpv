function checkEmail() {

    var status = document.getElementById("status");

    // If email address is not blank
    if (document.getElementById("email").value) {
        // Check to make sure it is valid, thanks emailregex.com for the regex
        if (/^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(document.getElementById("email").value)) {
            document.getElementById('vbutton').style.display = "none";
            status.innerHTML = "<img src='static/blocks.gif' />";
            return true;
        }
        else {
            status.innerHTML = "Please enter a valid email address.";
            status.style.color = "red";
            return false;
        }
    }
    // If email address is blank, error
    else {
        status.innerHTML = "You must enter an email address.";
        status.style.color = "red";
        return false;
    }
}

function loading() {
    document.getElementById("lbutton").style.display = "none";
    document.getElementById("loadingframe").innerHTML = "<img src='static/blocks.gif' />";
    return true;
}

function toggle(which) {
    var block = document.getElementById(which);
    var link = document.getElementById(which+'link');
    if (block.style.display === "none") {
        block.style.display = "block";
        link.style.fontWeight = "bold";
        link.style.textDecoration = "underline";
    }
    else {
        block.style.display = "none";
        link.style.fontWeight = "normal";
        link.style.textDecoration = "none";
    }
}

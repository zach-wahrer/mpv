function emailLoading() {
    email = document.getElementById("email").value;
    if (email != "") {
        document.getElementById('vbutton').style.display = "none";
        document.getElementById('status').innerHTML = "<img src=static/blocks.gif />";
        return true;
    }
}

function testLoading() {
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

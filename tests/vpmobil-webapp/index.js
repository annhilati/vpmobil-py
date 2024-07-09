var txtList = []

window.onload = function() {
    var tmpList = document.getElementsByClassName("bigContTxt")
    for (let i = 0; i < tmpList.length; i++) {
        const element = tmpList[i];
        if(element.id == "txt" + i.toString()) {
            txtList.push(element)
        }
    }
}

//Code, um die Informationen des heutigen Tages zu bekommen
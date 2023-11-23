function RollDownUserMenu(){
    document.getElementById('user-menu').classList.toggle("user-menu");
    document.getElementById('user-menu').classList.toggle("hidden");
}

function showChangePicOptions(){
    document.getElementById('pop-back').classList.toggle("show");
    document.getElementById('pop-back').classList.toggle("popup-background");
}

function displayImage() {
    var fileInput = document.getElementById('profile_picture');
    var previewSelectedImage = document.getElementById('previewSelectedImage');
    document.querySelector('ion-icon[name="add-outline"]').style.display = "none";
    var radios = document.querySelectorAll('input[type="radio"]');
    radios.forEach(function(radioButton) {
        radioButton.checked = false;
    });
    previewSelectedImage.style = "border: solid; border-color: blueviolet;";

    if (fileInput.files && fileInput.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            previewSelectedImage.style.backgroundImage = "url('" + e.target.result + "')";
        };

        reader.readAsDataURL(fileInput.files[0]);
    }
    else{
        document.querySelector('ion-icon[name="add-outline"]').style.display = "block";
        previewSelectedImage.style = "border: none";
    }
}

function noBorderImageSelector(){
    var previewSelectedImage = document.getElementById('previewSelectedImage');
    previewSelectedImage.style = "border: none";
    document.querySelector('ion-icon[name="add-outline"]').style.display = "block";
    var fileInput = document.getElementById('profile_picture');
    fileInput.value = '';
}

function DisplayFlashcardsFrom(module_id){
    window.location.href = "/module_id=" + module_id;
}

function ShowKeyboard(){
    document.getElementById('keys').classList.toggle("keys");
    //document.getElementById('keys').classList.toggle("hidden");
    document.querySelector('#input-answer').focus();
    document.querySelector('#caret-down').classList.toggle("hidden");
    document.querySelector('#caret-up').classList.toggle("caret-up");
    document.querySelector('#caret-up').classList.toggle("show");
}

function enterButton(id){
    array = ['á','é','í','ó','ú','ü','ñ', '¿','Á','É','Í','Ó','Ú','Ü','Ñ','¡'];
    document.querySelector('#input-answer').value += array[id];
    document.querySelector('#input-answer').focus();
}

function showPassword(item){
    ancestor = item.previousElementSibling;
    if(ancestor.type === "password"){
        ancestor.type = "text";
    }
    item.nextElementSibling.style.display = "block";
    item.style.display = "none";
}

function hidePassword(item){
    ancestor_2 = item.previousElementSibling;
    ancestor = ancestor_2.previousElementSibling;
    if(ancestor.type === "text"){
        ancestor.type = "password";
    }
    item.previousElementSibling.style.display = "block";
    item.style.display = "none";
}

function showInfo() {
    document.querySelector(".popup-background").style.display = "flex";
}

function closeInfo() {
    document.querySelector(".popup-background").style.display = "none";
}

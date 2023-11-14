function RollDownUserMenu(){
    document.getElementById('user-menu').classList.toggle("user-menu");
    document.getElementById('user-menu').classList.toggle("hidden");
}

function showChangePicOptions(){
    document.getElementById('change_profile_pic').classList.toggle("change_profile_pic");
    document.getElementById('change_profile_pic').classList.toggle("hidden");
}

function showOutline(){
    document.getElementsByClassName('image_option').forEach(el => {
        console.log(el);
    });
}

function DisplayFlashcardsFrom(module_id){
    window.location.href = "/module_id=" + module_id;
}

const cards = document.querySelectorAll(".card");
cards.forEach(card => {
    card.addEventListener("click", flipCard);
});

function flipCard() {
this.classList.toggle("flipCard");
}


const slider = document.querySelector('.flashcards-slideshow')
const slides = Array.from(document.querySelectorAll('.card'))
let currentIndex = 0;

function PreviousFlashcard(){
    if(currentIndex != 0){
        photo_width = getCurrentElementWidth();
        slider.style.transform = `translateX(${-photo_width*(currentIndex-1)}px)`
        currentIndex -= 1;
    }

}

function NextFlashcard(){
    if(currentIndex != slides.length-1){
        photo_width = getCurrentElementWidth();
        slider.style.transform = `translateX(${-photo_width*(currentIndex+1)}px)`
        currentIndex += 1;
    }
}

function getCurrentElementWidth(){
    return parseFloat(document.getElementById("card-0").getBoundingClientRect().width).toFixed(2);
}
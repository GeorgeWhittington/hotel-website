// George Whittington, Student ID: 20026036, 2022

const buttons = document.querySelectorAll(".carousel-control");
const carousel = document.querySelector(".carousel-inner");
const carouselItems = document.querySelectorAll(".carousel-item");

function scrollCarouselLeft() {
    let carouselPosition = carousel.getBoundingClientRect();

    for (let i=0; i<carouselItems.length; i++) {
        let cardPosition = carouselItems[i].getBoundingClientRect();
        // is the end of the card before the start of the carousel?
        if ((cardPosition.x + cardPosition.width) > carouselPosition.x) {
            // is the start of the card before the start of the carousel?
            if (cardPosition.x < carouselPosition.x) {
                carouselItems[i].scrollIntoView();
                return;
            } else {
                // is there a card before it to make visible?
                if (i - 1 < 0) {
                    carouselItems[i].scrollIntoView();
                    return;
                } else {
                    carouselItems[i - 1].scrollIntoView();
                    return;
                }
            }
        }
    }
}

function scrollCarouselRight() {
    let carouselPosition = carousel.getBoundingClientRect();

    for (let i=0; i<carouselItems.length; i++) {
        let cardPosition = carouselItems[i].getBoundingClientRect();
        // is the end of the card after the start of the carousel?
        if ((cardPosition.x + cardPosition.width) > carouselPosition.x) {
            // is there a card after it to make visible?
            if (i + 1 > carouselItems.length) {
                return;
            } else {
                carousel.scroll(carouselItems[i + 1].offsetLeft - Math.ceil(carouselPosition.x), 0);
                return;
            }
        }
    }
}

buttons[0].addEventListener("click", scrollCarouselLeft);
buttons[1].addEventListener("click", scrollCarouselRight);
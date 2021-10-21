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
                carousel.scroll(carouselItems[i].offsetLeft - carouselPosition.x, 0);
                return;
            } else {
                // is there a card before it to make visible?
                if (i - 1 < 0) {
                    carousel.scroll(carouselItems[i].offsetLeft - carouselPosition.x, 0);
                    return;
                } else {
                    carousel.scroll(carouselItems[i - 1].offsetLeft - carouselPosition.x, 0);
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
                carousel.scroll(carouselItems[i + 1].offsetLeft - carouselPosition.x, 0);
                return;
            }
        }
    }
}

buttons[0].addEventListener("click", scrollCarouselLeft);
buttons[1].addEventListener("click", scrollCarouselRight);
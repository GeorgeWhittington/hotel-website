const nav = document.querySelector("nav");
const navButton = document.querySelector("nav .nav-button");
const navCurrencySelect = document.querySelector("nav .selectNative");

const startHeight = nav.offsetHeight;

// transform between 2 distinct heights so css transitions can work in both directions
function expandSection() {
    const currentHeight = nav.scrollHeight;
    nav.style.height = currentHeight + "px";
    nav.className = "menu-open";
}

function collapseSection() {
    const currentHeight = nav.scrollHeight;
    nav.style.height = currentHeight + "px";
    nav.style.height = startHeight + "px";
    nav.className = "menu-closed";
}

function toggleNav() {
    if (nav.className === "menu-closed") {
        expandSection();
    } else {
        collapseSection();
    }
}

function toggleNavKeyboard(e) {
    // Spacebar
    if (e.keyCode === 32) {
        toggleNav();
    }
}

function closeNavMenu() {
    if (window.innerWidth > 768) {
        collapseSection();
    }
}

// Link currency select in nav bar to a cookie
function currencyUpdate(event) {
    document.cookie = "current_currency=" + event.target.value;
    window.location.reload();
}

window.addEventListener("resize", closeNavMenu);
navButton.addEventListener("click", toggleNav);
navButton.addEventListener("keyup", toggleNavKeyboard);
navCurrencySelect.addEventListener("change", currencyUpdate);
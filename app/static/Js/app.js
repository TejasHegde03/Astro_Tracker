// Step 1: get DOM
let nextDom = document.getElementById('next');
let prevDom = document.getElementById('prev');

let carouselDom = document.querySelector('.carousel');
let SliderDom = carouselDom.querySelector('.carousel .list');
let thumbnailBorderDom = document.querySelector('.carousel .thumbnail');
let thumbnailItemsDom = thumbnailBorderDom.querySelectorAll('.item');
let timeDom = document.querySelector('.carousel .time');

let currentIndex = 0; // Track the index of the currently visible item

thumbnailBorderDom.appendChild(thumbnailItemsDom[0]);

nextDom.onclick = function () {
    showSlider('next');
}

prevDom.onclick = function () {
    showSlider('prev');
}

function showSlider(type) {
    let SliderItemsDom = SliderDom.querySelectorAll('.carousel .list .item');
    let thumbnailItemsDom = document.querySelectorAll('.carousel .thumbnail .item');

    if (type === 'next') {
        currentIndex = (currentIndex + 1) % SliderItemsDom.length;
    } else {
        currentIndex = (currentIndex - 1 + SliderItemsDom.length) % SliderItemsDom.length;
    }

    SliderItemsDom.forEach((item, index) => {
        item.classList.toggle('visible', index === currentIndex);
    });

    thumbnailItemsDom.forEach((item, index) => {
        item.classList.toggle('visible', index === currentIndex);
    });
}

document.querySelectorAll('.details-btn').forEach(button => {
    button.addEventListener('click', () => {
        const modalTarget = button.getAttribute('data-modal-target');
        const modal = document.querySelector(modalTarget);
        const satelliteId = button.closest('.item').getAttribute('data-satellite-id');
        const detailsSection = document.querySelector(`.details-section[data-satellite-id="${satelliteId}"]`);
        const modalBody = modal.querySelector('.modal-body');

        if (modalTarget === '#launchModal') {
            modalBody.innerHTML = detailsSection.querySelector('.launch-details').innerHTML;
        } else if (modalTarget === '#orbitModal') {
            modalBody.innerHTML = detailsSection.querySelector('.orbit-details').innerHTML;
        } else if (modalTarget === '#observerModal') {
            modalBody.innerHTML = detailsSection.querySelector('.observer-details').innerHTML;
        } else if (modalTarget === '#coordinatesModal') {
            modalBody.innerHTML = detailsSection.querySelector('.observer-coordinates').innerHTML;
        }

        openModal(modal);
    });
});

const closeButtons = document.querySelectorAll('[data-close-button]');
const overlay = document.getElementById('overlay');

closeButtons.forEach(button => {
    button.addEventListener('click', () => {
        const modal = button.closest('.modal');
        closeModal(modal);
    });
});

function openModal(modal) {
    if (modal == null) return;
    modal.classList.add('active');
    overlay.classList.add('active');
}

function closeModal(modal) {
    if (modal == null) return;
    modal.classList.remove('active');
    overlay.classList.remove('active');
}

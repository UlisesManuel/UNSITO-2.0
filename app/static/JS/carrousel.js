document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide');

    if (slides.length <= 1) return;

    let actual = 0;

    setInterval(() => {

        slides[actual].classList.remove(
            'opacity-100',
            'pointer-events-auto',
            'z-10'
        );

        slides[actual].classList.add(
            'opacity-0',
            'pointer-events-none'
        );

        actual = (actual + 1) % slides.length;

        slides[actual].classList.remove(
            'opacity-0',
            'pointer-events-none'
        );

        slides[actual].classList.add(
            'opacity-100',
            'pointer-events-auto',
            'z-10'
        );

    }, 5000);
});
// ======================= JavaScript =======================
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const navbarLinks = document.getElementById('navbar-links');

    if (menuToggle && navbarLinks) {
        menuToggle.addEventListener('click', function() {
            // Toggles the 'active' class on the navbar links container
            navbarLinks.classList.toggle('active');
        });
    }
}); 
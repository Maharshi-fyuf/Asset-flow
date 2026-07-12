function navigateTo(viewId) {
    // Check if we are logging in
    if (viewId === 'view-dashboard') {
        document.getElementById('view-login').style.display = 'none';
        document.getElementById('view-login').classList.remove('active');
        document.getElementById('app-layout').style.display = 'flex';
    }

    // Hide all views
    const views = document.querySelectorAll('.view-container');
    views.forEach(view => {
        if (view.id !== 'view-login') {
            view.classList.remove('active');
        }
    });

    // Show target view
    const target = document.getElementById(viewId);
    if (target && viewId !== 'view-login') {
        target.classList.add('active');
    }

    // Update active state on sidebar
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.classList.remove('active');
    });

    // Find the corresponding nav item and set it active
    const targetNavItem = Array.from(navItems).find(item => item.getAttribute('onclick').includes(viewId));
    if (targetNavItem) {
        targetNavItem.classList.add('active');
    }
}
// Dashboard Active Metrics

function random(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function updateDashboard() {
    const cards = document.querySelectorAll(".card-value");

    if (cards.length >= 6) {
        cards[0].innerText = random(120, 140); // Available Assets
        cards[1].innerText = random(30, 45);   // Allocated
        cards[2].innerText = random(2, 10);    // Available Resources
        cards[3].innerText = random(1, 6);     // Active Bookings
        cards[4].innerText = random(0, 5);     // Pending Maintenance
        cards[5].innerText = random(5, 15);    // Upcoming Returns
    }
}
updateDashboard();
setInterval(updateDashboard, 5000);


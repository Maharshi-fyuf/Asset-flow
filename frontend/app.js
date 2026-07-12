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

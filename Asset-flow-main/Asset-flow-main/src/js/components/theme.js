// theme.js
const STORAGE_KEY = 'asset_flow_theme';

export function initializeTheme() {
  const savedTheme = localStorage.getItem(STORAGE_KEY) || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateToggleButtons(savedTheme);
  return savedTheme;
}

export function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem(STORAGE_KEY, newTheme);
  updateToggleButtons(newTheme);
  
  // Dispatch custom event for widgets (like charts) to adapt programmatically
  const event = new CustomEvent('theme-changed', { detail: newTheme });
  window.dispatchEvent(event);
  
  return newTheme;
}

function updateToggleButtons(theme) {
  const toggles = document.querySelectorAll('.theme-toggle');
  toggles.forEach(btn => {
    // Expecting button to have icons or text that adapts
    const icon = btn.querySelector('i');
    if (icon) {
      if (theme === 'dark') {
        icon.className = 'lucide-sun'; // Or feather icon style class name
        if (typeof lucide !== 'undefined') lucide.createIcons();
      } else {
        icon.className = 'lucide-moon';
        if (typeof lucide !== 'undefined') lucide.createIcons();
      }
    }
  });
}

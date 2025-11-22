(() => {
    'use strict'

    const getStoredTheme = () => localStorage.getItem('theme')
    const setStoredTheme = theme => localStorage.setItem('theme', theme)

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme()
        if (storedTheme) {
            return storedTheme
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }

    const setTheme = theme => {
        if (theme === 'auto') {
            document.documentElement.setAttribute('data-bs-theme', (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'))
        } else {
            document.documentElement.setAttribute('data-bs-theme', theme)
        }
    }

    // Initial setup
    setTheme(getPreferredTheme())

    // Button handler
    window.addEventListener('DOMContentLoaded', () => {
        const toggleButton = document.getElementById('theme-toggle');
        if (!toggleButton) return;

        const icon = toggleButton.querySelector('i');

        const updateIcon = (theme) => {
            if (theme === 'dark') {
                icon.classList.remove('bi-moon-stars-fill');
                icon.classList.add('bi-sun-fill');
            } else {
                icon.classList.remove('bi-sun-fill');
                icon.classList.add('bi-moon-stars-fill');
            }
        };

        // Set initial icon
        updateIcon(getPreferredTheme());

        toggleButton.addEventListener('click', () => {
            const current = getStoredTheme() || getPreferredTheme();
            const next = current === 'dark' ? 'light' : 'dark';
            setStoredTheme(next);
            setTheme(next);
            updateIcon(next);
        });
    });
})()
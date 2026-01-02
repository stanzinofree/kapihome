// Theme Toggle System
(function() {
    'use strict';
    
    const STORAGE_KEY = 'theme-preference';
    
    // Get theme preference
    const getThemePreference = () => {
        if (localStorage.getItem(STORAGE_KEY)) {
            return localStorage.getItem(STORAGE_KEY);
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    };
    
    // Set theme
    const setTheme = (theme) => {
        const root = document.documentElement;
        
        if (theme === 'dark') {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }
        
        localStorage.setItem(STORAGE_KEY, theme);
        
        // Update toggle button if it exists
        updateToggleButton(theme);
    };
    
    // Update toggle button appearance
    const updateToggleButton = (theme) => {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
            toggleBtn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
        }
    };
    
    // Toggle theme
    const toggleTheme = () => {
        const current = getThemePreference();
        const next = current === 'dark' ? 'light' : 'dark';
        setTheme(next);
    };
    
    // Initialize theme on page load
    const initTheme = () => {
        const theme = getThemePreference();
        setTheme(theme);
    };
    
    // Create toggle button
    const createToggleButton = () => {
        const existingBtn = document.getElementById('theme-toggle');
        if (existingBtn) return; // Button already exists
        
        const btn = document.createElement('button');
        btn.id = 'theme-toggle';
        btn.className = 'theme-toggle-btn';
        btn.setAttribute('aria-label', 'Toggle theme');
        btn.onclick = toggleTheme;
        
        // Insert in nav-external section
        const navExternal = document.querySelector('.nav-external');
        if (navExternal) {
            navExternal.appendChild(btn);
        } else {
            // Fallback: append to header
            const header = document.querySelector('.header .nav-container');
            if (header) {
                header.appendChild(btn);
            }
        }
        
        updateToggleButton(getThemePreference());
    };
    
    // Init on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initTheme();
            createToggleButton();
        });
    } else {
        initTheme();
        createToggleButton();
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem(STORAGE_KEY)) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
    
    // Expose toggle function globally
    window.toggleTheme = toggleTheme;
})();

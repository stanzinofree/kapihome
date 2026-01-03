// ==UserScript==
// @name         Udemy Main Stats Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Extract main weekly stats from Udemy for KapiHome
// @author       Alessandro Middei
// @match        https://www.udemy.com/home/my-courses/*
// @icon         https://www.udemy.com/staticx/udemy/images/v7/logo-udemy.svg
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function createExportButton() {
        const btn = document.createElement('button');
        btn.innerHTML = '💾 Export Weekly Stats';
        btn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            padding: 12px 20px;
            background: #5cb85c;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(92, 184, 92, 0.4);
            font-size: 14px;
        `;
        btn.addEventListener('click', extractStats);
        document.body.appendChild(btn);
    }

    function extractStats() {
        const bodyText = document.body.innerText;
        
        const minutesMatch = bodyText.match(/(\d+)\/(\d+)\s+minuti\s+di\s+corso/i);
        const visitsMatch = bodyText.match(/(\d+)\/(\d+)\s+visita/i);
        const streakMatch = bodyText.match(/(\d+)\s+settimane?/i);
        const paginationMatch = bodyText.match(/(\d+)-\d+\s+di\s+(\d+)\s+corsi/i);
        
        const data = {
            type: 'weekly-stats',
            stats: {
                weekly_minutes_current: minutesMatch ? parseInt(minutesMatch[1]) : 0,
                weekly_minutes_goal: minutesMatch ? parseInt(minutesMatch[2]) : 30,
                visits_this_week: visitsMatch ? parseInt(visitsMatch[1]) : 0,
                visits_last_week: visitsMatch ? parseInt(visitsMatch[2]) : 0,
                weekly_streak: streakMatch ? parseInt(streakMatch[1]) : 0,
                total_courses: paginationMatch ? parseInt(paginationMatch[2]) : 0
            },
            extracted_at: new Date().toISOString()
        };
        
        console.log('Extracted stats:', data);
        
        // Download JSON
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'udemy-stats.json';
        a.click();
        URL.revokeObjectURL(url);
        
        alert(`✅ Exported weekly stats!\n\n` +
              `Total courses: ${data.stats.total_courses}\n` +
              `Weekly minutes: ${data.stats.weekly_minutes_current}/${data.stats.weekly_minutes_goal}\n` +
              `Visits: ${data.stats.visits_this_week}/${data.stats.visits_last_week}\n` +
              `Streak: ${data.stats.weekly_streak} settimane\n\n` +
              `File: udemy-stats.json`);
    }

    // Initialize after page load
    setTimeout(createExportButton, 3000);
})();

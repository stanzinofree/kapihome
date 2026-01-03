// ==UserScript==
// @name         Udemy Student Stats Extractor
// @namespace    http://tampermonkey.net/
// @version      2.0.0
// @description  Extract Udemy student learning statistics for KapiHome
// @author       Alessandro Middei
// @match        https://www.udemy.com/home/my-courses/*
// @match        https://www.udemy.com/home/my-courses/learning/*
// @icon         https://www.udemy.com/staticx/udemy/images/v7/logo-udemy.svg
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_deleteValue
// ==/UserScript==

(function() {
    'use strict';

    const STORAGE_KEY = 'udemy_extraction_data';

    // Detect current page type
    function getCurrentPageType() {
        const url = window.location.href;
        if (url.includes('progress_filter=in-progress')) return 'in-progress';
        if (url.includes('progress_filter=not-started')) return 'not-started';
        return 'main';
    }

    // Extract courses from current page
    function extractCoursesFromCurrentPage() {
        const courses = [];
        const courseCards = document.querySelectorAll('[data-purpose="enrolled-course-card"]');
        
        console.log(`Found ${courseCards.length} course cards on page`);
        
        courseCards.forEach(card => {
            const titleEl = card.querySelector('h3') || card.querySelector('[data-purpose="course-title"]');
            const title = titleEl?.textContent.trim() || 'Unknown Course';
            
            const cardText = card.textContent;
            const percentMatch = cardText.match(/(\d+)%\s+completato/i);
            const isNotStarted = cardText.includes('INIZIA IL CORSO');
            
            let progress = 0;
            if (percentMatch) {
                progress = parseInt(percentMatch[1]);
            } else if (isNotStarted) {
                progress = 0;
            }
            
            const imageEl = card.querySelector('img');
            const linkEl = card.querySelector('a[href*="/course/"]');
            
            courses.push({
                title: title,
                progress: progress,
                image: imageEl?.src || '',
                url: linkEl?.href || window.location.origin + (linkEl?.getAttribute('href') || '')
            });
        });
        
        return courses;
    }

    // Extract weekly stats from main page
    function extractWeeklyStats() {
        const bodyText = document.body.textContent;
        
        const minutesMatch = bodyText.match(/(\d+)\/(\d+)\s+minuti\s+di\s+corso/i);
        const visitsMatch = bodyText.match(/(\d+)\/(\d+)\s+visita/i);
        const streakMatch = bodyText.match(/(\d+)\s+settimane?/i);
        const paginationMatch = bodyText.match(/(\d+)-\d+\s+di\s+(\d+)\s+corsi/i);
        
        return {
            currentMinutes: minutesMatch ? parseInt(minutesMatch[1]) : 0,
            goalMinutes: minutesMatch ? parseInt(minutesMatch[2]) : 30,
            visitsThisWeek: visitsMatch ? parseInt(visitsMatch[1]) : 0,
            visitsLastWeek: visitsMatch ? parseInt(visitsMatch[2]) : 0,
            weeklyStreak: streakMatch ? parseInt(streakMatch[1]) : 0,
            totalEnrolled: paginationMatch ? parseInt(paginationMatch[2]) : 0
        };
    }

    // Create navigation buttons
    function createNavigationUI() {
        const pageType = getCurrentPageType();
        const data = GM_getValue(STORAGE_KEY, null);
        
        const container = document.createElement('div');
        container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            background: white;
            border: 2px solid #A435F0;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(164, 53, 240, 0.3);
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            max-width: 300px;
        `;
        
        const title = document.createElement('div');
        title.textContent = '📚 Udemy Data Extractor';
        title.style.cssText = 'font-weight: bold; margin-bottom: 10px; color: #A435F0;';
        container.appendChild(title);
        
        const status = document.createElement('div');
        status.style.cssText = 'font-size: 12px; margin-bottom: 10px; color: #666;';
        
        if (pageType === 'main') {
            const courses = extractCoursesFromCurrentPage();
            const stats = extractWeeklyStats();
            
            status.innerHTML = `
                Step 1/3: Main page ✅<br>
                Total courses: ${stats.totalEnrolled}<br>
                Weekly: ${stats.currentMinutes}/${stats.goalMinutes} min
            `;
            
            const btnInProgress = document.createElement('button');
            btnInProgress.textContent = '→ Go to In-Progress';
            btnInProgress.style.cssText = `
                width: 100%;
                padding: 10px;
                background: #A435F0;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                margin-bottom: 8px;
            `;
            btnInProgress.onclick = () => {
                GM_setValue(STORAGE_KEY, { 
                    stats: stats,
                    mainPageCourses: courses
                });
                window.location.href = 'https://www.udemy.com/home/my-courses/learning/?progress_filter=in-progress';
            };
            
            container.appendChild(status);
            container.appendChild(btnInProgress);
            
        } else if (pageType === 'in-progress') {
            const courses = extractCoursesFromCurrentPage();
            
            status.innerHTML = `
                Step 2/3: In-Progress ✅<br>
                Found: ${courses.length} courses
            `;
            
            const btnNotStarted = document.createElement('button');
            btnNotStarted.textContent = '→ Go to Not-Started';
            btnNotStarted.style.cssText = `
                width: 100%;
                padding: 10px;
                background: #A435F0;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
            `;
            btnNotStarted.onclick = () => {
                const savedData = GM_getValue(STORAGE_KEY, {});
                savedData.inProgressCourses = courses;
                GM_setValue(STORAGE_KEY, savedData);
                window.location.href = 'https://www.udemy.com/home/my-courses/learning/?progress_filter=not-started';
            };
            
            container.appendChild(status);
            container.appendChild(btnNotStarted);
            
        } else if (pageType === 'not-started') {
            const courses = extractCoursesFromCurrentPage();
            
            status.innerHTML = `
                Step 3/3: Not-Started ✅<br>
                Found: ${courses.length} courses
            `;
            
            const btnExport = document.createElement('button');
            btnExport.textContent = '💾 Export Data';
            btnExport.style.cssText = `
                width: 100%;
                padding: 10px;
                background: #5cb85c;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
            `;
            btnExport.onclick = () => {
                const savedData = GM_getValue(STORAGE_KEY, {});
                savedData.notStartedCourses = courses;
                exportData(savedData);
            };
            
            container.appendChild(status);
            container.appendChild(btnExport);
        }
        
        document.body.appendChild(container);
    }

    function exportData(savedData) {
        const stats = savedData.stats || {};
        const inProgressCourses = savedData.inProgressCourses || [];
        const notStartedCourses = savedData.notStartedCourses || [];
        
        // Separate completed and in-progress
        const completedCourses = inProgressCourses.filter(c => c.progress >= 100);
        const actualInProgress = inProgressCourses.filter(c => c.progress > 0 && c.progress < 100);
        
        const totalCourses = stats.totalEnrolled || (completedCourses.length + actualInProgress.length + notStartedCourses.length);
        
        const data = {
            student: {
                total_courses: totalCourses,
                completed_courses: completedCourses.length,
                in_progress_courses: actualInProgress.length,
                weekly_minutes_current: stats.currentMinutes || 0,
                weekly_minutes_goal: stats.goalMinutes || 30,
                visits_this_week: stats.visitsThisWeek || 0,
                visits_last_week: stats.visitsLastWeek || 0,
                weekly_streak: stats.weeklyStreak || 0
            },
            stats: {
                total_enrolled: totalCourses,
                completed: completedCourses.length,
                in_progress: actualInProgress.length,
                completion_rate: totalCourses > 0 ? Math.round((completedCourses.length / totalCourses) * 100) : 0,
                weekly_minutes: `${stats.currentMinutes || 0}/${stats.goalMinutes || 30}`,
                weekly_visits: `${stats.visitsThisWeek || 0}/${stats.visitsLastWeek || 0}`,
                streak_weeks: stats.weeklyStreak || 0
            },
            completed_courses: completedCourses.slice(0, 20),
            in_progress_courses: actualInProgress.slice(0, 20),
            not_started_courses: notStartedCourses.slice(0, 20),
            last_updated: new Date().toISOString()
        };
        
        console.log('Exported data:', data);
        
        // Download JSON
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'udemy.json';
        a.click();
        URL.revokeObjectURL(url);
        
        // Clear storage
        GM_deleteValue(STORAGE_KEY);
        
        alert('✅ Udemy student data extracted successfully!\n\n' +
              `Total Courses: ${totalCourses}\n` +
              `Completed: ${completedCourses.length}\n` +
              `In Progress: ${actualInProgress.length}\n` +
              `Not Started: ${notStartedCourses.length}\n\n` +
              `Weekly Minutes: ${stats.currentMinutes}/${stats.goalMinutes}\n` +
              `Weekly Visits: ${stats.visitsThisWeek}/${stats.visitsLastWeek}\n` +
              `Weekly Streak: ${stats.weeklyStreak} settimane\n\n` +
              'File downloaded: udemy.json\n\n' +
              'You can now go back to My Courses main page.');
    }

    // Initialize after page load
    setTimeout(createNavigationUI, 2000);
})();

// ==UserScript==
// @name         Udemy Student Stats Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Extract Udemy student learning statistics for KapiHome
// @author       Alessandro Middei
// @match        https://www.udemy.com/home/my-courses/*
// @match        https://www.udemy.com/home/learning/*
// @icon         https://www.udemy.com/staticx/udemy/images/v7/logo-udemy.svg
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Create export button
    function createExportButton() {
        const btn = document.createElement('button');
        btn.innerHTML = '💾 Export Student Stats';
        btn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            padding: 12px 20px;
            background: #A435F0;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(164, 53, 240, 0.4);
            font-size: 14px;
        `;
        btn.addEventListener('click', extractUdemyStudentData);
        document.body.appendChild(btn);
    }

    async function extractUdemyStudentData() {
        try {
            console.log('Starting Udemy student data extraction...');
            
            // Extract weekly goal stats from dashboard
            const weeklyMinutesText = document.body.textContent;
            
            // Extract "0/30 minuti di corso"
            const minutesMatch = weeklyMinutesText.match(/(\d+)\/(\d+)\s+minuti\s+di\s+corso/i);
            const currentMinutes = minutesMatch ? parseInt(minutesMatch[1]) : 0;
            const goalMinutes = minutesMatch ? parseInt(minutesMatch[2]) : 30;
            
            // Extract "4/1 visita" (this week / last week)
            const visitsMatch = weeklyMinutesText.match(/(\d+)\/(\d+)\s+visita/i);
            const visitsThisWeek = visitsMatch ? parseInt(visitsMatch[1]) : 0;
            const visitsLastWeek = visitsMatch ? parseInt(visitsMatch[2]) : 0;
            
            // Extract "0 settimane" (consecutive weeks streak)
            const streakMatch = weeklyMinutesText.match(/(\d+)\s+settimane?/i);
            const weeklyStreak = streakMatch ? parseInt(streakMatch[1]) : 0;
            
            // Extract total courses from pagination "1-12 di 341 corsi"
            const paginationMatch = weeklyMinutesText.match(/\d+-\d+\s+di\s+(\d+)\s+corsi/i);
            const totalEnrolled = paginationMatch ? parseInt(paginationMatch[1]) : 0;
            
            // Extract completed courses
            const completedCourses = [];
            const inProgressCourses = [];
            
            // Parse each course card
            document.querySelectorAll('[data-purpose="course-card"], .my-courses__course-card').forEach((card, index) => {
                if (index >= 20) return; // Limit to 20 courses
                
                const titleEl = card.querySelector('[data-purpose="course-title"], h3, .course-card--course-title--');
                const progressEl = card.querySelector('[data-purpose="progress-bar"], .progress-bar');
                const progressText = progressEl?.getAttribute('aria-valuenow') || progressEl?.style?.width || '0';
                const progress = parseInt(progressText.replace('%', '')) || 0;
                
                const imageEl = card.querySelector('img');
                const linkEl = card.querySelector('a[href*="/course/"]');
                
                const courseData = {
                    title: titleEl?.textContent.trim() || 'Unknown Course',
                    progress: progress,
                    image: imageEl?.src || '',
                    url: linkEl?.href || ''
                };
                
                if (progress >= 100) {
                    completedCourses.push(courseData);
                } else if (progress > 0) {
                    inProgressCourses.push(courseData);
                }
            });
            
            // Calculate weekly learning estimate (you can manually adjust this)
            const coursesViewedWeekly = Math.min(inProgressCourses.length, 5); // Estimate
            
            // Extract learning stats from dashboard if available
            let totalMinutesLearned = 0;
            let learningStreak = 0;
            
            const statsCards = document.querySelectorAll('[data-purpose="learning-time"], .learning-stats');
            statsCards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes('minutes') || text.includes('hours')) {
                    const match = text.match(/(\d+)/);
                    if (match) {
                        totalMinutesLearned = parseInt(match[1]);
                    }
                }
            });
            
            // Build final data structure
            const data = {
                student: {
                    total_courses: totalEnrolled,
                    completed_courses: completedCourses.length,
                    in_progress_courses: inProgressCourses.length,
                    weekly_minutes_current: currentMinutes,
                    weekly_minutes_goal: goalMinutes,
                    visits_this_week: visitsThisWeek,
                    visits_last_week: visitsLastWeek,
                    weekly_streak: weeklyStreak
                },
                stats: {
                    total_enrolled: totalEnrolled,
                    completed: completedCourses.length,
                    in_progress: inProgressCourses.length,
                    completion_rate: totalEnrolled > 0 ? Math.round((completedCourses.length / totalEnrolled) * 100) : 0,
                    weekly_minutes: `${currentMinutes}/${goalMinutes}`,
                    weekly_visits: `${visitsThisWeek}/${visitsLastWeek}`,
                    streak_weeks: weeklyStreak
                },
                completed_courses: completedCourses.slice(0, 10),
                in_progress_courses: inProgressCourses.slice(0, 10),
                last_updated: new Date().toISOString()
            };
            
            console.log('Extracted data:', data);
            
            // Download as JSON
            downloadJSON(data, 'udemy.json');
            
            alert('✅ Udemy student data extracted successfully!\n\n' +
                  `Total Courses: ${totalEnrolled}\n` +
                  `Weekly Minutes: ${currentMinutes}/${goalMinutes}\n` +
                  `Weekly Visits: ${visitsThisWeek}/${visitsLastWeek}\n` +
                  `Weekly Streak: ${weeklyStreak} settimane\n` +
                  `Completed: ${completedCourses.length}\n` +
                  `In Progress: ${inProgressCourses.length}\n\n` +
                  'File downloaded: udemy.json');
            
        } catch (error) {
            console.error('Error extracting Udemy student data:', error);
            alert('❌ Error extracting data. Check console for details.\n\n' +
                  'Make sure you are on:\n' +
                  '- My Courses page (https://www.udemy.com/home/my-courses/)\n' +
                  '- Learning Dashboard');
        }
    }

    function downloadJSON(data, filename) {
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    // Initialize
    setTimeout(createExportButton, 2000);
})();

// ==UserScript==
// @name         Udemy In-Progress Courses Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Extract in-progress courses from Udemy for KapiHome
// @author       Alessandro Middei
// @match        https://www.udemy.com/home/my-courses/learning/?progress_filter=in-progress*
// @icon         https://www.udemy.com/staticx/udemy/images/v7/logo-udemy.svg
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function createExportButton() {
        const btn = document.createElement('button');
        btn.innerHTML = '💾 Export In-Progress Courses';
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
        btn.addEventListener('click', extractCourses);
        document.body.appendChild(btn);
    }

    function extractCourses() {
        const courses = [];
        
        // Try different selectors for course cards
        let courseCards = document.querySelectorAll('[data-purpose="enrolled-course-card"]');
        if (courseCards.length === 0) {
            courseCards = document.querySelectorAll('.my-courses--course-card--2YAuJ');
        }
        if (courseCards.length === 0) {
            courseCards = document.querySelectorAll('[class*="course-card"]');
        }
        
        console.log('Found course cards:', courseCards.length);
        
        if (courseCards.length > 0) {
            courseCards.forEach((card, index) => {
                // Try multiple selectors for title
                let titleEl = card.querySelector('[data-purpose="course-title-url"]');
                if (!titleEl) titleEl = card.querySelector('h3');
                if (!titleEl) titleEl = card.querySelector('[class*="course-title"]');
                
                // Try multiple selectors for instructor
                let instructorEl = card.querySelector('[data-purpose="safely-set-inner-html:course-card:visible-instructors"]');
                if (!instructorEl) instructorEl = card.querySelector('[class*="instructor"]');
                
                // Try multiple selectors for progress
                let progressEl = card.querySelector('[data-purpose="course-card-progress"]');
                if (!progressEl) progressEl = card.querySelector('[aria-label*="completato"]');
                if (!progressEl) progressEl = card.querySelector('[class*="progress"]');
                
                if (titleEl) {
                    let title = titleEl.textContent.trim();
                    let instructor = instructorEl ? instructorEl.textContent.trim() : '';
                    
                    // Clean up instructor (remove "Insegnante:" prefix if present)
                    instructor = instructor.replace(/^Insegnante:\s*/i, '').trim();
                    
                    let progress = 0;
                    if (progressEl) {
                        const progressText = progressEl.getAttribute('aria-label') || progressEl.textContent;
                        const match = progressText.match(/(\d+)%/);
                        if (match) progress = parseInt(match[1]);
                    }
                    
                    // Validate: don't add if instructor looks like a progress text
                    if (instructor.includes('%') || instructor.toLowerCase().includes('completato')) {
                        instructor = '';
                    }
                    
                    if (title && progress > 0 && progress < 100) {
                        courses.push({
                            title: title,
                            instructor: instructor,
                            progress: progress,
                            order: index
                        });
                        console.log(`Course ${index}:`, {title, instructor, progress});
                    }
                }
            });
        } else {
            // Fallback: parse from text
            const allText = document.body.innerText;
            const lines = allText.split('\n');
            
            let currentCourse = null;
            let currentInstructor = null;
            
            lines.forEach((line, index) => {
                // Look for course titles
                if (line.length > 20 && line.length < 200 && !line.includes('%') && !line.includes('completato')) {
                    currentCourse = line.trim();
                    // Next line might be instructor
                    if (index + 1 < lines.length) {
                        const nextLine = lines[index + 1].trim();
                        if (nextLine.length > 5 && nextLine.length < 100) {
                            currentInstructor = nextLine;
                        }
                    }
                }
                
                // Look for progress percentage
                const progressMatch = line.match(/(\d+)%\s*completato/i);
                if (progressMatch && currentCourse) {
                    const progress = parseInt(progressMatch[1]);
                    if (progress > 0 && progress < 100) {
                        courses.push({
                            title: currentCourse,
                            instructor: currentInstructor || '',
                            progress: progress,
                            order: courses.length
                        });
                        currentCourse = null;
                        currentInstructor = null;
                    }
                }
            });
        }
        
        console.log('Extracted courses:', courses);
        
        const data = {
            type: 'in-progress',
            courses: courses, // Keep original order (most recent first)
            count: courses.length,
            extracted_at: new Date().toISOString()
        };
        
        // Download JSON
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'udemy-in-progress.json';
        a.click();
        URL.revokeObjectURL(url);
        
        alert(`✅ Exported ${courses.length} in-progress courses!\n\nFile: udemy-in-progress.json\n\nNote: Courses are ordered by most recent access`);
    }

    // Initialize after page load
    setTimeout(createExportButton, 3000);
})();

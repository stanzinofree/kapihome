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
        
        // Get all course titles and check their progress
        const allText = document.body.innerText;
        const lines = allText.split('\n');
        
        let currentCourse = null;
        
        lines.forEach((line, index) => {
            // Look for course titles (usually longer text before progress)
            if (line.length > 20 && line.length < 200 && !line.includes('%') && !line.includes('completato')) {
                currentCourse = line.trim();
            }
            
            // Look for progress percentage
            const progressMatch = line.match(/(\d+)%\s*completato/i);
            if (progressMatch && currentCourse) {
                const progress = parseInt(progressMatch[1]);
                if (progress > 0 && progress < 100) {
                    courses.push({
                        title: currentCourse,
                        progress: progress
                    });
                    currentCourse = null;
                }
            }
        });
        
        // Remove duplicates
        const uniqueCourses = courses.filter((course, index, self) =>
            index === self.findIndex(c => c.title === course.title)
        );
        
        console.log('Extracted courses:', uniqueCourses);
        
        const data = {
            type: 'in-progress',
            courses: uniqueCourses,
            count: uniqueCourses.length,
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
        
        alert(`✅ Exported ${uniqueCourses.length} in-progress courses!\n\nFile: udemy-in-progress.json`);
    }

    // Initialize after page load
    setTimeout(createExportButton, 3000);
})();

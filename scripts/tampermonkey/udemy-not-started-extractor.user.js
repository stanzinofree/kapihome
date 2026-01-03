// ==UserScript==
// @name         Udemy Not-Started Courses Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Extract not-started courses from Udemy for KapiHome
// @author       Alessandro Middei
// @match        https://www.udemy.com/home/my-courses/learning/?progress_filter=not-started*
// @icon         https://www.udemy.com/staticx/udemy/images/v7/logo-udemy.svg
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    function createExportButton() {
        const btn = document.createElement('button');
        btn.innerHTML = '💾 Export Not-Started Courses';
        btn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            padding: 12px 20px;
            background: #EC5252;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(236, 82, 82, 0.4);
            font-size: 14px;
        `;
        btn.addEventListener('click', extractCourses);
        document.body.appendChild(btn);
    }

    function extractCourses() {
        const courses = [];
        
        // Get all text and look for course titles near "INIZIA IL CORSO"
        const allText = document.body.innerText;
        const lines = allText.split('\n');
        
        let currentCourse = null;
        
        lines.forEach((line, index) => {
            // Look for course titles
            if (line.length > 20 && line.length < 200 && !line.includes('INIZIA')) {
                currentCourse = line.trim();
            }
            
            // Look for "INIZIA IL CORSO" indicator
            if (line.includes('INIZIA IL CORSO') && currentCourse) {
                courses.push({
                    title: currentCourse,
                    progress: 0
                });
                currentCourse = null;
            }
        });
        
        // Remove duplicates
        const uniqueCourses = courses.filter((course, index, self) =>
            index === self.findIndex(c => c.title === course.title)
        );
        
        console.log('Extracted courses:', uniqueCourses);
        
        const data = {
            type: 'not-started',
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
        a.download = 'udemy-not-started.json';
        a.click();
        URL.revokeObjectURL(url);
        
        alert(`✅ Exported ${uniqueCourses.length} not-started courses!\n\nFile: udemy-not-started.json`);
    }

    // Initialize after page load
    setTimeout(createExportButton, 3000);
})();

// ==UserScript==
// @name         Udemy Instructor Stats Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Extract Udemy instructor statistics and courses for KapiHome
// @author       Alessandro Middei
// @match        https://www.udemy.com/instructor/performance/*
// @match        https://www.udemy.com/instructor/courses/*
// @icon         https://www.udemy.com/staticx/udemy/images/v7/logo-udemy.svg
// @grant        GM_xmlhttpRequest
// @connect      udemy.com
// ==/UserScript==

(function() {
    'use strict';

    // Create export button
    function createExportButton() {
        const btn = document.createElement('button');
        btn.innerHTML = '💾 Export Udemy Stats';
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
        btn.addEventListener('click', extractUdemyData);
        document.body.appendChild(btn);
    }

    async function extractUdemyData() {
        try {
            console.log('Starting Udemy data extraction...');
            
            // Extract instructor profile data from page
            const instructorName = document.querySelector('[data-purpose="instructor-name"]')?.textContent.trim() || 
                                  document.querySelector('.instructor-profile--instructor-name--')?.textContent.trim() ||
                                  'Unknown Instructor';
            
            // Extract stats from performance dashboard if available
            const stats = {
                total_students: 0,
                total_reviews: 0,
                total_courses: 0,
                average_rating: 0,
                total_revenue: 0,
                monthly_earnings: 0
            };
            
            // Try to extract stats from dashboard cards
            const statCards = document.querySelectorAll('[data-purpose="metric-stat"]');
            statCards.forEach(card => {
                const label = card.querySelector('[data-purpose="metric-label"]')?.textContent.toLowerCase() || '';
                const value = card.querySelector('[data-purpose="metric-value"]')?.textContent.trim() || '0';
                
                if (label.includes('student')) {
                    stats.total_students = parseInt(value.replace(/,/g, '')) || 0;
                } else if (label.includes('review')) {
                    stats.total_reviews = parseInt(value.replace(/,/g, '')) || 0;
                } else if (label.includes('course')) {
                    stats.total_courses = parseInt(value.replace(/,/g, '')) || 0;
                } else if (label.includes('rating')) {
                    stats.average_rating = parseFloat(value) || 0;
                }
            });
            
            // Alternative: extract from page text
            if (stats.total_students === 0) {
                const bodyText = document.body.textContent;
                const studentsMatch = bodyText.match(/(\d+(?:,\d+)*)\s+(?:total\s+)?students?/i);
                if (studentsMatch) {
                    stats.total_students = parseInt(studentsMatch[1].replace(/,/g, '')) || 0;
                }
            }
            
            // Extract courses list
            const courses = [];
            const courseCards = document.querySelectorAll('[data-purpose="course-card"], .course-card, .popper-module--popper-');
            
            courseCards.forEach((card, index) => {
                if (index >= 10) return; // Limit to 10 courses
                
                const titleEl = card.querySelector('[data-purpose="course-title"], .course-card--course-title--');
                const studentsEl = card.querySelector('[data-purpose="enrollment-count"]');
                const ratingEl = card.querySelector('[data-purpose="rating-number"]');
                const reviewsEl = card.querySelector('[data-purpose="reviews-count"]');
                const priceEl = card.querySelector('[data-purpose="price"]');
                const imageEl = card.querySelector('img[alt*="course"]');
                
                if (titleEl) {
                    courses.push({
                        title: titleEl.textContent.trim(),
                        students: studentsEl ? parseInt(studentsEl.textContent.replace(/[^\d]/g, '')) || 0 : 0,
                        rating: ratingEl ? parseFloat(ratingEl.textContent) || 0 : 0,
                        reviews: reviewsEl ? parseInt(reviewsEl.textContent.replace(/[^\d]/g, '')) || 0 : 0,
                        price: priceEl ? priceEl.textContent.trim() : 'N/A',
                        image: imageEl ? imageEl.src : '',
                        url: card.querySelector('a')?.href || ''
                    });
                }
            });
            
            // If no courses found via cards, try alternative method
            if (courses.length === 0) {
                console.log('No courses found via cards, trying alternative extraction...');
                // This would need manual data entry or API integration
                console.log('Please ensure you are on the Instructor Dashboard > Courses page');
            }
            
            // Build final data structure
            const data = {
                instructor: {
                    name: instructorName,
                    total_students: stats.total_students,
                    total_courses: stats.total_courses,
                    total_reviews: stats.total_reviews,
                    average_rating: stats.average_rating
                },
                stats: {
                    total_students: stats.total_students,
                    total_courses: stats.total_courses,
                    total_reviews: stats.total_reviews,
                    average_rating: stats.average_rating,
                    total_revenue: stats.total_revenue,
                    monthly_earnings: stats.monthly_earnings
                },
                courses: courses,
                last_updated: new Date().toISOString()
            };
            
            console.log('Extracted data:', data);
            
            // Download as JSON
            downloadJSON(data, 'udemy.json');
            
            alert('✅ Udemy data extracted successfully!\n\n' +
                  `Instructor: ${instructorName}\n` +
                  `Total Students: ${stats.total_students.toLocaleString()}\n` +
                  `Total Courses: ${stats.total_courses}\n` +
                  `Courses Extracted: ${courses.length}\n\n` +
                  'File downloaded: udemy.json');
            
        } catch (error) {
            console.error('Error extracting Udemy data:', error);
            alert('❌ Error extracting data. Check console for details.\n\n' +
                  'Make sure you are on:\n' +
                  '- Instructor Dashboard > Performance, or\n' +
                  '- Instructor Dashboard > Courses');
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

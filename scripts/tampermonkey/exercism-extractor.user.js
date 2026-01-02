// ==UserScript==
// @name         Exercism Stats & Badges Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Extract Exercism profile stats, badges, and solutions
// @author       Alessandro Middei
// @match        https://exercism.org/profiles/*
// @icon         https://exercism.org/favicon.ico
// @grant        none
// ==/UserScript==

(function() {
    "use strict";

    const createButton = () => {
        const btn = document.createElement("button");
        btn.textContent = "📊 Extract Exercism Data";
        btn.style.cssText = "position:fixed;bottom:30px;right:30px;z-index:9999;padding:12px 20px;background:#6200ee;color:#fff;border:none;border-radius:8px;font-weight:bold;cursor:pointer;box-shadow:0 4px 8px rgba(0,0,0,0.3);";
        btn.onclick = extractData;
        document.body.appendChild(btn);
    };

    const extractData = async () => {
        const username = window.location.pathname.split('/')[2];
        
        const data = {
            profile: {},
            stats: {},
            badges: [],
            recent_solutions: [],
            tracks: [],
            extracted_at: new Date().toISOString()
        };

        try {
            // Extract profile info from main page
            const reputationEl = document.querySelector('[data-tooltip*="Reputation"]') || 
                                document.querySelector('div[class*="reputation"]');
            if (reputationEl) {
                const repMatch = reputationEl.textContent.match(/\d+/);
                data.stats.reputation = repMatch ? parseInt(repMatch[0]) : 0;
            }

            // Extract location and joined date
            const locationEl = Array.from(document.querySelectorAll('div')).find(el => 
                el.textContent.includes('Rome') || el.textContent.includes('Italy')
            );
            if (locationEl) {
                data.profile.location = locationEl.textContent.trim();
            }

            // Extract badge count from main page
            const badgeCountEl = Array.from(document.querySelectorAll('*')).find(el => 
                el.textContent.match(/\d+\s+badge/)
            );
            if (badgeCountEl) {
                const countMatch = badgeCountEl.textContent.match(/(\d+)\s+badge/);
                data.stats.total_badges = countMatch ? parseInt(countMatch[1]) : 0;
            }

            // Try to extract badges from current page
            const badgeElements = document.querySelectorAll('img[src*="badge"], img[src*="hello-world"], img[src*="editor"], img[src*="logo"], img[src*="v1"], img[src*="v2"]');
            const badgeNames = new Set();
            
            badgeElements.forEach(img => {
                const src = img.src;
                const alt = img.alt || '';
                
                // Extract badge name from alt text or src
                let badgeName = '';
                if (alt.includes('Badge:')) {
                    badgeName = alt.replace('Badge:', '').trim();
                } else if (src.includes('hello-world')) {
                    badgeName = 'Anybody there?';
                } else if (src.includes('editor')) {
                    badgeName = 'Rookie';
                } else if (src.includes('logo')) {
                    badgeName = 'Member';
                } else if (src.includes('v1')) {
                    badgeName = 'v1';
                } else if (src.includes('v2')) {
                    badgeName = 'v2';
                }
                
                if (badgeName && !badgeNames.has(badgeName)) {
                    badgeNames.add(badgeName);
                    
                    // Determine rarity from class or nearby text
                    let rarity = 'common';
                    const parent = img.closest('div');
                    if (parent) {
                        const parentText = parent.textContent.toLowerCase();
                        if (parentText.includes('rare')) rarity = 'rare';
                        if (parentText.includes('ultimate')) rarity = 'ultimate';
                        if (parentText.includes('legendary')) rarity = 'legendary';
                    }
                    
                    data.badges.push({
                        name: badgeName,
                        rarity: rarity,
                        icon_url: src
                    });
                }
            });

            // Fetch solutions from API
            try {
                const apiUrl = `https://exercism.org/api/v2/profiles/${username}/solutions`;
                const response = await fetch(apiUrl);
                const apiData = await response.json();
                
                if (apiData.results) {
                    data.stats.total_solutions = apiData.meta?.total || apiData.results.length;
                    
                    // Extract recent solutions (max 5)
                    data.recent_solutions = apiData.results.slice(0, 5).map(sol => ({
                        exercise: sol.exercise?.title || 'Unknown',
                        track: sol.track?.title || 'Unknown',
                        track_icon: sol.track?.icon_url || '',
                        status: sol.iteration_status || 'published',
                        published_at: sol.published_at ? sol.published_at.split('T')[0] : '',
                        num_stars: sol.num_stars || 0,
                        num_comments: sol.num_comments || 0,
                        url: sol.links?.public_url || ''
                    }));
                    
                    // Extract unique tracks
                    const tracksMap = new Map();
                    apiData.results.forEach(sol => {
                        const trackTitle = sol.track?.title;
                        if (trackTitle && !tracksMap.has(trackTitle)) {
                            tracksMap.set(trackTitle, {
                                name: trackTitle,
                                icon_url: sol.track?.icon_url || '',
                                exercises_completed: 1
                            });
                        } else if (trackTitle) {
                            tracksMap.get(trackTitle).exercises_completed++;
                        }
                    });
                    
                    data.tracks = Array.from(tracksMap.values());
                    data.stats.total_tracks = data.tracks.length;
                }
            } catch (apiError) {
                console.warn('API fetch failed:', apiError);
            }

            // Calculate badge stats
            data.stats.badges_by_rarity = {
                common: data.badges.filter(b => b.rarity === 'common').length,
                rare: data.badges.filter(b => b.rarity === 'rare').length,
                ultimate: data.badges.filter(b => b.rarity === 'ultimate').length,
                legendary: data.badges.filter(b => b.rarity === 'legendary').length
            };

            // Add username
            data.profile.username = username;

            const json = JSON.stringify(data, null, 2);

            // Log to console
            console.log("Exercism Data:", json);

            // Copy to clipboard
            try {
                await navigator.clipboard.writeText(json);
                console.log("Copied to clipboard!");
            } catch (e) {
                console.warn("Clipboard copy failed:", e);
            }

            // Download file
            const blob = new Blob([json], {type: "application/json"});
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `exercism-data-${new Date().toISOString().split("T")[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            // Show alert
            alert(
                "Exercism Data Extracted!\n\n" +
                `Username: ${username}\n` +
                `Reputation: ${data.stats.reputation || 'N/A'}\n` +
                `Total Badges: ${data.stats.total_badges || data.badges.length}\n` +
                `Total Solutions: ${data.stats.total_solutions || 0}\n` +
                `Total Tracks: ${data.stats.total_tracks || 0}\n\n` +
                "JSON downloaded and copied to clipboard!"
            );

        } catch (error) {
            console.error("Error:", error);
            alert("Error extracting data: " + error.message);
        }
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => setTimeout(createButton, 2000));
    } else {
        setTimeout(createButton, 2000);
    }

})();

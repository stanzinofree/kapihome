// ==UserScript==
// @name         LinkedIn Stats Extractor
// @namespace    http://tampermonkey.net/
// @version      1.2.0
// @description  Extract LinkedIn dashboard stats with manual edit capability
// @author       Alessandro Middei
// @match        https://www.linkedin.com/dashboard/
// @match        https://www.linkedin.com/dashboard/*
// @icon         https://www.linkedin.com/favicon.ico
// @grant        GM_setClipboard
// @grant        GM_notification
// ==/UserScript==

(function() {
    "use strict";

    const createExtractorButton = () => {
        const button = document.createElement("button");
        button.id = "linkedin-stats-extractor-btn";
        button.innerHTML = "📊 Extract Stats";
        button.style.cssText = `
            position: fixed; bottom: 30px; right: 30px; z-index: 9999;
            padding: 12px 20px; background: linear-gradient(135deg, #0aff9d, #00d4ff);
            color: #0f0f0f; border: none; border-radius: 8px;
            font-weight: bold; font-size: 14px; cursor: pointer;
            box-shadow: 0 4px 15px rgba(10, 255, 157, 0.4);
            transition: all 0.3s ease;
        `;

        button.addEventListener("mouseenter", () => {
            button.style.transform = "scale(1.05)";
            button.style.boxShadow = "0 6px 20px rgba(10, 255, 157, 0.6)";
        });

        button.addEventListener("mouseleave", () => {
            button.style.transform = "scale(1)";
            button.style.boxShadow = "0 4px 15px rgba(10, 255, 157, 0.4)";
        });

        button.addEventListener("click", extractStats);
        document.body.appendChild(button);
    };

    const extractNumber = (text) => {
        if (!text) return 0;
        const cleaned = text.replace(/[^\d.,]/g, "").replace(",", "");
        const num = parseFloat(cleaned);
        return isNaN(num) ? 0 : num;
    };

    const extractStats = () => {
        console.log("🔍 Starting LinkedIn stats extraction...");

        const stats = {
            profile_views_7d: 0,
            profile_views_30d: 0,
            profile_views_90d: 0,
            post_impressions_7d: 0,
            post_impressions_30d: 0,
            search_appearances_7d: 0,
            search_appearances_30d: 0,
            followers: 0,
            connection_growth_7d: 0,
            engagement_rate: 0.0
        };

        const debugInfo = [];

        try {
            // Strategy 1: Try all possible selectors
            const selectors = [
                "*[class*='dashboard']",
                "*[class*='analytics']",
                "*[class*='stat']",
                "*[class*='metric']",
                "section",
                "article",
                ".pvs-list",
                "li"
            ];

            const allElements = new Set();
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => allElements.add(el));
            });

            debugInfo.push(`Found ${allElements.size} potential elements`);

            // Scan all elements for numbers
            allElements.forEach(el => {
                const text = el.textContent.toLowerCase();
                const directText = Array.from(el.childNodes)
                    .filter(n => n.nodeType === 3)
                    .map(n => n.textContent.trim())
                    .join(" ");

                // Profile views detection
                if (text.match(/profil.*view|chi.*visualizz|who.*view|visualizzazioni.*profil|hanno.*visitato/i)) {
                    debugInfo.push(`Profile views card found: ${text.substring(0, 100)}`);
                    const numbers = extractAllNumbers(el);
                    debugInfo.push(`  Numbers found: ${JSON.stringify(numbers)}`);
                    if (numbers.length >= 1) stats.profile_views_7d = Math.max(stats.profile_views_7d, numbers[0]);
                    if (numbers.length >= 2) stats.profile_views_30d = Math.max(stats.profile_views_30d, numbers[1]);
                    if (numbers.length >= 3) stats.profile_views_90d = Math.max(stats.profile_views_90d, numbers[2]);
                }

                // Post impressions
                if (text.match(/impression|visualizzazioni.*post/i)) {
                    debugInfo.push(`Post impressions card found: ${text.substring(0, 100)}`);
                    const numbers = extractAllNumbers(el);
                    debugInfo.push(`  Numbers found: ${JSON.stringify(numbers)}`);
                    if (numbers.length >= 1) stats.post_impressions_7d = Math.max(stats.post_impressions_7d, numbers[0]);
                    if (numbers.length >= 2) stats.post_impressions_30d = Math.max(stats.post_impressions_30d, numbers[1]);
                }

                // Search appearances
                if (text.match(/search.*appear|ricerche.*compar/i)) {
                    debugInfo.push(`Search appearances found: ${text.substring(0, 100)}`);
                    const numbers = extractAllNumbers(el);
                    debugInfo.push(`  Numbers found: ${JSON.stringify(numbers)}`);
                    if (numbers.length >= 1) stats.search_appearances_7d = Math.max(stats.search_appearances_7d, numbers[0]);
                    if (numbers.length >= 2) stats.search_appearances_30d = Math.max(stats.search_appearances_30d, numbers[1]);
                }

                // Followers
                if (text.match(/follower|seguaci/i) && !text.match(/connection/i)) {
                    debugInfo.push(`Followers found: ${text.substring(0, 100)}`);
                    const numbers = extractAllNumbers(el);
                    debugInfo.push(`  Numbers found: ${JSON.stringify(numbers)}`);
                    if (numbers.length >= 1) stats.followers = Math.max(stats.followers, numbers[0]);
                }

                // Connections growth
                if (text.match(/(new.*connection|nuov.*conness)/i)) {
                    debugInfo.push(`Connection growth found: ${text.substring(0, 100)}`);
                    const numbers = extractAllNumbers(el);
                    debugInfo.push(`  Numbers found: ${JSON.stringify(numbers)}`);
                    if (numbers.length >= 1) stats.connection_growth_7d = Math.max(stats.connection_growth_7d, numbers[0]);
                }
            });

            // Calculate engagement rate
            if (stats.followers > 0 && stats.post_impressions_7d > 0) {
                stats.engagement_rate = parseFloat(((stats.post_impressions_7d / stats.followers) * 100).toFixed(2));
            }

            const output = {
                stats: stats,
                extracted_at: new Date().toISOString(),
                note: "Extracted from LinkedIn Dashboard",
                debug: debugInfo
            };

            const jsonOutput = JSON.stringify(output, null, 2);
            showResultModal(jsonOutput, stats, debugInfo);
            console.log("✅ Extraction complete:", output);

        } catch (error) {
            console.error("❌ Extraction error:", error);
            alert("Error extracting stats. Check console for details.\n\n" + error.message);
        }
    };

    const extractAllNumbers = (element) => {
        const numbers = [];
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let node;
        while (node = walker.nextNode()) {
            const val = extractNumber(node.textContent);
            if (val > 0 && !numbers.includes(val)) {
                numbers.push(val);
            }
        }

        return numbers;
    };

    const showResultModal = (json, stats, debugInfo = []) => {
        const existing = document.getElementById("stats-extractor-modal");
        if (existing) existing.remove();

        const modal = document.createElement("div");
        modal.id = "stats-extractor-modal";
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.8); z-index: 10000;
            display: flex; align-items: center; justify-content: center;
            backdrop-filter: blur(5px);
        `;

        const content = document.createElement("div");
        content.style.cssText = `
            background: #1a1a1a; border: 2px solid #0aff9d;
            border-radius: 12px; padding: 30px; max-width: 800px;
            max-height: 80vh; overflow-y: auto;
            box-shadow: 0 0 40px rgba(10, 255, 157, 0.4); color: #ffffff;
        `;

        const hasData = Object.values(stats).some(v => v > 0);

        content.innerHTML = `
            <h2 style="color: #0aff9d; margin-bottom: 20px;">📊 LinkedIn Stats Extracted</h2>
            ${hasData ? `
            <div style="margin-bottom: 20px; background: rgba(10, 255, 157, 0.1); padding: 15px; border-radius: 8px;">
                <h3 style="color: #00d4ff; margin-bottom: 10px;">Summary:</h3>
                <ul style="list-style: none; padding: 0;">
                    <li>Profile Views (7d): <strong>${stats.profile_views_7d}</strong></li>
                    <li>Profile Views (30d): <strong>${stats.profile_views_30d}</strong></li>
                    <li>Profile Views (90d): <strong>${stats.profile_views_90d}</strong></li>
                    <li>Post Impressions (7d): <strong>${stats.post_impressions_7d}</strong></li>
                    <li>Post Impressions (30d): <strong>${stats.post_impressions_30d}</strong></li>
                    <li>Followers: <strong>${stats.followers}</strong></li>
                    <li>Engagement Rate: <strong>${stats.engagement_rate}%</strong></li>
                </ul>
            </div>
            ` : `
            <div style="margin-bottom: 20px; background: rgba(255, 165, 0, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid orange;">
                <p style="color: orange; margin: 0;">⚠️ No stats found. LinkedIn layout may have changed.</p>
                <p style="color: #aaa; margin-top: 10px; font-size: 12px;">Check debug info below or open browser console (F12) for details.</p>
            </div>
            `}
            ${debugInfo.length > 0 ? `
            <details style="margin-bottom: 15px;">
                <summary style="color: #00d4ff; cursor: pointer; padding: 10px; background: rgba(0, 212, 255, 0.1); border-radius: 6px;">
                    🔍 Debug Info (${debugInfo.length} entries)
                </summary>
                <div style="margin-top: 10px; padding: 10px; background: #0f0f0f; border-radius: 6px; max-height: 200px; overflow-y: auto;">
                    ${debugInfo.map(info => `<div style="font-size: 11px; color: #888; margin-bottom: 5px; font-family: monospace;">${info}</div>`).join('')}
                </div>
            </details>
            ` : ''}
            <h3 style="color: #00d4ff; margin-bottom: 10px;">JSON Output:</h3>
            <textarea id="stats-json-output" readonly style="
                width: 100%; height: 250px; background: #0f0f0f;
                color: #0aff9d; border: 1px solid #333;
                padding: 15px; font-family: monospace; margin-bottom: 15px;
            ">${json}</textarea>
            <div style="display: flex; gap: 10px; justify-content: space-between; align-items: center;">
                <button id="manual-edit-btn" style="padding: 10px 20px; background: #555; color: #fff; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">✏️ Edit Values</button>
                <div style="display: flex; gap: 10px;">
                    <button id="copy-json-btn" style="padding: 10px 20px; background: linear-gradient(135deg, #0aff9d, #00d4ff); color: #0f0f0f; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">📋 Copy JSON</button>
                    <button id="download-json-btn" style="padding: 10px 20px; background: linear-gradient(135deg, #00d4ff, #0aff9d); color: #0f0f0f; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">💾 Download JSON</button>
                    <button id="close-modal-btn" style="padding: 10px 20px; background: #333; color: #fff; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">✕ Close</button>
                </div>
            </div>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);

        document.getElementById("manual-edit-btn").addEventListener("click", () => {
            const editedStats = { ...stats };
            
            const promptValue = (label, currentValue) => {
                const input = prompt(`${label} (current: ${currentValue})`, currentValue);
                if (input === null) return null; // User cancelled
                const num = parseFloat(input);
                return isNaN(num) ? currentValue : num;
            };

            const newProfileViews7d = promptValue("Profile Views (7 days)", editedStats.profile_views_7d);
            if (newProfileViews7d === null) return;
            editedStats.profile_views_7d = newProfileViews7d;

            const newProfileViews30d = promptValue("Profile Views (30 days)", editedStats.profile_views_30d);
            if (newProfileViews30d === null) return;
            editedStats.profile_views_30d = newProfileViews30d;

            const newProfileViews90d = promptValue("Profile Views (90 days)", editedStats.profile_views_90d);
            if (newProfileViews90d === null) return;
            editedStats.profile_views_90d = newProfileViews90d;

            const newSearchAppear7d = promptValue("Search Appearances (7 days)", editedStats.search_appearances_7d);
            if (newSearchAppear7d === null) return;
            editedStats.search_appearances_7d = newSearchAppear7d;

            const newSearchAppear30d = promptValue("Search Appearances (30 days)", editedStats.search_appearances_30d);
            if (newSearchAppear30d === null) return;
            editedStats.search_appearances_30d = newSearchAppear30d;

            const newConnGrowth = promptValue("Connection Growth (7 days)", editedStats.connection_growth_7d);
            if (newConnGrowth === null) return;
            editedStats.connection_growth_7d = newConnGrowth;

            // Recalculate engagement rate
            if (editedStats.followers > 0 && editedStats.post_impressions_7d > 0) {
                editedStats.engagement_rate = parseFloat(((editedStats.post_impressions_7d / editedStats.followers) * 100).toFixed(2));
            }

            const editedOutput = {
                stats: editedStats,
                extracted_at: new Date().toISOString(),
                note: "Extracted from LinkedIn Dashboard (manually edited)"
            };

            const editedJson = JSON.stringify(editedOutput, null, 2);
            showResultModal(editedJson, editedStats, [`Manually edited values at ${new Date().toISOString()}`]);
        });

        document.getElementById("copy-json-btn").addEventListener("click", () => {
            navigator.clipboard.writeText(json).then(() => {
                alert("✅ JSON copied to clipboard!");
            });
        });

        document.getElementById("download-json-btn").addEventListener("click", () => {
            const blob = new Blob([json], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `linkedin-stats-${new Date().toISOString().split("T")[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });

        document.getElementById("close-modal-btn").addEventListener("click", () => {
            modal.remove();
        });

        modal.addEventListener("click", (e) => {
            if (e.target === modal) modal.remove();
        });
    };

    const init = () => {
        if (document.getElementById("linkedin-stats-extractor-btn")) return;
        
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", createExtractorButton);
        } else {
            createExtractorButton();
        }

        console.log("✅ LinkedIn Stats Extractor loaded!");
    };

    setTimeout(init, 2000);

})();

// ==UserScript==
// @name         LinkedIn Stats Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Extract LinkedIn dashboard stats and export as JSON
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

        try {
            const viewsCards = document.querySelectorAll("[class*=dashboard-stats], [class*=stat-card], .analytics-card");
            
            viewsCards.forEach(card => {
                const text = card.textContent.toLowerCase();
                
                if (text.includes("profile view") || text.includes("who viewed")) {
                    const numbers = card.querySelectorAll("[class*=number], [class*=stat-value], strong, h3, h4");
                    numbers.forEach((numEl, idx) => {
                        const val = extractNumber(numEl.textContent);
                        if (val > 0) {
                            if (idx === 0) stats.profile_views_7d = val;
                            else if (idx === 1) stats.profile_views_30d = val;
                            else if (idx === 2) stats.profile_views_90d = val;
                        }
                    });
                }

                if (text.includes("post impression") || text.includes("impressions")) {
                    const numbers = card.querySelectorAll("[class*=number], [class*=stat-value], strong, h3, h4");
                    numbers.forEach((numEl, idx) => {
                        const val = extractNumber(numEl.textContent);
                        if (val > 0) {
                            if (idx === 0) stats.post_impressions_7d = val;
                            else if (idx === 1) stats.post_impressions_30d = val;
                        }
                    });
                }

                if (text.includes("search appear") || text.includes("searches")) {
                    const numbers = card.querySelectorAll("[class*=number], [class*=stat-value], strong, h3, h4");
                    numbers.forEach((numEl, idx) => {
                        const val = extractNumber(numEl.textContent);
                        if (val > 0) {
                            if (idx === 0) stats.search_appearances_7d = val;
                            else if (idx === 1) stats.search_appearances_30d = val;
                        }
                    });
                }

                if (text.includes("follower")) {
                    const numbers = card.querySelectorAll("[class*=number], [class*=stat-value], strong, h3, h4");
                    const val = extractNumber(numbers[0]?.textContent);
                    if (val > 0) stats.followers = val;
                }

                if (text.includes("connection") && (text.includes("new") || text.includes("growth"))) {
                    const numbers = card.querySelectorAll("[class*=number], [class*=stat-value], strong, h3, h4");
                    const val = extractNumber(numbers[0]?.textContent);
                    if (val > 0) stats.connection_growth_7d = val;
                }
            });

            if (stats.followers > 0 && stats.post_impressions_7d > 0) {
                stats.engagement_rate = parseFloat(((stats.post_impressions_7d / stats.followers) * 100).toFixed(2));
            }

            const output = {
                stats: stats,
                extracted_at: new Date().toISOString(),
                note: "Extracted from LinkedIn Dashboard"
            };

            const jsonOutput = JSON.stringify(output, null, 2);
            showResultModal(jsonOutput, stats);
            console.log("✅ Extraction complete:", output);

        } catch (error) {
            console.error("❌ Extraction error:", error);
            alert("Error extracting stats. Check console for details.");
        }
    };

    const showResultModal = (json, stats) => {
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
            border-radius: 12px; padding: 30px; max-width: 700px;
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
            ` : '<p style="color: orange;">⚠️ No stats found. Make sure you are on the dashboard page.</p>'}
            <h3 style="color: #00d4ff; margin-bottom: 10px;">JSON Output:</h3>
            <textarea id="stats-json-output" readonly style="
                width: 100%; height: 250px; background: #0f0f0f;
                color: #0aff9d; border: 1px solid #333;
                padding: 15px; font-family: monospace; margin-bottom: 15px;
            ">${json}</textarea>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button id="copy-json-btn" style="padding: 10px 20px; background: linear-gradient(135deg, #0aff9d, #00d4ff); color: #0f0f0f; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">📋 Copy JSON</button>
                <button id="download-json-btn" style="padding: 10px 20px; background: linear-gradient(135deg, #00d4ff, #0aff9d); color: #0f0f0f; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">💾 Download JSON</button>
                <button id="close-modal-btn" style="padding: 10px 20px; background: #333; color: #fff; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">✕ Close</button>
            </div>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);

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

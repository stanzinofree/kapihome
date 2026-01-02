// ==UserScript==
// @name         LinkedIn Stats Extractor (Minimal)
// @namespace    http://tampermonkey.net/
// @version      1.6.0
// @description  Simple extractor with auto-download
// @author       Alessandro Middei
// @match        https://www.linkedin.com/dashboard/
// @match        https://www.linkedin.com/dashboard/*
// @icon         https://www.linkedin.com/favicon.ico
// @grant        none
// ==/UserScript==

(function() {
    "use strict";

    const createButton = () => {
        const btn = document.createElement("button");
        btn.textContent = "📊 Extract Stats";
        btn.style.cssText = "position:fixed;bottom:30px;right:30px;z-index:9999;padding:12px 20px;background:#0aff9d;color:#000;border:none;border-radius:8px;font-weight:bold;cursor:pointer;";
        btn.onclick = extractStats;
        document.body.appendChild(btn);
    };

    const extractStats = () => {
        const stats = {
            profile_views_90d: 0,
            post_impressions_7d: 0,
            search_appearances_7d: 0,
            followers: 0,
            follower_growth_pct: 0
        };

        try {
            const cards = document.querySelectorAll(".pcd-analytics-view-item");
            
            cards.forEach(card => {
                const mainNum = card.querySelector(".text-body-large-bold");
                const label = card.querySelector(".text-body-small");
                
                if (!mainNum || !label) return;
                
                const value = parseFloat(mainNum.textContent.replace(/\./g, "").replace(",", "."));
                const labelText = label.textContent.toLowerCase();
                
                if (labelText.includes("impression")) {
                    stats.post_impressions_7d = value;
                } else if (labelText.includes("follower")) {
                    stats.followers = value;
                    const growthEl = card.querySelector(".analytics-tools-shared-trend-text__value--increase-caret-lead");
                    if (growthEl) {
                        stats.follower_growth_pct = parseFloat(growthEl.textContent.replace("%", "").replace(",", "."));
                    }
                } else if (labelText.includes("visitatori")) {
                    stats.profile_views_90d = value;
                } else if (labelText.includes("comparse")) {
                    stats.search_appearances_7d = value;
                }
            });

            const output = {
                stats: stats,
                extracted_at: new Date().toISOString(),
                note: "Extracted from LinkedIn Dashboard"
            };

            const json = JSON.stringify(output, null, 2);
            
            // Log to console
            console.log("LinkedIn Stats:", json);

            // Try to copy
            try {
                navigator.clipboard.writeText(json);
                console.log("Copied to clipboard!");
            } catch (e) {
                console.log("Clipboard copy failed:", e);
            }

            // Download
            const blob = new Blob([json], {type: "application/json"});
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "linkedin-stats-" + new Date().toISOString().split("T")[0] + ".json";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            // Show alert
            alert("Stats extracted!\n\nPost Impressions: " + stats.post_impressions_7d + "\nFollowers: " + stats.followers + "\nProfile Views (90d): " + stats.profile_views_90d + "\nSearch Appearances: " + stats.search_appearances_7d + "\n\nJSON downloaded and copied to clipboard!");

        } catch (error) {
            console.error("Error:", error);
            alert("Error extracting stats: " + error.message);
        }
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", createButton);
    } else {
        setTimeout(createButton, 2000);
    }

})();

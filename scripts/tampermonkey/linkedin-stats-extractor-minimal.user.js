// ==UserScript==
// @name         LinkedIn Stats Extractor (Minimal)
// @namespace    http://tampermonkey.net/
// @version      1.5.0
// @description  Simple extractor with auto-download and clipboard copy
// @author       Alessandro Middei
// @match        https://www.linkedin.com/dashboard/
// @match        https://www.linkedin.com/dashboard/*
// @icon         https://www.linkedin.com/favicon.ico
// @grant        none
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
        `;
        button.addEventListener("click", extractStats);
        document.body.appendChild(button);
    };

    const extractStats = () => {
        console.log("🔍 Extracting LinkedIn stats...");

        const stats = {
            profile_views_90d: 0,
            post_impressions_7d: 0,
            search_appearances_7d: 0,
            followers: 0,
            follower_growth_pct: 0
        };

        try {
            // Find all analytics cards
            const cards = document.querySelectorAll(".pcd-analytics-view-item");
            
            cards.forEach(card => {
                const text = card.textContent;
                const mainNumber = card.querySelector(".text-body-large-bold");
                const label = card.querySelector(".text-body-small");
                
                if (!mainNumber || !label) return;
                
                const value = parseFloat(mainNumber.textContent.replace(/\./g, "").replace(",", "."));
                const labelText = label.textContent.toLowerCase();
                
                console.log(`Found: ${labelText} = ${value}`);
                
                if (labelText.includes("impression")) {
                    stats.post_impressions_7d = value;
                } else if (labelText.includes("follower")) {
                    stats.followers = value;
                    // Extract growth percentage
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
                note: "Extracted actual values from LinkedIn Dashboard (no estimates)"
            };

            const jsonOutput = JSON.stringify(output, null, 2);
            showResultModal(jsonOutput, stats);
            console.log("✅ Extraction complete:", output);

        } catch (error) {
            console.error("❌ Error:", error);
            alert("Error extracting stats: " + error.message);
        }
    };

    const showResultModal = (json, stats) => {
        // Summary
        const summary = `📊 LinkedIn Stats Extracted!\n\n` +
            `Post Impressions (7d): ${stats.post_impressions_7d}\n` +
            `Followers: ${stats.followers} (+${stats.follower_growth_pct}%)\n` +
            `Profile Views (90d): ${stats.profile_views_90d}\n` +
            `Search Appearances (7d): ${stats.search_appearances_7d}\n\n` +
            `JSON is in console and will be downloaded.`;

        // Show summary
        alert(summary);

        // Log to console
        console.log("📊 LinkedIn Stats JSON:");
        console.log(json);

        // Copy to clipboard
        navigator.clipboard.writeText(json).then(() => {
            console.log("✅ JSON copied to clipboard!");
        }).catch(err => {
            console.error("❌ Copy failed:", err);
            // Fallback: show JSON in prompt for manual copy
            prompt("Copy this JSON:", json);
        });

        // Auto-download
        try {
            const blob = new Blob([json], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `linkedin-stats-${new Date().toISOString().split("T")[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            console.log("💾 JSON file downloaded!");
        } catch (err) {
            console.error("❌ Download failed:", err);
        }
    };

    setTimeout(() => {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", createExtractorButton);
        } else {
            createExtractorButton();
        }
    }, 2000);

})();

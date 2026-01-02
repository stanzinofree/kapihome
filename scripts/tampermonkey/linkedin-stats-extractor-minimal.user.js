// ==UserScript==
// @name         LinkedIn Stats Extractor (Minimal)
// @namespace    http://tampermonkey.net/
// @version      1.4.0
// @description  Extract only actual LinkedIn dashboard stats (no estimates)
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
        const existing = document.getElementById("stats-modal");
        if (existing) existing.remove();

        const modal = document.createElement("div");
        modal.id = "stats-modal";
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.8); z-index: 10000;
            display: flex; align-items: center; justify-content: center;
        `;

        const content = document.createElement("div");
        content.style.cssText = `
            background: #1a1a1a; border: 2px solid #0aff9d;
            border-radius: 12px; padding: 30px; max-width: 600px;
            color: #ffffff;
        `;

        content.innerHTML = `
            <h2 style="color: #0aff9d; margin-bottom: 20px;">📊 LinkedIn Stats</h2>
            <div style="margin-bottom: 20px; background: rgba(10, 255, 157, 0.1); padding: 15px; border-radius: 8px;">
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li>Post Impressions (7d): <strong>${stats.post_impressions_7d}</strong></li>
                    <li>Followers: <strong>${stats.followers}</strong> (+${stats.follower_growth_pct}%)</li>
                    <li>Profile Views (90d): <strong>${stats.profile_views_90d}</strong></li>
                    <li>Search Appearances (7d): <strong>${stats.search_appearances_7d}</strong></li>
                </ul>
            </div>
            <textarea id="json-output" readonly style="
                width: 100%; height: 200px; background: #0f0f0f;
                color: #0aff9d; border: 1px solid #333;
                padding: 15px; font-family: monospace; margin-bottom: 15px;
            ">${json}</textarea>
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button id="copy-btn" style="padding: 10px 20px; background: linear-gradient(135deg, #0aff9d, #00d4ff); color: #0f0f0f; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">📋 Copy</button>
                <button id="download-btn" style="padding: 10px 20px; background: linear-gradient(135deg, #00d4ff, #0aff9d); color: #0f0f0f; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">💾 Download</button>
                <button id="close-btn" style="padding: 10px 20px; background: #333; color: #fff; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;">✕ Close</button>
            </div>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);

        document.getElementById("copy-btn").addEventListener("click", () => {
            navigator.clipboard.writeText(json);
            alert("✅ Copied!");
        });

        document.getElementById("download-btn").addEventListener("click", () => {
            const blob = new Blob([json], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `linkedin-stats-${new Date().toISOString().split("T")[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
        });

        document.getElementById("close-btn").addEventListener("click", () => modal.remove());
        modal.addEventListener("click", (e) => { if (e.target === modal) modal.remove(); });
    };

    setTimeout(() => {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", createExtractorButton);
        } else {
            createExtractorButton();
        }
    }, 2000);

})();

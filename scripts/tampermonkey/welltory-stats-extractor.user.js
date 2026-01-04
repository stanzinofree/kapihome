// ==UserScript==
// @name         Welltory Stats Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Extract health metrics from Welltory web app
// @author       Alessandro Middei
// @match        https://app.welltory.com/*
// @icon         https://welltory.com/favicon.ico
// @grant        none
// ==/UserScript==

(function() {
    "use strict";

    const createButton = () => {
        const btn = document.createElement("button");
        btn.textContent = "📊 Extract Welltory Stats";
        btn.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 9999;
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        `;
        btn.onmouseover = () => {
            btn.style.transform = "translateY(-2px)";
            btn.style.boxShadow = "0 6px 12px rgba(0,0,0,0.15)";
        };
        btn.onmouseout = () => {
            btn.style.transform = "translateY(0)";
            btn.style.boxShadow = "0 4px 6px rgba(0,0,0,0.1)";
        };
        btn.onclick = extractStats;
        document.body.appendChild(btn);
    };

    const extractStats = () => {
        console.log("🔍 Starting Welltory extraction...");

        const stats = {
            stress: null,
            energy: null,
            productivity: null,
            hrv: null,
            resting_heart_rate: null,
            sleep_quality: null,
            mood: null
        };

        const today = new Date().toISOString().split('T')[0];

        try {
            // Strategy 1: Try to find metric cards/widgets
            const metricCards = document.querySelectorAll('[class*="metric"], [class*="card"], [class*="widget"]');
            
            metricCards.forEach(card => {
                const text = card.textContent.toLowerCase();
                const numbers = card.textContent.match(/\d+(\.\d+)?/g);
                
                if (!numbers || numbers.length === 0) return;
                
                const value = parseFloat(numbers[0]);
                
                // Identify metrics by text content
                if (text.includes('stress') && stats.stress === null) {
                    stats.stress = value;
                } else if (text.includes('energy') && stats.energy === null) {
                    stats.energy = value;
                } else if ((text.includes('productivity') || text.includes('performance')) && stats.productivity === null) {
                    stats.productivity = value;
                } else if ((text.includes('hrv') || text.includes('variability')) && stats.hrv === null) {
                    stats.hrv = value;
                } else if ((text.includes('heart rate') || text.includes('rhr')) && !text.includes('variability') && stats.resting_heart_rate === null) {
                    stats.resting_heart_rate = value;
                } else if (text.includes('sleep') && stats.sleep_quality === null) {
                    stats.sleep_quality = value;
                } else if (text.includes('mood') && stats.mood === null) {
                    stats.mood = value;
                }
            });

            // Strategy 2: Try to extract from dashboard numbers/values
            const dashboardValues = document.querySelectorAll('[class*="value"], [class*="number"], [class*="score"]');
            
            dashboardValues.forEach(el => {
                const parentText = el.parentElement?.textContent.toLowerCase() || '';
                const value = parseFloat(el.textContent.replace(/[^\d.]/g, ''));
                
                if (isNaN(value)) return;
                
                if (parentText.includes('stress') && stats.stress === null) {
                    stats.stress = value;
                } else if (parentText.includes('energy') && stats.energy === null) {
                    stats.energy = value;
                } else if (parentText.includes('productivity') && stats.productivity === null) {
                    stats.productivity = value;
                }
            });

            // Strategy 3: Try to extract from chart labels/titles
            const chartTitles = document.querySelectorAll('h1, h2, h3, h4, [class*="title"], [class*="heading"]');
            
            chartTitles.forEach(title => {
                const text = title.textContent.toLowerCase();
                const nextEl = title.nextElementSibling;
                
                if (!nextEl) return;
                
                const numbers = nextEl.textContent.match(/\d+(\.\d+)?/g);
                if (!numbers) return;
                
                const value = parseFloat(numbers[0]);
                
                if (text.includes('stress') && stats.stress === null) {
                    stats.stress = value;
                } else if (text.includes('energy') && stats.energy === null) {
                    stats.energy = value;
                } else if (text.includes('hrv') && stats.hrv === null) {
                    stats.hrv = value;
                }
            });

        } catch (error) {
            console.error("Error extracting stats:", error);
        }

        // Build output structure
        const output = {
            stats: {
                stress: stats.stress,
                energy: stats.energy,
                productivity: stats.productivity,
                hrv: stats.hrv,
                resting_heart_rate: stats.resting_heart_rate,
                sleep_quality: stats.sleep_quality,
                mood: stats.mood
            },
            date: today,
            extracted_at: new Date().toISOString(),
            source: "welltory_webapp",
            note: "Extracted from Welltory Web App"
        };

        const json = JSON.stringify(output, null, 2);

        // Log results
        console.log("📊 Welltory Stats Extracted:");
        console.log(json);
        console.table(output.stats);

        // Copy to clipboard
        try {
            navigator.clipboard.writeText(json).then(() => {
                console.log("✅ Copied to clipboard!");
                showNotification("✅ Stats copied to clipboard!", "success");
            }).catch(err => {
                console.log("⚠️  Clipboard copy failed:", err);
            });
        } catch (e) {
            console.log("⚠️  Clipboard not available");
        }

        // Auto-download JSON file
        downloadJSON(output, `welltory-stats-${today}.json`);

        // Show summary notification
        const validStats = Object.values(output.stats).filter(v => v !== null).length;
        showNotification(
            `📊 Extracted ${validStats} metrics!\n${JSON.stringify(output.stats, null, 2)}`,
            validStats > 0 ? "success" : "warning"
        );
    };

    const downloadJSON = (data, filename) => {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log(`📥 Downloaded: ${filename}`);
    };

    const showNotification = (message, type = "info") => {
        const notification = document.createElement("div");
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 30px;
            right: 30px;
            z-index: 10000;
            padding: 16px 24px;
            background: ${type === "success" ? "#10b981" : type === "warning" ? "#f59e0b" : "#3b82f6"};
            color: white;
            border-radius: 8px;
            font-weight: 500;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 400px;
            white-space: pre-wrap;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = "slideOut 0.3s ease";
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 5000);
    };

    // Add CSS animations
    const style = document.createElement("style");
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(400px); opacity: 0; }
        }
    `;
    document.head.appendChild(style);

    // Wait for page to load, then create button
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", createButton);
    } else {
        createButton();
    }

    console.log("🚀 Welltory Stats Extractor loaded!");
})();

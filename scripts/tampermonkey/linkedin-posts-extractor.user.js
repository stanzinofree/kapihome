// ==UserScript==
// @name         LinkedIn Posts Extractor
// @namespace    http://tampermonkey.net/
// @version      1.1.0
// @description  Extract recent posts from LinkedIn profile (fixed selectors)
// @author       Alessandro Middei
// @match        https://www.linkedin.com/in/*/recent-activity/all/
// @match        https://www.linkedin.com/in/stanzinofree/recent-activity/all/
// @icon         https://www.linkedin.com/favicon.ico
// @grant        none
// ==/UserScript==

(function() {
    "use strict";

    const createButton = () => {
        const btn = document.createElement("button");
        btn.textContent = "📝 Extract Posts";
        btn.style.cssText = "position:fixed;bottom:30px;right:30px;z-index:9999;padding:12px 20px;background:#0aff9d;color:#000;border:none;border-radius:8px;font-weight:bold;cursor:pointer;";
        btn.onclick = extractPosts;
        document.body.appendChild(btn);
    };

    const extractPosts = () => {
        console.log("🔍 Extracting LinkedIn posts...");

        try {
            const posts = [];
            
            // Find all post containers - use the feed-shared-update-v2 class
            const postElements = document.querySelectorAll('.feed-shared-update-v2');
            
            console.log("Found " + postElements.length + " post elements");

            postElements.forEach((postEl, index) => {
                if (index >= 5) return; // Limit to 5 posts

                try {
                    // Extract post text from update-components-text
                    const textEl = postEl.querySelector('.update-components-text');
                    let title = "";
                    let excerpt = "";
                    
                    if (textEl) {
                        const fullText = textEl.textContent.trim();
                        // Clean up whitespace
                        const cleaned = fullText.replace(/\s+/g, ' ').trim();
                        // First sentence or first 100 chars as title
                        const sentences = cleaned.split(/[.!?]\s+/);
                        title = sentences[0] ? sentences[0].substring(0, 100) : cleaned.substring(0, 100);
                        excerpt = cleaned.substring(0, 250);
                    }

                    // Extract URN from data-urn attribute to build URL
                    const urn = postEl.getAttribute('data-urn');
                    let url = "";
                    if (urn) {
                        // Extract activity ID from urn:li:activity:7411868109092896770
                        const activityId = urn.split(':').pop();
                        url = "https://www.linkedin.com/feed/update/" + urn + "/";
                    }

                    // Extract date - try to find relative time text
                    const timeText = postEl.querySelector('.update-components-actor__sub-description');
                    let date = new Date().toISOString().split('T')[0];
                    if (timeText) {
                        const text = timeText.textContent.toLowerCase();
                        // Parse relative dates like "2 giorni" or "1 settimana"
                        if (text.includes('giorn') || text.includes('day')) {
                            const match = text.match(/(\d+)/);
                            if (match) {
                                const daysAgo = parseInt(match[1]);
                                const d = new Date();
                                d.setDate(d.getDate() - daysAgo);
                                date = d.toISOString().split('T')[0];
                            }
                        }
                    }

                    // Only add if we have text
                    if (title && excerpt) {
                        posts.push({
                            title: title,
                            excerpt: excerpt,
                            date: date,
                            url: url || "https://www.linkedin.com/in/stanzinofree/recent-activity/"
                        });
                        
                        console.log("Extracted post " + (index + 1) + ":", {title: title.substring(0, 50) + "...", date, url});
                    }
                } catch (err) {
                    console.error("Error extracting post " + index + ":", err);
                }
            });

            const output = {
                recent_posts: posts,
                extracted_at: new Date().toISOString(),
                note: "Extracted from LinkedIn recent activity"
            };

            const json = JSON.stringify(output, null, 2);
            
            // Log to console
            console.log("LinkedIn Posts:", json);

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
            a.download = "linkedin-posts-" + new Date().toISOString().split("T")[0] + ".json";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            // Show alert
            alert("Posts extracted!\n\n" + posts.length + " posts found\n\nJSON downloaded and copied to clipboard!");

        } catch (error) {
            console.error("Error:", error);
            alert("Error extracting posts: " + error.message);
        }
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => setTimeout(createButton, 3000));
    } else {
        setTimeout(createButton, 3000);
    }

})();

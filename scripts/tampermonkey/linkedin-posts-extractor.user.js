// ==UserScript==
// @name         LinkedIn Posts Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Extract recent posts from LinkedIn profile
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
            
            // Find all post containers
            const postElements = document.querySelectorAll('.profile-creator-shared-feed-update__container');
            
            console.log("Found " + postElements.length + " post elements");

            postElements.forEach((postEl, index) => {
                if (index >= 5) return; // Limit to 5 posts

                try {
                    // Extract post text/title
                    const textEl = postEl.querySelector('.feed-shared-update-v2__description, .feed-shared-text__text-view');
                    let title = "";
                    let excerpt = "";
                    
                    if (textEl) {
                        const fullText = textEl.textContent.trim();
                        // First line or first 80 chars as title
                        const lines = fullText.split('\n').filter(l => l.trim());
                        title = lines[0] ? lines[0].substring(0, 100) : "";
                        excerpt = fullText.substring(0, 200);
                    }

                    // Extract timestamp
                    const timeEl = postEl.querySelector('.feed-shared-actor__sub-description time, .update-components-actor__sub-description time');
                    let date = "";
                    if (timeEl) {
                        const datetime = timeEl.getAttribute('datetime');
                        if (datetime) {
                            date = datetime.split('T')[0]; // Get YYYY-MM-DD
                        }
                    }

                    // Extract post URL
                    const linkEl = postEl.querySelector('a[href*="/posts/"]');
                    let url = "";
                    if (linkEl) {
                        url = linkEl.href.split('?')[0]; // Remove query params
                    }

                    // Only add if we have minimum data
                    if (title || excerpt) {
                        posts.push({
                            title: title || excerpt.substring(0, 80) + "...",
                            excerpt: excerpt || title,
                            date: date || new Date().toISOString().split('T')[0],
                            url: url || "https://www.linkedin.com/in/stanzinofree/recent-activity/"
                        });
                        
                        console.log("Extracted post " + (index + 1) + ":", {title, date, url});
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

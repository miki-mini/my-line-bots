const apiBase = '/api/kinotake';

// State
let bambooVotes = 0;
let mushroomVotes = 0;
let pressing = false;
let pressStartTime = 0;
let keysPressed = {};
let konamiIndex = 0;
const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

// Elements
const bambooScoreEl = document.getElementById('bamboo-score');
const mushroomScoreEl = document.getElementById('mushroom-score');
const bambooBar = document.getElementById('bamboo-bar');
const mushroomBar = document.getElementById('mushroom-bar');
const logList = document.getElementById('log-list');
const refereeSpeech = document.getElementById('referee-speech');

// Functions
async function fetchState() {
    try {
        const res = await fetch(`${apiBase}/state`);
        if (!res.ok) return;
        const data = await res.json();
        updateUI(data);
    } catch (e) {
        console.error("Failed to fetch state", e);
    }
}

async function sendVote(team, count, cheat = null, helper = null) {
    // Optimistic UI update (simple increment) - creates responsive feel
    if (!cheat && team === 'bamboo') bambooScoreEl.innerText = parseInt(bambooScoreEl.innerText) + count;
    if (!cheat && team === 'mushroom') mushroomScoreEl.innerText = parseInt(mushroomScoreEl.innerText) + count;

    try {
        const res = await fetch(`${apiBase}/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team, count, cheat_code: cheat, helper_name: helper })
        });
        const data = await res.json();

        if (data.success) {
            updateUI(data.state);
        } else if (data.error === 'API_LIMIT_EXCEEDED') {
            alert(data.message);
            refereeSpeech.innerText = "API制限だ！\n落ち着け！";
        }
    } catch (e) {
        console.error("Vote failed", e);
    }
}

function updateUI(data) {
    bambooVotes = data.bamboo || 0;
    mushroomVotes = data.mushroom || 0;
    document.getElementById('prettier-score').innerText = data.prettier || 0;

    bambooScoreEl.innerText = bambooVotes;
    mushroomScoreEl.innerText = mushroomVotes;

    // Bar Logic (Visual Exaggeration)
    const total = Math.max(bambooVotes + mushroomVotes, 1);
    let bHeight = (bambooVotes / total) * 100;
    let mHeight = (mushroomVotes / total) * 100;

    // Safety clamp
    bambooBar.style.height = `${bHeight}%`;
    mushroomBar.style.height = `${mHeight}%`;

    // Logs
    if (data.culprits) {
        logList.innerHTML = '';
        data.culprits.slice().reverse().forEach(log => {
            const li = document.createElement('li');
            li.innerText = log;
            logList.appendChild(li);
        });
        logList.scrollTop = 0;
    }
}

// Event Listeners
document.getElementById('btn-bamboo').addEventListener('click', () => {
    sendVote('bamboo', 1);
});
document.getElementById('btn-mushroom').addEventListener('click', () => {
    sendVote('mushroom', 1);
});
document.getElementById('btn-prettier').addEventListener('click', () => sendVote('prettier', 1));

// Cheat Input Listener
const cheatInput = document.getElementById('cheat-input');
const cheatBtn = document.getElementById('btn-cheat');

if (cheatBtn && cheatInput) {
    cheatBtn.addEventListener('click', () => {
        const code = cheatInput.value.trim();
        if (code) {
            // Simple manual override for cheats if typed directly
            if (code === "上上下下左右左右BA" || code.toLowerCase() === "uuddlrlrba") {
                sendVote('bamboo', 100, "上上下下左右左右BA", "手入力ハッカー");
                alert("Konami Code Applied!");
            } else if (code === "Kamehameha" || code === "かめはめ波") {
                sendVote('mushroom', 500, "かめはめ波", "手入力ハッカー");
                triggerExplosion();
            } else {
                alert("無効なコマンドです");
            }
            cheatInput.value = "";
        }
    });
}

// Long Press Logic
const btns = document.querySelectorAll('.vote-btn');
btns.forEach(btn => {
    btn.addEventListener('mousedown', () => {
        pressing = true;
        pressStartTime = Date.now();
        btn.classList.add('pressing');
    });

    btn.addEventListener('mouseup', () => {
        if (!pressing) return;
        const duration = Date.now() - pressStartTime;
        btn.classList.remove('pressing');
        pressing = false;

        if (duration > 3000) {
            const team = btn.id === 'btn-bamboo' ? 'bamboo' : 'mushroom';
            sendVote(team, 100, "3秒チャージ", "チャージマン");
            triggerExplosion();
        }
    });

    btn.addEventListener('mouseleave', () => {
        if (pressing) {
            pressing = false;
            btn.classList.remove('pressing');
        }
    });
});

// Cheats
document.addEventListener('keydown', (e) => {
    // Konami
    if (e.key === konamiCode[konamiIndex]) {
        konamiIndex++;
        if (konamiIndex === konamiCode.length) {
            sendVote('bamboo', 100, "上上下下左右左右BA", "高橋名人");
            alert("Konami Code Activated! +100 Bamboo");
            konamiIndex = 0;
        }
    } else {
        konamiIndex = 0;
    }

    // KMH
    keysPressed[e.key.toUpperCase()] = true;
    if (keysPressed['K'] && keysPressed['M'] && keysPressed['H']) {
        document.body.style.boxShadow = "inset 0 0 50px blue";
    }

    if (e.key === 'Enter' && keysPressed['K'] && keysPressed['M'] && keysPressed['H']) {
        sendVote('mushroom', 500, "かめはめ波", "孫悟空");
        document.body.style.boxShadow = "none";
        triggerExplosion();
    }
});

document.addEventListener('keyup', (e) => {
    delete keysPressed[e.key.toUpperCase()];
    if (!keysPressed['K'] || !keysPressed['M'] || !keysPressed['H']) {
        document.body.style.boxShadow = "none";
    }
});

// Hidden Trigger (Background 5 clicks)
let hidden_clicks = 0;
document.getElementById('hidden-trigger').addEventListener('click', () => {
    hidden_clicks++;
    if (hidden_clicks === 5) {
        alert("Hidden Character Found!");
        hidden_clicks = 0;
    }
});

// Anywhere Door Cheat
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('gadget') === 'anywhere-door') {
    document.body.style.filter = "invert(1)";
    refereeSpeech.innerText = "どこでもドアだと！？\n票を奪う気か！";
}

function triggerExplosion() {
    document.body.classList.add('shake-screen');
    setTimeout(() => document.body.classList.remove('shake-screen'), 500);
}

// Init
fetchState();
setInterval(fetchState, 3000); // Polling slower to save bandwidth

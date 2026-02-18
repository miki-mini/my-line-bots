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
const prettierScoreEl = document.getElementById('prettier-score');
const bambooBar = document.getElementById('bamboo-bar');
const mushroomBar = document.getElementById('mushroom-bar');
const logList = document.getElementById('log-list');
const refereeSpeech = document.getElementById('referee-speech');

// Functions
async function fetchState() {
    try {
        const res = await fetch(`${apiBase}/state`);
        if (!res.ok) {
            console.error("State fetch failed:", res.status, res.statusText);
            return;
        }
        const data = await res.json();
        updateUI(data);
    } catch (e) {
        console.error("Failed to fetch state", e);
    }
}

async function sendVote(team, count, cheat = null, helper = null) {
    console.log(`Sending vote: Team=${team}, Count=${count}, Cheat=${cheat}`);

    // Optimistic UI update
    if (!cheat && team === 'bamboo' && bambooScoreEl) {
        bambooScoreEl.innerText = parseInt(bambooScoreEl.innerText || "0") + count;
    }
    if (!cheat && team === 'mushroom' && mushroomScoreEl) {
        mushroomScoreEl.innerText = parseInt(mushroomScoreEl.innerText || "0") + count;
    }

    try {
        const res = await fetch(`${apiBase}/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team, count, cheat_code: cheat, helper_name: helper })
        });

        if (!res.ok) {
            console.error("Vote failed:", res.status, res.statusText);
            const text = await res.text();
            console.error("Response:", text);
            return;
        }

        const data = await res.json();

        if (data.success) {
            updateUI(data.state);
        } else if (data.error === 'API_LIMIT_EXCEEDED') {
            alert(data.message);
            refereeSpeech.innerText = "API制限だ！\n落ち着け！";
        }
    } catch (e) {
        console.error("Vote request exception", e);
    }
}

function updateUI(data) {
    if (!data) return;

    bambooVotes = data.bamboo || 0;
    mushroomVotes = data.mushroom || 0;
    if (prettierScoreEl) prettierScoreEl.innerText = data.prettier || 0;

    if (bambooScoreEl) bambooScoreEl.innerText = bambooVotes;
    if (mushroomScoreEl) mushroomScoreEl.innerText = mushroomVotes;

    // Bar Logic
    const total = Math.max(bambooVotes + mushroomVotes, 1);
    let bHeight = (bambooVotes / total) * 100;
    let mHeight = (mushroomVotes / total) * 100;

    if (bambooBar) bambooBar.style.height = `${bHeight}%`;
    if (mushroomBar) mushroomBar.style.height = `${mHeight}%`;

    // Logs
    if (data.culprits && logList) {
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
const btnBamboo = document.getElementById('btn-bamboo');
if (btnBamboo) {
    btnBamboo.addEventListener('click', () => sendVote('bamboo', 1));
} else {
    console.error("Element btn-bamboo not found");
}

const btnMushroom = document.getElementById('btn-mushroom');
if (btnMushroom) {
    btnMushroom.addEventListener('click', () => sendVote('mushroom', 1));
} else {
    console.error("Element btn-mushroom not found");
}

const btnPrettier = document.getElementById('btn-prettier');
if (btnPrettier) {
    btnPrettier.addEventListener('click', () => sendVote('prettier', 1));
}

// Cheat Input Listener
const cheatInput = document.getElementById('cheat-input');
const cheatBtn = document.getElementById('btn-cheat');

if (cheatBtn && cheatInput) {
    cheatBtn.addEventListener('click', () => {
        const code = cheatInput.value.trim();
        if (code) {
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
const hiddenTrigger = document.getElementById('hidden-trigger');
if (hiddenTrigger) {
    hiddenTrigger.addEventListener('click', () => {
        hidden_clicks++;
        if (hidden_clicks === 5) {
            const inputArea = document.querySelector('.input-area');
            if (inputArea) {
                inputArea.style.display = inputArea.style.display === 'block' ? 'none' : 'block';
                if (inputArea.style.display === 'block') {
                    alert("Hidden Command Input Unlocked!");
                }
            }
            hidden_clicks = 0;
        }
    });
}

// Anywhere Door Cheat
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('gadget') === 'anywhere-door') {
    document.body.style.filter = "invert(1)";
    if (refereeSpeech) refereeSpeech.innerText = "どこでもドアだと！？\n票を奪う気か！";
}

function triggerExplosion() {
    document.body.classList.add('shake-screen');
    setTimeout(() => document.body.classList.remove('shake-screen'), 500);
}

// BGM Logic
const bgm = document.getElementById('bgm');
const btnAudio = document.getElementById('btn-audio');
let audioStarted = false;

function toggleAudio() {
    if (!bgm) return;
    if (bgm.paused) {
        bgm.play().then(() => {
            btnAudio.innerText = "🔊";
            audioStarted = true;
        }).catch(e => console.log("Audio play failed", e));
    } else {
        bgm.pause();
        btnAudio.innerText = "🔇";
    }
}

if (btnAudio) {
    btnAudio.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent vote triggering if overlapping
        toggleAudio();
    });
}

// Attempt to start audio on first interaction
function startAudioOnInteraction() {
    if (audioStarted) return;
    bgm.volume = 0.5; // Set volume to 50%
    bgm.play().then(() => {
        btnAudio.innerText = "🔊";
        audioStarted = true;
        // Remove listeners once started
        document.removeEventListener('click', startAudioOnInteraction);
        document.removeEventListener('keydown', startAudioOnInteraction);
    }).catch(e => {
        console.log("Autoplay prevented, waiting for interaction");
    });
}

document.addEventListener('click', startAudioOnInteraction);
document.addEventListener('keydown', startAudioOnInteraction);

// Init
console.log("Kinotae Seisen Script Loaded");
fetchState();
setInterval(fetchState, 3000);

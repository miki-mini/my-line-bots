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

async function sendVote(team, count, cheatCode = null, helperName = null) {
    console.log(`Sending vote: Team=${team}, Count=${count}, Cheat=${cheatCode}`);

    if (vimQteActive) return; // No voting during boss battle

    // Shonbori Logic
    if (team === 'prettier') {
        prettierClickCount += count;
        if (prettierClickCount >= 32 && !document.body.classList.contains('shonbori-mode')) {
            activateShonboriMode();
        }
    }

    // Optimistic UI update for standard votes
    if (!cheatCode && team === 'bamboo' && bambooScoreEl) {
        bambooScoreEl.innerText = parseInt(bambooScoreEl.innerText || "0") + count;
    }
    if (!cheatCode && team === 'mushroom' && mushroomScoreEl) {
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

            // Handle Server-Side Cheat Responses
            if (data.message === 'VIM_DUNGEON_MODE') {
                activateVimMode();
            } else if (data.message && data.message.includes("Cheat Activated")) {
                if (data.message.includes("かめはめ波") || data.message.includes("kamehameha")) {
                    triggerExplosion();
                } else if (data.message.includes("BA")) {
                    alert("Konami Code Activated! (Server)");
                }
            }

        } else if (data.error === 'API_LIMIT_EXCEEDED') {
            alert(data.message);
            if (refereeSpeech) refereeSpeech.innerText = "API制限だ！\n落ち着け！";
        } else if (data.error === 'INVALID_CODE') {
            alert("無効なコマンドです");
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

// VIM DUNGEON LOGIC
let vimQteActive = false;
let vimQteSequence = [':', 'q', '!'];
let vimQteProgress = 0; // 0, 1, 2
let vimQteCount = 0; // 0 to 5
let vimQteTimer = null;

let vimAudio = null;

function activateShonboriMode() {
    document.body.classList.add('shonbori-mode');

    // Stop Main BGM
    if (bgm) bgm.pause();

    // Play Shonbori BGM
    if (!shonboriAudio) {
        shonboriAudio = new Audio('/static/kinotake/shonbori.mp3');
        shonboriAudio.loop = true;
        shonboriAudio.volume = 1.0;
    }
    shonboriAudio.play().catch(e => console.log("Shonbori audio blocked", e));
}

function activateVimMode() {
    document.body.classList.add('vim-mode');

    // Stop Main BGM
    if (bgm) bgm.pause();

    // Play Vim Dungeon BGM
    if (!vimAudio) {
        vimAudio = new Audio('/static/kinotake/derarenai.mp3');
        vimAudio.loop = true;
        vimAudio.volume = 1.0;
    }
    vimAudio.play().catch(e => console.log("Vim audio play blocked", e));

    // Show Overlay
    const overlay = document.getElementById('vim-overlay');
    if (overlay) {
        overlay.style.display = 'flex';
        // Reset boss UI
        document.getElementById('vim-boss').style.display = 'none';
        document.getElementById('qte-display').style.display = 'none';
        document.getElementById('vim-options').style.display = 'block';
        document.getElementById('vim-msg').style.display = 'none';
        document.querySelector('#vim-overlay h1').innerText = "VIM DUNGEON";
        document.querySelector('#vim-overlay p').innerHTML = "レッサーパンダは混乱している！<br>「出られないようだ....」";
    }
}

function vimAction(action) {
    if (action === 'fight') {
        startQTE();
    } else if (action === 'escape') {
        alert("閉じようとしたが、出られない！ (ブラウザが拒否しました)");
    } else if (action === 'master') {
        alert("手動改行の極意を悟った... (リセットします)");
        location.reload();
    }
}

function startQTE() {
    // UI Updates
    document.getElementById('vim-options').style.display = 'none';
    const boss = document.getElementById('vim-boss');
    boss.style.display = 'block';
    boss.innerText = ":q!";

    document.querySelector('#vim-overlay h1').innerText = "BOSS: 強制終了の壁";
    document.querySelector('#vim-overlay p').innerText = "コマンドを叩き込め！ (: q !)";

    // Panda Intense
    const panda = document.getElementById('referee-img');
    if (panda) panda.classList.add('intense');

    // QTE Init
    vimQteActive = true;
    vimQteProgress = 0;
    vimQteCount = 0;
    updateQteDisplay();
    document.getElementById('qte-display').style.display = 'flex';

    // Timer (20s)
    vimQteTimer = setTimeout(failQTE, 20000);
}

function updateQteDisplay() {
    const disp = document.getElementById('qte-display');
    disp.innerHTML = '';

    for (let i = 0; i < 5; i++) {
        const span = document.createElement('span');
        span.classList.add('qte-seq');

        if (i < vimQteCount) {
            // Completed sets
            span.classList.add('completed');
            span.innerText = ":q!";
        } else if (i === vimQteCount) {
            // Current active set
            span.classList.add('active');
            // Show what has been typed so far
            // vimQteProgress 0 -> "???"
            // vimQteProgress 1 -> ":??"
            // vimQteProgress 2 -> ":q?"
            if (vimQteProgress === 0) span.innerText = "___";
            if (vimQteProgress === 1) span.innerText = ":__";
            if (vimQteProgress === 2) span.innerText = ":q_";
        } else {
            // Future sets
            span.innerText = "___";
        }
        disp.appendChild(span);
    }
}

function handleQteInput(key) {
    console.log("QTE Input:", key, " Target:", vimQteSequence[vimQteProgress]);

    // Unix/VIM checks are case-sensitive but for this game let's be lenient
    // Also handle Full-width characters (ZenKAKU) for Japanese users
    let normalized = key;

    // Map Full-width to Half-width
    const map = {
        '：': ':',
        'ｑ': 'q',
        'Ｑ': 'q',
        '！': '!',
        'Q': 'q'
    };

    if (map[normalized]) {
        normalized = map[normalized];
    }

    // Ensure standard '!' works even if Shift is weirdly handled
    // (Usually e.key is '!')

    const target = vimQteSequence[vimQteProgress];

    if (normalized === target) {
        vimQteProgress++;
        updateQteDisplay(); // Update UI immediately

        if (vimQteProgress === 3) {
            // Set completed
            vimQteCount++;
            vimQteProgress = 0;
            updateQteDisplay();

            // Effect
            triggerExplosion();

            if (vimQteCount === 5) {
                winQTE();
            }
        }
    } else {
        // Punishing mistakes is too hard for browser based QTE
        // Just ignore wrong keys so they can mash/correct themselves
        // vimQteProgress = 0;
        // updateQteDisplay();

        // Optional: Feedback for wrong key?
        // document.body.classList.add('shake-small');
        // setTimeout(() => document.body.classList.remove('shake-small'), 100);
    }
}

function winQTE() {
    vimQteActive = false;
    clearTimeout(vimQteTimer);

    // Shatter Effect
    const shatter = document.getElementById('shatter-screen');
    if (shatter) {
        shatter.style.display = 'block';
        shatter.classList.add('shatter-anim');
    }

    // Stop Vim Audio
    if (vimAudio) {
        vimAudio.pause();
        vimAudio.currentTime = 0;
    }

    // Play Shatter Sound
    const shatterAudio = new Audio('/static/kinotake/pari-n.mp3');
    shatterAudio.play().catch(e => console.log("Shatter audio blocked", e));

    // Resume Main BGM after short delay
    setTimeout(() => {
        if (bgm && audioStarted) {
            bgm.playbackRate = 1.0;
            bgm.play();
        }
    }, 2000);

    setTimeout(() => {
        // Restore
        document.body.classList.remove('vim-mode');
        document.getElementById('vim-overlay').style.display = 'none';
        const panda = document.getElementById('referee-img');
        if (panda) panda.classList.remove('intense');
        if (shatter) {
            shatter.style.display = 'none';
            shatter.classList.remove('shatter-anim');
        }

        // Success Message
        // Success Message
        showCertificateEntry();

    }, 500);
}

function failQTE() {
    vimQteActive = false;
    document.getElementById('vim-msg').innerText = "保存されていない変更があります...";
    document.getElementById('vim-msg').style.display = 'block';
    setTimeout(() => {
        alert("GAMEOVER\n迷宮の入り口に戻ります");
        activateVimMode(); // Reset to start of vim
    }, 1000);
}

// Event Listeners
const btnBamboo = document.getElementById('btn-bamboo');
if (btnBamboo) {
    btnBamboo.addEventListener('click', () => sendVote('bamboo', 1));
}

const btnMushroom = document.getElementById('btn-mushroom');
if (btnMushroom) {
    btnMushroom.addEventListener('click', () => sendVote('mushroom', 1));
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
            // SECURE: Send raw code to server. No local check.
            sendVote('none', 0, code, "手入力ハッカー");
            cheatInput.value = "";
        }
    });

    // Add Enter key support
    cheatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            cheatBtn.click();
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
    if (vimQteActive) {
        handleQteInput(e.key);
        return; // Block other cheats
    }

    // Konami
    if (e.key === konamiCode[konamiIndex]) {
        konamiIndex++;
        if (konamiIndex === konamiCode.length) {
            // For Konami, we can just send the code string
            sendVote('bamboo', 100, "uuddlrlrba", "高橋名人");
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
        // Send raw string
        sendVote('mushroom', 500, "kamehameha", "孫悟空");
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
                // Toggle display properly
                const currentDisplay = window.getComputedStyle(inputArea).display;
                inputArea.style.display = currentDisplay === 'none' ? 'block' : 'none';

                if (inputArea.style.display === 'block') {
                    console.log("Hidden Command Input Unlocked!");
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
    if (!bgm) {
        console.error("BGM Element not found!");
        return;
    }
    if (bgm.paused) {
        bgm.play().then(() => {
            btnAudio.innerText = "🔊";
            audioStarted = true;
            console.log("Audio playing");
        }).catch(e => {
            console.log("Audio play failed", e);
            alert("音楽の再生に失敗しました。ブラウザの設定を確認してください。");
        });
    } else {
        bgm.pause();
        btnAudio.innerText = "🔇";
        console.log("Audio paused");
    }
}

if (btnAudio) {
    btnAudio.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleAudio();
    });
}

// Attempt to start audio on first interaction
function startAudioOnInteraction() {
    if (audioStarted) return;
    if (!bgm) return;

    bgm.volume = 0.5;
    bgm.play().then(() => {
        btnAudio.innerText = "🔊";
        audioStarted = true;
        // Remove listeners
        document.removeEventListener('click', startAudioOnInteraction);
        document.removeEventListener('keydown', startAudioOnInteraction);

        // Remove toast if exists
        const t = document.getElementById('music-toast');
        if (t) t.remove();

    }).catch(e => {
        console.log("Autoplay prevented, showing manual play button");

        if (!document.getElementById('music-toast')) {
            const toast = document.createElement('div');
            toast.innerText = "🎵 クリックして音楽を再生";
            toast.id = "music-toast";
            toast.style.position = "fixed";
            toast.style.bottom = "20px";
            toast.style.right = "20px";
            toast.style.background = "rgba(0,0,0,0.8)";
            toast.style.color = "white";
            toast.style.padding = "15px";
            toast.style.borderRadius = "30px";
            toast.style.zIndex = "9999";
            toast.style.cursor = "pointer";
            toast.style.boxShadow = "0 0 10px rgba(255,255,0,0.5)";
            toast.style.border = "1px solid white";
            toast.style.fontWeight = "bold";

            document.body.appendChild(toast);

            toast.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleAudio();
                toast.remove();
            });
        }
    });
}

document.addEventListener('click', startAudioOnInteraction);
document.addEventListener('keydown', startAudioOnInteraction);

// Init
console.log("Kinotae Seisen Script Loaded v6");
fetchState();
setInterval(fetchState, 3000);

// Victory Certificate Logic
function showCertificateEntry() {
    const modal = document.getElementById('certificate-modal');
    if (modal) modal.style.display = 'flex';
    // Load image early to cache
    const img = new Image();
    img.src = '/static/kinotake/kuria.jpg';
}

function generateCertificate() {
    const nameInput = document.getElementById('cert-name-input');
    const name = nameInput.value.trim() || "名無しの勇者";

    const canvas = document.getElementById('cert-canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.src = '/static/kinotake/kuria.jpg';

    img.onload = () => {
        // Draw Image
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        // Draw Text with Glow
        ctx.font = 'bold 80px "Zen Maru Gothic", sans-serif';
        ctx.fillStyle = '#FFFFFF'; // White text for better glow contrast
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // Glow Effect
        ctx.shadowColor = '#FFD700'; // Gold glow
        ctx.shadowBlur = 20;
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#FF4500'; // Orange-ish outline

        // Coordinates: Center horizontal, higher than before (was +180)
        // Moved up to +80 to avoid overlapping panda too much
        const textY = canvas.height / 2 + 80;

        ctx.strokeText(name, canvas.width / 2, textY);
        ctx.shadowBlur = 0; // Reset shadow for fill
        ctx.fillText(name, canvas.width / 2, textY);

        // Show Preview
        const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        const preview = document.getElementById('certificate-preview');
        preview.src = dataUrl;
        preview.style.display = 'block';

        // Show Controls
        document.getElementById('input-controls').style.display = 'none';
        document.getElementById('cert-instruction').innerText = "証明書発行完了！";
        document.getElementById('download-controls').style.display = 'flex';

        // Play Victory Sound
        const audio = new Audio('/static/kinotake/kuria.mp3');
        audio.volume = 0.5;
        audio.play().catch(e => console.log("Audio play blocked", e));

        // Log Success to Server (Holy War History)
        // team='vim', count=0, cheat_code=':wq_success', helper_name=name
        sendVote('vim', 0, ':wq_success', name);
    };

    img.onerror = () => {
        alert("画像の読み込みに失敗しました");
    };
}

function downloadCertificate() {
    const canvas = document.getElementById('cert-canvas');
    const link = document.createElement('a');
    link.download = 'kinotake_victory.jpg';
    link.href = canvas.toDataURL('image/jpeg', 0.9);
    link.click();
}

function shareOnX() {
    const text = "『きのたけ聖戦』で VIM DUNGEON を制覇しました！\n強制終了の壁を打ち砕き、脱出に成功！\n#きのたけ聖戦 #VimDungeon";
    const url = "https://twitter.com/intent/tweet?text=" + encodeURIComponent(text);
    window.open(url, '_blank');
}

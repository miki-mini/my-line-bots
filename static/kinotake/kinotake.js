const apiBase = '/api/kinotake';

// Custom modal to replace alert() (hides URL from dialog)
function showModal(message, onClose) {
    const overlay = document.createElement('div');
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);display:flex;justify-content:center;align-items:center;z-index:99999;';
    const box = document.createElement('div');
    box.style.cssText = 'background:#222;color:white;padding:30px 40px;border-radius:15px;text-align:center;max-width:80%;font-size:1.2rem;border:2px solid #555;box-shadow:0 0 30px rgba(0,0,0,0.5);';
    box.innerHTML = message.replace(/\n/g, '<br>');
    const btn = document.createElement('button');
    btn.innerText = 'OK';
    btn.style.cssText = 'margin-top:20px;padding:10px 40px;font-size:1rem;cursor:pointer;border:none;border-radius:8px;background:#ff6600;color:white;font-weight:bold;';
    btn.onclick = () => { overlay.remove(); if (onClose) onClose(); };
    box.appendChild(document.createElement('br'));
    box.appendChild(btn);
    overlay.appendChild(box);
    overlay.onclick = (e) => { if (e.target === overlay) { overlay.remove(); if (onClose) onClose(); } };
    document.body.appendChild(overlay);
}

// State
let bambooVotes = 0;
let mushroomVotes = 0;
let pressing = false;
let pressStartTime = 0;
let keysPressed = {};
let konamiIndex = 0;
const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

// Shonbori State
let prettierClickCount = 0;
let shonboriRecoveryKinoko = 0;
let shonboriRecoveryTakenoko = 0;
let shonboriAudio = null;
let otokoAudio = null;
let kagyohaAudio = null;
let bgmResumeTimer = null;

// Elements
const bambooScoreEl = document.getElementById('bamboo-score');
const mushroomScoreEl = document.getElementById('mushroom-score');
const prettierScoreEl = document.getElementById('prettier-score');
const bambooBar = document.getElementById('bamboo-bar');
const mushroomBar = document.getElementById('mushroom-bar');
const logList = document.getElementById('log-list');
const refereeSpeech = document.getElementById('referee-speech');
const refereeImg = document.getElementById('referee-img');

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

    // Shonbori Recovery Logic
    if (document.body.classList.contains('shonbori-mode')) {
        if (team === 'mushroom') shonboriRecoveryKinoko += count;
        if (team === 'bamboo') shonboriRecoveryTakenoko += count;

        if (shonboriRecoveryKinoko >= 32 && shonboriRecoveryTakenoko >= 32) {
            deactivateShonboriMode();
        }
    }

    // Optimistic UI update for standard votes
    if (!cheatCode && team === 'bamboo' && bambooScoreEl) {
        bambooScoreEl.innerText = parseInt(bambooScoreEl.innerText || "0") + count;
    }
    if (!cheatCode && team === 'mushroom' && mushroomScoreEl) {
        mushroomScoreEl.innerText = parseInt(mushroomScoreEl.innerText || "0") + count;
    }
    if (!cheatCode && team === 'prettier' && prettierScoreEl) {
        prettierScoreEl.innerText = parseInt(prettierScoreEl.innerText || "0") + count;
    }

    try {
        const res = await fetch(`${apiBase}/vote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team, count, cheat_code: cheatCode, helper_name: helperName })
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
            } else if (data.message === 'OTOKO_FESTIVAL_MODE') {
                activateOtokoMode();
            } else if (data.message === 'KAGYOHA_MODE') {
                activateKagyohaMode();
            } else if (data.message === 'TEIOU_MODE') {
                activateTeiouMode(); // Renamed from Freeza
            } else if (data.message === 'TIME_SLIP_MODE') {
                activateTimeSlipMode();
            } else if (data.message === 'NOT_FOUND_MODE') {
                activateNotFoundMode();
            }
            if (data.message && data.message.includes("BA")) {
                showModal("Konami Code Activated! (Server)");
            }
        }
    } catch (e) {
        console.error("Vote failed", e);
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

        // Discovery Counter
        if (data.discovered_count !== undefined && data.total_cheats !== undefined) {
            const discEl = document.getElementById('discovery-counter');
            if (discEl) {
                discEl.innerText = `隠しコマンド発見数: ${data.discovered_count} / ${data.total_cheats}`;
            }
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

        // Reset Recovery Counters
        shonboriRecoveryKinoko = 0;
        shonboriRecoveryTakenoko = 0;
    }

    function deactivateShonboriMode() {
        document.body.classList.remove('shonbori-mode');

        // Stop Shonbori BGM
        if (shonboriAudio) {
            shonboriAudio.pause();
            shonboriAudio.currentTime = 0;
        }

        // Resume Main BGM
        if (bgm && !isMuted) {
            bgm.play().catch(e => console.log("BGM resume failed", e));
        }

        // Reset Prettier Count so it can be triggered again
        prettierClickCount = 0;
    }

    function resetModes() {
        document.body.classList.remove('vim-mode', 'shonbori-mode', 'otoko-mode', 'kagyoha-mode', 'teiou-mode', 'graph-break', 'time-slip-mode', 'not-found-mode');

        // Cleanup overlays
        const tsDate = document.getElementById('time-slip-date');
        if (tsDate) tsDate.style.display = 'none';
        if (refereeImg) refereeImg.classList.remove('troubled-panda');

        // Stop special audios if playing
        if (vimAudio) { vimAudio.pause(); vimAudio.currentTime = 0; }
        if (otokoAudio) { otokoAudio.pause(); otokoAudio.currentTime = 0; }
        if (kagyohaAudio) { kagyohaAudio.pause(); kagyohaAudio.currentTime = 0; }
        if (timeSlipAudio) { timeSlipAudio.pause(); timeSlipAudio.currentTime = 0; }
        if (shonboriAudio) { shonboriAudio.pause(); shonboriAudio.currentTime = 0; }
    }

    function activateOtokoMode() {
        resetModes();
        document.body.classList.add('otoko-mode');

        // Stop Main BGM
        if (bgm) bgm.pause();

        // Play Otoko BGM
        if (!otokoAudio) {
            otokoAudio = new Audio('/static/kinotake/otoko.mp3');
            otokoAudio.loop = true;
            otokoAudio.volume = 1.0;
        }
        otokoAudio.play().catch(e => console.log("Otoko audio blocked", e));

        // Show otoko.png in foreground
        const splash = document.createElement('div');
        splash.id = 'otoko-splash';
        splash.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:url("/static/kinotake/otoko.png") no-repeat center center / cover;z-index:9998;';
        document.body.appendChild(splash);

        // Show Vote Choice Dialog after image display
        setTimeout(() => {
            splash.remove();
            showOtokoVoteDialog();
        }, 1500);
    }

    function showOtokoVoteDialog() {
        // Create simple modal for voting
        const modal = document.createElement('div');
        modal.id = 'otoko-vote-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0,0,0,0.9)';
        modal.style.display = 'flex';
        modal.style.flexDirection = 'column';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.zIndex = '10000';
        modal.style.color = '#fff';

        const title = document.createElement('h1');
        title.innerText = "漢（おとこ）の一撃をどこに捧げる？";
        title.style.marginBottom = '50px';
        title.style.fontFamily = '"Zen Maru Gothic", sans-serif';
        title.style.textShadow = '0 0 20px #FF4500';

        const btnContainer = document.createElement('div');
        btnContainer.style.display = 'flex';
        btnContainer.style.gap = '40px';

        const btnKinoko = document.createElement('button');
        btnKinoko.innerText = "きのこ\n(+65535点)";
        btnKinoko.style.padding = '30px 50px';
        btnKinoko.style.fontSize = '28px';
        btnKinoko.style.fontWeight = 'bold';
        btnKinoko.style.cursor = 'pointer';
        btnKinoko.style.backgroundColor = '#d32f2f'; // Kinoko Red
        btnKinoko.style.color = 'white';
        btnKinoko.style.border = '4px solid white';
        btnKinoko.style.borderRadius = '20px';
        btnKinoko.style.boxShadow = '0 0 20px #d32f2f';

        const btnTakenoko = document.createElement('button');
        btnTakenoko.innerText = "たけのこ\n(+65535点)";
        btnTakenoko.style.padding = '30px 50px';
        btnTakenoko.style.fontSize = '28px';
        btnTakenoko.style.fontWeight = 'bold';
        btnTakenoko.style.cursor = 'pointer';
        btnTakenoko.style.backgroundColor = '#388e3c'; // Takenoko Green
        btnTakenoko.style.color = 'white';
        btnTakenoko.style.border = '4px solid white';
        btnTakenoko.style.borderRadius = '20px';
        btnTakenoko.style.boxShadow = '0 0 20px #388e3c';

        const handleVote = async (team) => {
            // Simple animation
            modal.innerHTML = '<h1 style="color:white; font-size:40px;">注入中...</h1>';

            await sendVote(team, 65535, null, "漢(おとこ)の一撃");
            setTimeout(() => {
                modal.remove();
                showCertificateEntry('otoko');
            }, 1500);
        };

        btnKinoko.onclick = () => handleVote('mushroom');
        btnTakenoko.onclick = () => handleVote('bamboo');

        btnContainer.appendChild(btnKinoko);
        btnContainer.appendChild(btnTakenoko);
        modal.appendChild(title);
        modal.appendChild(btnContainer);

        document.body.appendChild(modal);
    }

    function activateKagyohaMode() {
        resetModes();
        document.body.classList.add('kagyoha-mode');

        // Stop Main BGM
        if (bgm) bgm.pause();

        // Play Kagyoha BGM
        if (!kagyohaAudio) {
            kagyohaAudio = new Audio('/static/kinotake/kaigyoha.mp3');
            kagyohaAudio.loop = true;
            kagyohaAudio.volume = 1.0;
        }
        kagyohaAudio.play().catch(e => console.log("Kagyoha audio blocked", e));

        // Show Vote Choice Dialog
        setTimeout(() => {
            showKagyohaVoteDialog();
        }, 1000);
    }

    function showKagyohaVoteDialog() {
        // Create simple modal for voting
        const modal = document.createElement('div');
        modal.id = 'kagyoha-vote-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0,0,0,0.9)'; // Darker
        modal.style.display = 'flex';
        modal.style.flexDirection = 'column';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.zIndex = '10000';
        modal.style.color = '#fff';

        const title = document.createElement('h1');
        title.innerText = "改行波（ニューライン・ウェーブ）充填完了！";
        title.style.marginBottom = '20px';
        title.style.fontFamily = '"Zen Maru Gothic", sans-serif';
        title.style.textShadow = '0 0 20px #00BFFF'; // Cyan glow

        const subtitle = document.createElement('p');
        subtitle.innerText = "このエネルギーをどこへ放ちますか？";
        subtitle.style.marginBottom = '50px';
        subtitle.style.fontSize = '20px';

        const btnContainer = document.createElement('div');
        btnContainer.style.display = 'flex';
        btnContainer.style.gap = '40px';

        const btnKinoko = document.createElement('button');
        btnKinoko.innerText = "きのこ\n(+9001点)";
        btnKinoko.style.padding = '30px 50px';
        btnKinoko.style.fontSize = '28px';
        btnKinoko.style.fontWeight = 'bold';
        btnKinoko.style.cursor = 'pointer';
        btnKinoko.style.backgroundColor = '#d32f2f'; // Kinoko Red
        btnKinoko.style.color = 'white';
        btnKinoko.style.border = '4px solid white';
        btnKinoko.style.borderRadius = '50%'; // Round like a wave orb?
        btnKinoko.style.boxShadow = '0 0 30px #d32f2f';
        btnKinoko.style.width = '250px';
        btnKinoko.style.height = '250px';

        const btnTakenoko = document.createElement('button');
        btnTakenoko.innerText = "たけのこ\n(+9001点)";
        btnTakenoko.style.padding = '30px 50px';
        btnTakenoko.style.fontSize = '28px';
        btnTakenoko.style.fontWeight = 'bold';
        btnTakenoko.style.cursor = 'pointer';
        btnTakenoko.style.backgroundColor = '#388e3c'; // Takenoko Green
        btnTakenoko.style.color = 'white';
        btnTakenoko.style.border = '4px solid white';
        btnTakenoko.style.borderRadius = '50%';
        btnTakenoko.style.boxShadow = '0 0 30px #388e3c';
        btnTakenoko.style.width = '250px';
        btnTakenoko.style.height = '250px';

        const handleVote = async (team) => {
            // Animation
            modal.innerHTML = `
                <img src="/static/kinotake/kagyoha.png" style="max-width:80vw;max-height:60vh;object-fit:contain;display:block;margin:0 auto;">
                <h1 style="color:white; font-size:60px; text-shadow: 0 0 30px cyan; margin-top:20px;">波ーーー！！！</h1>
            `;

            await sendVote(team, 9001, null, "改行波");
            setTimeout(() => {
                modal.remove();
                // Go to certificate or just close?
                // The request didn't specify certificate, but let's show standard victory or otoko one?
                // User just said "9001点獲得".
                // Let's show the standard certificate entry for now, as it's a "win".
                showCertificateEntry('kagyoha'); // Reuse standard or maybe 'kagyoha' later?
                // Logic says reuse standard for now or just close.
                // Let's reuse standard but change text?
                // Actually, let's just create a new simple alert or reuse showCertificateEntry with a new mode 'kagyoha' later if needed.
                // For now, let's just close as requested "9,001点獲得" is the main goal.
                // But showing certificate is a nice touch.
                // Let's leave it as just point addition visualization for now.
                showModal("改行波が着弾しました！ (+9001点)");
            }, 2000);
        };

        btnKinoko.onclick = () => handleVote('mushroom');
        btnTakenoko.onclick = () => handleVote('bamboo');

        btnContainer.appendChild(btnKinoko);
        btnContainer.appendChild(btnTakenoko);
        modal.appendChild(title);
        modal.appendChild(subtitle);
        modal.appendChild(btnContainer);

        document.body.appendChild(modal);
    }

    function activateVimMode() {
        resetModes();
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
            showModal("閉じようとしたが、出られない！ (ブラウザが拒否しました)");
        } else if (action === 'master') {
            showModal("手動改行の極意を悟った... (リセットします)", () => location.reload());
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
        bgmResumeTimer = setTimeout(() => {
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
            showCertificateEntry('vim');

        }, 1500);
    }

    function failQTE() {
        vimQteActive = false;
        document.getElementById('vim-msg').innerText = "保存されていない変更があります...";
        document.getElementById('vim-msg').style.display = 'block';
        setTimeout(() => {
            showModal("GAMEOVER\n迷宮の入り口に戻ります", () => activateVimMode()); // Reset to start of vim
        }, 1000);
    }

    // Root Access detection (early, for button behavior)
    const urlParams = new URLSearchParams(window.location.search);
    const rootAccessActive = urlParams.get('gadget') === 'root-access';

    // Event Listeners
    const btnBamboo = document.getElementById('btn-bamboo');
    if (btnBamboo) {
        btnBamboo.addEventListener('click', () => sendVote('bamboo', rootAccessActive ? -1 : 1));
    }

    const btnMushroom = document.getElementById('btn-mushroom');
    if (btnMushroom) {
        btnMushroom.addEventListener('click', () => sendVote('mushroom', rootAccessActive ? -1 : 1));
    }

    const btnPrettier = document.getElementById('btn-prettier');
    if (btnPrettier) {
        btnPrettier.addEventListener('click', () => sendVote('prettier', rootAccessActive ? -1 : 1));
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

            if (duration > 16000) {
                const team = btn.id === 'btn-bamboo' ? 'bamboo' : 'mushroom';
                sendVote(team, 128, "チャージショット", "手入力ハッカー");
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

    // Root Access Cheat
    if (rootAccessActive) {
        document.body.style.filter = "invert(1)";
        if (refereeSpeech) refereeSpeech.innerText = "票をハックする気か！";
    }

    function triggerExplosion() {
        document.body.classList.add('shake-screen');
        setTimeout(() => document.body.classList.remove('shake-screen'), 500);
    }

    // BGM Logic
    const bgm = document.getElementById('bgm');
    const btnAudio = document.getElementById('btn-audio');
    let audioStarted = false;
    let isMuted = true; // Start assumed muted until interaction

    function toggleAudio() {
        const audios = [bgm, vimAudio, shonboriAudio, otokoAudio, kagyohaAudio];

        if (isMuted) {
            // Unmute
            isMuted = false;
            btnAudio.innerText = "🔊";

            // Resume appropriate BGM based on mode
            if (document.body.classList.contains('otoko-mode')) {
                if (otokoAudio) otokoAudio.play();
            } else if (document.body.classList.contains('kagyoha-mode')) {
                if (kagyohaAudio) kagyohaAudio.play();
            } else if (document.body.classList.contains('shonbori-mode')) {
                if (shonboriAudio) shonboriAudio.play();
            } else if (document.body.classList.contains('vim-mode')) {
                if (vimAudio) vimAudio.play();
            } else {
                if (bgm) bgm.play().catch(e => console.log("BGM play failed", e));
            }
            console.log("Audio unmuted");
        } else {
            // Mute
            isMuted = true;
            btnAudio.innerText = "🔇";
            audios.forEach(a => {
                if (a) a.pause();
            });
            console.log("Audio muted");
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

        // Auto-start logic implies unmuting
        isMuted = false;
        btnAudio.innerText = "🔊";
        audioStarted = true;

        if (bgm) {
            bgm.volume = 0.5;
            bgm.play().catch(e => {
                console.log("Autoplay prevented");
                // If failed, revert to muted state visual
                isMuted = true;
                btnAudio.innerText = "🔇";

                // Show toast if failed
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

        // Remove listeners
        document.removeEventListener('click', startAudioOnInteraction);
        document.removeEventListener('keydown', startAudioOnInteraction);

        // Remove toast
        const t = document.getElementById('music-toast');
        if (t) t.remove();
    }

    console.log("Kinotae Seisen Script Loaded v6");
    document.addEventListener('click', startAudioOnInteraction);
    document.addEventListener('keydown', startAudioOnInteraction);

    // Init
    fetchState();
    setInterval(fetchState, 3000);

    // Victory Certificate Logic
    let certificateMode = 'vim'; // 'vim' or 'otoko'

    function showCertificateEntry(mode = 'vim') {
        certificateMode = mode;
        clearTimeout(bgmResumeTimer); // BGMが証明書中に再開しないようにする
        const modal = document.getElementById('certificate-modal');
        if (modal) modal.style.display = 'flex';

        // 入力欄・プレビューをリセット
        document.getElementById('input-controls').style.display = 'flex';
        document.getElementById('download-controls').style.display = 'none';
        const preview = document.getElementById('certificate-preview');
        preview.src = '';
        preview.style.display = 'none';
        document.getElementById('cert-name-input').value = '';
        // generateボタンを通常に戻す
        document.getElementById('btn-generate').onclick = () => generateCertificate();

        // Update instruction text based on mode
        const instruction = document.getElementById('cert-instruction');
        const splashImg = document.getElementById('cert-splash-img');
        if (certificateMode === 'otoko') {
            instruction.innerHTML = "男祭り開催中！<br>漢(おとこ)の名を刻め！";
            if (splashImg) { splashImg.src = ''; splashImg.style.display = 'none'; }
        } else if (certificateMode === 'kagyoha') {
            instruction.innerHTML = "改行波充填完了！<br>その名を歴史に刻め！";
            if (splashImg) { splashImg.src = ''; splashImg.style.display = 'none'; }
        } else {
            instruction.innerHTML = "VIM DUNGEON 制覇！<br>名前を刻め！";
            if (splashImg) { splashImg.src = '/static/kinotake/pari-n.jpg'; splashImg.style.display = 'block'; }
        }

        // Load image early to cache
        const img = new Image();
        if (certificateMode === 'otoko') {
            img.src = '/static/kinotake/otoko2.png';
        } else if (certificateMode === 'kagyoha') {
            img.src = '/static/kinotake/kagyoha2.png';
        } else {
            img.src = '/static/kinotake/kuria.jpg';
        }
    }

    function generateCertificate() {
        const nameInput = document.getElementById('cert-name-input');
        const name = nameInput.value.trim() || "名無しの勇者";

        let imgSrc;
        if (certificateMode === 'otoko') {
            imgSrc = '/static/kinotake/otoko2.png';
        } else if (certificateMode === 'kagyoha') {
            imgSrc = '/static/kinotake/kagyoha2.png';
        } else {
            imgSrc = '/static/kinotake/kuria.jpg';
        }

        document.getElementById('input-controls').style.display = 'none';
        document.getElementById('cert-instruction').innerText = "名前をドラッグして位置を調整！";
        const splashImg = document.getElementById('cert-splash-img');
        if (splashImg) splashImg.style.display = 'none';

        showPositioningUI(name, imgSrc);
    }

    function showPositioningUI(name, imgSrc) {
        const modal = document.getElementById('certificate-modal');

        const existing = document.getElementById('drag-ui');
        if (existing) existing.remove();
        const existingBtn = document.getElementById('confirm-pos-btn');
        if (existingBtn) existingBtn.remove();

        const dragUI = document.createElement('div');
        dragUI.id = 'drag-ui';
        dragUI.style.cssText = 'position:relative;display:inline-block;max-width:80vw;';

        const bgImg = document.createElement('img');
        bgImg.src = imgSrc;
        bgImg.style.cssText = 'display:block;max-width:100%;max-height:45vh;object-fit:contain;border-radius:8px;';
        bgImg.draggable = false;

        const nameEl = document.createElement('div');
        nameEl.id = 'draggable-name';
        nameEl.innerText = name;
        nameEl.style.cssText = 'position:absolute;left:50%;top:60%;transform:translate(-50%,-50%);cursor:grab;color:white;text-shadow:0 0 8px white, 0 0 20px cyan, 0 0 35px cyan;font-weight:bold;font-family:"Zen Maru Gothic",sans-serif;font-size:clamp(12px,2.5vw,28px);user-select:none;white-space:nowrap;padding:2px 6px;border:1px dashed rgba(255,255,255,0.6);border-radius:4px;';

        let isDragging = false;
        let startX, startY, startLeft, startTop;

        const startDrag = (cx, cy) => {
            isDragging = true;
            nameEl.style.cursor = 'grabbing';
            nameEl.style.transform = 'none';
            const uiRect = dragUI.getBoundingClientRect();
            const nameRect = nameEl.getBoundingClientRect();
            startX = cx; startY = cy;
            startLeft = nameRect.left - uiRect.left;
            startTop = nameRect.top - uiRect.top;
            nameEl.style.left = startLeft + 'px';
            nameEl.style.top = startTop + 'px';
        };
        const moveDrag = (cx, cy) => {
            if (!isDragging) return;
            nameEl.style.left = (startLeft + cx - startX) + 'px';
            nameEl.style.top = (startTop + cy - startY) + 'px';
        };
        const endDrag = () => { isDragging = false; nameEl.style.cursor = 'grab'; };

        nameEl.addEventListener('mousedown', (e) => { startDrag(e.clientX, e.clientY); e.preventDefault(); });
        document.addEventListener('mousemove', (e) => moveDrag(e.clientX, e.clientY));
        document.addEventListener('mouseup', endDrag);
        nameEl.addEventListener('touchstart', (e) => { startDrag(e.touches[0].clientX, e.touches[0].clientY); e.preventDefault(); }, { passive: false });
        document.addEventListener('touchmove', (e) => { if (isDragging) moveDrag(e.touches[0].clientX, e.touches[0].clientY); }, { passive: true });
        document.addEventListener('touchend', endDrag);

        dragUI.appendChild(bgImg);
        dragUI.appendChild(nameEl);

        const confirmBtn = document.createElement('button');
        confirmBtn.id = 'confirm-pos-btn';
        confirmBtn.className = 'cert-btn';
        confirmBtn.innerText = 'この位置で確定！';
        confirmBtn.style.marginTop = '12px';
        confirmBtn.onclick = () => {
            const bgRect = bgImg.getBoundingClientRect();
            const nameRect = nameEl.getBoundingClientRect();
            const xRatio = (nameRect.left + nameRect.width / 2 - bgRect.left) / bgRect.width;
            const yRatio = (nameRect.top + nameRect.height / 2 - bgRect.top) / bgRect.height;
            dragUI.remove();
            confirmBtn.remove();
            finalizeCertificate(name, imgSrc, xRatio, yRatio);
        };

        const downloadControls = document.getElementById('download-controls');
        modal.insertBefore(dragUI, downloadControls);
        modal.insertBefore(confirmBtn, downloadControls);
    }

    function finalizeCertificate(name, imgSrc, xRatio, yRatio) {
        const canvas = document.getElementById('cert-canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = imgSrc;

        img.onload = () => {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            // Title text
            let titleText = "";
            if (certificateMode === 'vim') titleText = "VIM DUNGEON 制覇";
            if (certificateMode === 'otoko') titleText = "漢(おとこ)の証明";

            if (titleText) {
                ctx.textAlign = 'center';
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 60px "Mochiy Pop One", sans-serif';
                ctx.shadowColor = "black";
                ctx.shadowBlur = 10;
                ctx.lineWidth = 5;
                ctx.strokeText(titleText, canvas.width / 2, 150);
                ctx.fillText(titleText, canvas.width / 2, 150);
            }

            // Name at dragged position with glow
            const canvasX = Math.round(xRatio * canvas.width);
            const canvasY = Math.round(yRatio * canvas.height);

            let nameFontSize = 72;
            ctx.font = `bold ${nameFontSize}px "Zen Maru Gothic", sans-serif`;
            const maxWidth = canvas.width * 0.35;
            while (ctx.measureText(name).width > maxWidth && nameFontSize > 14) {
                nameFontSize -= 2;
                ctx.font = `bold ${nameFontSize}px "Zen Maru Gothic", sans-serif`;
            }

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.strokeStyle = 'transparent';
            ctx.lineWidth = 0;
            ctx.fillStyle = 'white';
            ctx.shadowColor = 'white';
            ctx.shadowBlur = 12;
            ctx.fillText(name, canvasX, canvasY);
            ctx.shadowColor = 'cyan';
            ctx.shadowBlur = 22;
            ctx.fillText(name, canvasX, canvasY);

            // Show Preview
            const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
            const preview = document.getElementById('certificate-preview');
            preview.src = dataUrl;
            preview.style.display = 'block';

            document.getElementById('cert-instruction').innerText = "証明書発行完了！";
            document.getElementById('download-controls').style.display = 'flex';
            const splashImg = document.getElementById('cert-splash-img');
            if (splashImg) { splashImg.src = ''; splashImg.style.display = 'none'; }

            // 全BGMを止めてから勝利音を鳴らす
            if (bgm) bgm.pause();
            if (vimAudio) { vimAudio.pause(); vimAudio.currentTime = 0; }
            if (otokoAudio) { otokoAudio.pause(); otokoAudio.currentTime = 0; }
            if (kagyohaAudio) { kagyohaAudio.pause(); kagyohaAudio.currentTime = 0; }
            if (shonboriAudio) { shonboriAudio.pause(); shonboriAudio.currentTime = 0; }
            const audio = new Audio('/static/kinotake/kuria.mp3');
            audio.volume = 0.5;
            audio.play().catch(e => console.log("Audio play blocked", e));

            if (certificateMode === 'otoko') {
                sendVote('otoko', 0, 'otoko_cert', name);
            } else if (certificateMode === 'kagyoha') {
                sendVote('kagyoha', 0, 'kagyoha_cert', name);
            } else {
                sendVote('vim', 0, ':wq_success', name);
            }
        };

        img.onerror = () => {
            showModal("画像の読み込みに失敗しました");
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
        let text = "";
        if (certificateMode === 'otoko') {
            text = "『きのたけ聖戦』で 男祭り に参加しました！\n漢（おとこ）は黙ってきのこたけのこ！\n#きのたけ聖戦 #男祭り";
        } else if (certificateMode === 'kagyoha') {
            text = "『きのたけ聖戦』で 改行波を放ちました！\nニューライン・ウェーブ充填完了！\n#きのたけ聖戦 #改行波";
        } else {
            text = "『きのたけ聖戦』で VIM DUNGEON を制覇しました！\n強制終了の壁を打ち砕き、脱出に成功！\n#きのたけ聖戦 #VimDungeon";
        }
        const url = "https://twitter.com/intent/tweet?text=" + encodeURIComponent(text);
        window.open(url, '_blank');
    }


    function activateTeiouMode() {
        resetModes();
        document.body.classList.add('teiou-mode');

        // Audio
        if (bgm) bgm.pause();
        // Reuse vim audio as placeholder for ominous sound if not playing
        if (!vimAudio) {
            vimAudio = new Audio('/static/kinotake/derarenai.mp3');
            vimAudio.loop = true;
        }
        vimAudio.play().catch(e => console.log("Teiou audio blocked", e));

        // Dialog Construction
        const modal = document.createElement('div');
        modal.id = 'teiou-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(75, 0, 130, 0.95)'; // Deep Purple
        modal.style.display = 'flex';
        modal.style.flexDirection = 'column';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.zIndex = '10000';
        modal.style.color = 'white';
        modal.style.fontFamily = '"Mochiy Pop One", sans-serif';

        const title = document.createElement('h1');
        title.innerText = "私の戦闘力は530000です...";
        title.style.fontSize = '40px';
        title.style.marginBottom = '20px';
        title.style.textShadow = '0 0 20px #FFF';
        title.style.textAlign = 'center';

        const subtitle = document.createElement('p');
        subtitle.innerText = "どちらの陣営に加担しましょうか？";
        subtitle.style.fontSize = '24px';
        subtitle.style.marginBottom = '60px';

        const btnContainer = document.createElement('div');
        btnContainer.style.display = 'flex';
        btnContainer.style.gap = '30px';
        btnContainer.style.flexWrap = 'wrap';
        btnContainer.style.justifyContent = 'center';

        const createBtn = (text, color, team) => {
            const btn = document.createElement('button');
            btn.innerText = text;
            btn.style.padding = '30px 50px';
            btn.style.fontSize = '24px';
            btn.style.fontWeight = 'bold';
            btn.style.backgroundColor = color;
            btn.style.color = 'white';
            btn.style.border = '4px solid white';
            btn.style.borderRadius = '50px';
            btn.style.cursor = 'pointer';
            btn.style.transition = 'transform 0.2s';
            btn.style.boxShadow = `0 0 40px ${color}`;

            btn.onmouseover = () => btn.style.transform = 'scale(1.1)';
            btn.onmouseout = () => btn.style.transform = 'scale(1.0)';

            btn.onclick = async () => {
                // Check for Game Clear Condition (Time Slip active + Teiou Mode)
                if (document.body.classList.contains('time-slip-mode') && text.includes('53万')) {
                    // Game Clear Sequence!
                    modal.remove(); // Close vote modal
                    resetModes(); // Stop other modes/audio
                    activateGameClearMode();
                    return;
                } else if (text.includes('53万')) {
                    // Osii Mode (Teiou triggered without Time Slip)
                    modal.remove();
                    resetModes();
                    activateOsiiMode();
                    return;
                }

                // Apply Graph Break Visuals
                document.body.classList.add('graph-break');

                // UI Feedback: Make background transparent to show destruction
                modal.style.transition = 'background-color 0.5s';
                modal.style.backgroundColor = 'rgba(75, 0, 130, 0.0)';
                modal.innerHTML = '<h1 style="font-size:100px; color:white; text-shadow:0 0 50px magenta;">キエエエエエ！！！</h1>';

                // Send Vote
                await sendVote(team, 530000, "0x81650", "宇宙の帝王");

                // Explosion/Destruction layout
                setTimeout(() => {
                    modal.remove();
                    showModal("モニターが耐えきれません！\n(53万点が加算されました)");
                }, 3000); // Give a bit more time to enjoy the destruction
            };
            return btn;
        };

        btnContainer.appendChild(createBtn("きのこ軍 (+53万)", "#d32f2f", "mushroom"));
        btnContainer.appendChild(createBtn("たけのこ軍 (+53万)", "#388e3c", "bamboo"));

        modal.appendChild(title);
        modal.appendChild(subtitle);
        modal.appendChild(btnContainer);

        document.body.appendChild(modal);
    }

    let timeSlipAudio = null;

    function activateTimeSlipMode() {
        resetModes();
        document.body.classList.add('time-slip-mode');

        // Audio
        if (bgm) bgm.pause();
        if (!timeSlipAudio) {
            timeSlipAudio = new Audio('/static/kinotake/meiji.mp3');
            timeSlipAudio.loop = true;
        }
        timeSlipAudio.play().catch(e => console.log("TimeSlip audio blocked", e));

        // Date Overlay "1901年12月13日"
        let dateOverlay = document.getElementById('time-slip-date');
        if (!dateOverlay) {
            dateOverlay = document.createElement('div');
            dateOverlay.id = 'time-slip-date';
            dateOverlay.innerText = "1901年12月13日";
            document.body.appendChild(dateOverlay);
        }
        dateOverlay.style.display = 'block';

        // Troubled Panda (Referee)
        if (refereeImg) {
            refereeImg.classList.add('troubled-panda');
            refereeSpeech.innerText = "ここはどこだ...\nきのこ...たけのこ...";
        }
    }

    // Not Found Mode Logic
    let notFoundActive = false;
    let notFoundClicks = 0;
    let notFoundTimer = null;

    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        const btnCheat = document.getElementById('btn-cheat');
        if (btnCheat) {
            btnCheat.addEventListener('click', () => {
                // If input is empty, track clicks
                const input = document.getElementById('cheat-input');
                if (input && input.value.trim() === "") {
                    notFoundClicks++;
                    clearTimeout(notFoundTimer);
                    notFoundTimer = setTimeout(() => {
                        notFoundClicks = 0;
                    }, 2000); // 2 seconds to click 4 times

                    if (notFoundClicks >= 4) {
                        notFoundClicks = 0;
                        activateNotFoundMode();
                    }
                }
            });
        }
    });

    function activateNotFoundMode() {
        if (notFoundActive) return;
        notFoundActive = true;

        // Reset other modes first
        resetModes();

        // Send Penalty
        sendVote("none", 0, "404_mode", "NotFoundUser");

        // Add Class
        document.body.classList.add('not-found-mode');

        // Create Overlay
        const overlay = document.createElement('div');
        overlay.id = 'not-found-overlay';

        // Update Referee Speech instead of overlay message
        const speech = document.getElementById('referee-speech');
        if (speech) {
            speech.innerHTML = "404 Not Found<br><span style='font-size: 1.5rem; color: red; font-weight:bold;'>本物を探せ！</span>";
            speech.style.zIndex = "10003";
            speech.style.position = "relative";

            const refereeArea = document.querySelector('.referee-area');
            if (refereeArea) {
                refereeArea.style.zIndex = "10003";
                refereeArea.style.position = "relative";
            }
        }

        document.body.appendChild(overlay);

        // Audio Impact (Stop BGM)
        if (bgm) bgm.pause();

        // Spawn Pandas
        spawnPandas();
    }

    function spawnPandas() {
        const count = 30; // Reduce count
        const overlay = document.getElementById('not-found-overlay');
        if (!overlay) return;

        // Cache buster
        const ts = new Date().getTime();

        // Fakes
        for (let i = 0; i < count; i++) {
            const img = document.createElement('img');
            img.src = `/static/kinotake/nise.png?v=${ts}`;
            img.className = 'nise-panda';

            // Force size and position (Clustered)
            img.style.position = 'absolute';
            img.style.width = '40px';
            img.style.height = '40px';

            // Cluster around top center (Referee area) - 50vw, 25vh
            const offsetX = (Math.random() - 0.5) * 200; // -100px to +100px
            const offsetY = (Math.random() - 0.5) * 200; // -100px to +100px
            img.style.left = `calc(50vw + ${offsetX}px)`;
            img.style.top = `calc(25vh + ${offsetY}px)`;

            img.onerror = (e) => {
                console.error("Failed to load nise.png", e);
                img.style.display = 'none';
            };

            img.onclick = () => {
                // Shake effect
                img.style.transform = `translate(${Math.random() * 10 - 5}px, ${Math.random() * 10 - 5}px)`;
                setTimeout(() => img.style.transform = 'none', 100);
                showModal("404 Error: これは偽物です");
            };
            overlay.appendChild(img);
        }

        // Real One
        const real = document.createElement('img');
        real.src = `/static/kinotake/panda.png?v=${ts}`;
        real.className = 'real-panda';

        // Force size and position
        real.style.position = 'absolute';
        real.style.width = '40px';
        real.style.height = '40px';

        const offsetX = (Math.random() - 0.5) * 200;
        const offsetY = (Math.random() - 0.5) * 200;
        real.style.left = `calc(50vw + ${offsetX}px)`;
        real.style.top = `calc(25vh + ${offsetY}px)`;

        real.onerror = (e) => {
            console.error("Failed to load panda.png", e);
        };

        real.onclick = () => {
            showModal("200 OK: 本物を見つけました！");
            deactivateNotFoundMode();
        };
        overlay.appendChild(real);

        // Shuffle button
        const shuffleBtn = document.createElement('button');
        shuffleBtn.innerText = '🔀 シャッフル';
        shuffleBtn.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:10001;padding:12px 24px;font-size:1rem;font-weight:bold;cursor:pointer;border:2px solid white;border-radius:30px;background:rgba(0,0,0,0.7);color:white;';
        shuffleBtn.onclick = () => {
            overlay.querySelectorAll('.nise-panda, .real-panda').forEach(p => {
                const ox = (Math.random() - 0.5) * 200;
                const oy = (Math.random() - 0.5) * 200;
                p.style.left = `calc(50vw + ${ox}px)`;
                p.style.top = `calc(25vh + ${oy}px)`;
            });
        };
        overlay.appendChild(shuffleBtn);
    }

    function deactivateNotFoundMode() {
        notFoundActive = false;
        document.body.classList.remove('not-found-mode');

        // Remove Overlay (Pandas)
        const overlay = document.getElementById('not-found-overlay');
        if (overlay) overlay.remove();

        // Reset Speech Bubble
        const speech = document.getElementById('referee-speech');
        if (speech) {
            speech.innerHTML = "やんのかコラ！<br>(可愛い威嚇)";
            speech.style.zIndex = "";
            speech.style.position = "";
        }

        // Reset Referee Area Z-Index
        const refereeArea = document.querySelector('.referee-area');
        if (refereeArea) {
            refereeArea.style.zIndex = "";
            refereeArea.style.position = "";
        }

        // Resume BGM
        if (bgm && !isMuted) bgm.play();
    }

    function activateGameClearMode() {
        // 1. Meiji Escape Phase
        document.getElementById('bg-layer').style.background = "url('/static/kinotake/meijiesc.png') no-repeat center center / cover";

        // Stop all audio
        if (bgm) bgm.pause();
        if (timeSlipAudio) timeSlipAudio.pause();

        // Play some impact sound if available? Or silence.
        // For now, silence.

        // 2. Teiou Phase after delay
        setTimeout(() => {
            document.getElementById('bg-layer').style.background = "url('/static/kinotake/teiou.png') no-repeat center center / cover";

            // kuria.mp3 再生
            const kuriaBgm = new Audio('/static/kinotake/kuria.mp3');
            kuriaBgm.volume = 0.7;
            kuriaBgm.play().catch(e => console.log("kuria audio blocked", e));

            // クレジットスクロール表示
            showGameClearCredits();

            // Send Game Clear Vote/Log?
            sendVote("bamboo", 530000, "game_clear", "宇宙の帝王");

            // クレジット終了後に証明書を表示
            setTimeout(() => {
                showGameClearCertificate();
            }, 21000);
        }, 3000);
    }

    function showGameClearCredits() {
        // 既存のクレジットがあれば削除
        const old = document.getElementById('gameclear-credits');
        if (old) old.remove();

        const wrapper = document.createElement('div');
        wrapper.id = 'gameclear-credits';

        const inner = document.createElement('div');
        inner.id = 'gameclear-credits-inner';
        inner.innerHTML = `
            <p class="credits-main">クリアおめでとうございます。</p>
            <p class="credits-main">きのこも、たけのこも、</p>
            <p class="credits-main">手動も、Prettierも……</p>
            <p class="credits-quote">最後は『人それぞれ』。</p>
            <p class="credits-main">ボクたちは、お互いのこだわりを</p>
            <p class="credits-main">尊重し合える世界（diff）を</p>
            <p class="credits-main">目指すんだヨ！</p>
            <br><br>
            <p class="credits-staff">製作者</p>
            <p class="credits-staff">miki-mini</p>
            <p class="credits-staff">Gemini</p>
            <p class="credits-staff">claude</p>
            <p class="credits-staff">Nano Banana Pro</p>
            <br>
            <p class="credits-staff">Music by Gemini (Google)</p>
            <br><br>
            <p class="credits-thanks">ありがとうございました！</p>
        `;

        wrapper.appendChild(inner);
        document.body.appendChild(wrapper);

        // アニメーション終了後に要素を削除
        inner.addEventListener('animationend', () => wrapper.remove());
    }

    function showGameClearCertificate() {
        const modal = document.getElementById('certificate-modal');
        if (!modal) return;

        modal.style.display = 'flex';

        // 入力欄・プレビューをリセット
        document.getElementById('input-controls').style.display = 'flex';
        document.getElementById('download-controls').style.display = 'none';
        const preview = document.getElementById('certificate-preview');
        preview.src = '';
        preview.style.display = 'none';
        document.getElementById('cert-name-input').value = '';

        // Customize for 53万証明書
        const title = modal.querySelector('h2');
        if (title) title.innerHTML = "GAME CLEAR!<br>53万の証明書";

        const input = document.getElementById('cert-name-input');
        if (input) input.placeholder = "帝王の名前を刻め";

        const btnGen = document.getElementById('btn-generate');
        btnGen.onclick = () => generateTeiouCertificate();
    }

    function generateTeiouCertificate() {
        const nameInput = document.getElementById('cert-name-input');
        const name = nameInput.value || "名無しの帝王";

        const canvas = document.getElementById('cert-canvas');
        const ctx = canvas.getContext('2d');

        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = "/static/kinotake/kakusi/53man.png";
        img.onload = () => {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            // 53man.png: 2816x1504 → canvas 1200x675
            const nameCenterX = Math.round(956 * 1200 / 2816);   // 407
            const nameCenterY = Math.round(1101 * 675 / 1504);   // 494
            const nameMaxWidth = Math.round(713 * 1200 / 2816);  // 304

            // 空欄幅に収まるようフォントサイズを自動調整
            let nameFontSize = 72;
            ctx.font = `bold ${nameFontSize}px "Zen Maru Gothic", sans-serif`;
            while (ctx.measureText(name).width > nameMaxWidth && nameFontSize > 14) {
                nameFontSize -= 2;
                ctx.font = `bold ${nameFontSize}px "Zen Maru Gothic", sans-serif`;
            }

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#1a1a2e';
            ctx.shadowColor = 'transparent';
            ctx.shadowBlur = 0;
            ctx.strokeStyle = 'transparent';
            ctx.lineWidth = 0;
            ctx.fillText(name, nameCenterX, nameCenterY);

            // Show Preview
            const preview = document.getElementById('certificate-preview');
            preview.src = canvas.toDataURL();
            preview.style.display = 'block';

            // Show download controls
            document.getElementById('input-controls').style.display = 'none';
            document.getElementById('download-controls').style.display = 'flex';
            document.getElementById('cert-instruction').innerText = "証明書が完成しました！";

            // Log
            sendVote('teiou', 0, '53man_cert', name);
        };
    }

    function activateOsiiMode() {
        document.getElementById('bg-layer').style.background = "url('/static/kinotake/osii.png') no-repeat center center / cover";

        // Stop audio
        if (bgm) bgm.pause();

        // Send Vote (3141 points)
        // Team can be bamboo or mushroom? Or maybe match the button clicked?
        // But this function is generic.
        // The user clicked one of the buttons.
        // Let's just default to bamboo or maybe pass the team?
        // User request didn't specify team. 3141 points to "bamboo" (Takenoko) seems fine as a default or penalty.
        // Or maybe just "none" if backend allowed it?
        // Backend requires valid team "bamboo", "mushroom", "prettier".
        // I will use "bamboo" as it's the "Takenoko" side (often the winner side in memes).
        sendVote("bamboo", 3141, "osii", "惜しい人");

        setTimeout(() => {
            showModal("おしい！このコマンドの前にもう一つコマンドが必要！\n(3,141点が加算されました)");
        }, 500);
    }

(function () {
    'use strict';

    // Shared audio helpers (background music) for WUTA Taekwondo Vocabulary Study App.
    //
    // Keeps state in localStorage:
    // - wuta_bgm_enabled: 'true' | 'false'
    // - wuta_bgm_volume:  '0.0'..'1.0'

    const STORAGE_ENABLED = 'wuta_bgm_enabled';
    const STORAGE_VOLUME = 'wuta_bgm_volume';

    function _safeGet(key) {
        try { return localStorage.getItem(key); } catch (e) { return null; }
    }

    function _safeSet(key, value) {
        try { localStorage.setItem(key, value); } catch (e) {}
    }

    function _clamp01(n) {
        const x = Number(n);
        if (Number.isNaN(x)) return 0;
        return Math.max(0, Math.min(1, x));
    }

    function initBgm(opts) {
        const cfg = Object.assign(
            {
                src: null,
                enabledDefault: true,
                volumeDefault: 0.22,
                toggleId: 'bgmToggle',
                volumeId: 'bgmVolume',
                labelId: 'bgmLabel',
            },
            opts || {}
        );

        if (!cfg.src) return;

        const toggleEl = document.getElementById(cfg.toggleId);
        const volumeEl = document.getElementById(cfg.volumeId);
        const labelEl = document.getElementById(cfg.labelId);

        // Create (or reuse) a singleton per page.
        const api = (window.WutaAudio = window.WutaAudio || {});
        if (!api._bgm) {
            const audio = new Audio(cfg.src);
            audio.loop = true;
            audio.preload = 'auto';
            // iOS Safari can be picky about when media is considered user-initiated.
            // These hints are harmless elsewhere.
            try { audio.setAttribute('playsinline', ''); } catch (e) {}
            try { audio.load(); } catch (e) {}
            api._bgm = {
                audio,
                enabled: cfg.enabledDefault,
                volume: cfg.volumeDefault,
                startedOnce: false,
                needsGesture: false,
            };
        } else {
            // Ensure the right track is set for this page.
            try {
                if (api._bgm.audio && api._bgm.audio.src !== cfg.src) {
                    api._bgm.audio.src = cfg.src;
                }
            } catch (e) {}
        }

        function loadState() {
            const rawEnabled = _safeGet(STORAGE_ENABLED);
            api._bgm.enabled = rawEnabled === null ? !!cfg.enabledDefault : rawEnabled === 'true';

            const rawVol = _safeGet(STORAGE_VOLUME);
            api._bgm.volume = rawVol === null ? cfg.volumeDefault : _clamp01(rawVol);

            api._bgm.audio.volume = api._bgm.volume;
        }

        function render() {
            const on = !!api._bgm.enabled;
            if (toggleEl) {
                toggleEl.setAttribute('aria-pressed', on ? 'true' : 'false');
                toggleEl.classList.toggle('is-off', !on);
                if (on && api._bgm.needsGesture) {
                    toggleEl.textContent = 'Music: ON (tap)';
                } else {
                    toggleEl.textContent = on ? 'Music: ON' : 'Music: OFF';
                }
            }
            if (labelEl) {
                labelEl.textContent = on ? '🎵 Music' : '🔇 Music';
            }
            if (volumeEl) {
                volumeEl.value = String(Math.round(api._bgm.volume * 100));
                volumeEl.disabled = !on;
            }
        }

        async function tryStart(reason) {
            if (!api._bgm.enabled) return false;
            if (!api._bgm.audio) return false;

            // Only attempt play after a user gesture in most browsers.
            try {
                api._bgm.audio.volume = api._bgm.volume;
                await api._bgm.audio.play();
                api._bgm.startedOnce = true;
                api._bgm.needsGesture = false;
                render();
                return true;
            } catch (e) {
                // Ignore; we'll retry on the next gesture.
                api._bgm.needsGesture = true;
                render();
                return false;
            }
        }

        function stop() {
            try {
                api._bgm.audio.pause();
                api._bgm.audio.currentTime = 0;
            } catch (e) {}
        }

        function setEnabled(enabled) {
            api._bgm.enabled = !!enabled;
            _safeSet(STORAGE_ENABLED, String(api._bgm.enabled));
            render();

            if (api._bgm.enabled) {
                // tryStart may still be blocked if not in a gesture, but that's okay.
                tryStart('toggle');
            } else {
                stop();
            }
        }

        function setVolume(vol01) {
            api._bgm.volume = _clamp01(vol01);
            api._bgm.audio.volume = api._bgm.volume;
            _safeSet(STORAGE_VOLUME, String(api._bgm.volume));
            render();
        }

        api.bgm = { tryStart, stop, setEnabled, setVolume, get audio() { return api._bgm.audio; } };

        loadState();
        render();

        if (toggleEl) {
            const toggleHandler = () => {
                // Tap/click is a user gesture - safest place to start playback.
                setEnabled(!api._bgm.enabled);
            };
            toggleEl.addEventListener('click', toggleHandler);
            // iOS Safari often behaves best when play() is triggered from touchstart.
            toggleEl.addEventListener('touchstart', toggleHandler, { passive: true });
        }

        if (volumeEl) {
            volumeEl.addEventListener('input', () => {
                const pct = Number(volumeEl.value);
                setVolume(_clamp01(pct / 100));
                // If the student adjusts volume, also try to start.
                tryStart('volume');
            });
        }

        // If music is enabled, attempt to start on the first interaction with the page.
        const startOnGesture = () => {
            tryStart('gesture');
        };
        // iOS Safari: touch events are the most reliable "gesture" signals.
        window.addEventListener('touchstart', startOnGesture, { once: true, passive: true });
        window.addEventListener('touchend', startOnGesture, { once: true, passive: true });
        // Other browsers
        window.addEventListener('pointerdown', startOnGesture, { once: true, passive: true });
        window.addEventListener('click', startOnGesture, { once: true, passive: true });
        window.addEventListener('keydown', startOnGesture, { once: true, passive: true });
    }

    window.WutaAudio = window.WutaAudio || {};
    window.WutaAudio.initBgm = initBgm;
})();

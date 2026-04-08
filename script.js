/**
 * 禅園西梅田 Instagram Reel Controller
 *
 * Instagram アルゴリズム最適化:
 * - 最初の1秒でフック → 視聴維持率UP
 * - 各シーン2.5〜4秒 → 飽きさせない展開
 * - 合計約21秒 → リール最適尺
 * - ループ再生 → 再生回数UP
 *
 * AI判定回避:
 * - 実写写真のKen Burns効果のみ
 * - テキストは最小限のオーバーレイ
 * - 過剰なフィルター・エフェクト無し
 */

class ReelPlayer {
    constructor() {
        this.scenes = document.querySelectorAll('.scene');
        this.totalScenes = this.scenes.length;
        this.currentScene = 0;
        this.isPlaying = false;
        this.timer = null;
        this.progressTimer = null;

        this.init();
    }

    init() {
        this.preloadImages();
        this.bindEvents();
        this.play();
    }

    preloadImages() {
        const images = [
            'assets/setting-sakura.jpg',
            'assets/table-overhead.jpg',
            'assets/dining-closeup.jpg',
            'assets/dining-group.jpg',
            'assets/dining-conversation.jpg',
            'assets/counter-service.jpg',
            'assets/celebration-menu.jpg'
        ];
        images.forEach(src => {
            const img = new Image();
            img.src = src;
        });
    }

    bindEvents() {
        // Tap navigation (Instagram-style)
        document.getElementById('tapLeft').addEventListener('click', () => {
            this.prev();
        });

        document.getElementById('tapRight').addEventListener('click', () => {
            this.next();
        });

        // Hold to pause
        const reel = document.getElementById('reel');
        let holdTimer = null;
        let isHolding = false;

        reel.addEventListener('mousedown', () => {
            holdTimer = setTimeout(() => {
                isHolding = true;
                this.pause();
            }, 200);
        });

        reel.addEventListener('mouseup', () => {
            clearTimeout(holdTimer);
            if (isHolding) {
                isHolding = false;
                this.resume();
            }
        });

        reel.addEventListener('mouseleave', () => {
            clearTimeout(holdTimer);
            if (isHolding) {
                isHolding = false;
                this.resume();
            }
        });

        // Touch hold to pause
        reel.addEventListener('touchstart', (e) => {
            holdTimer = setTimeout(() => {
                isHolding = true;
                this.pause();
            }, 200);
        }, { passive: true });

        reel.addEventListener('touchend', () => {
            clearTimeout(holdTimer);
            if (isHolding) {
                isHolding = false;
                this.resume();
            }
        }, { passive: true });

        // Keyboard
        document.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowRight':
                case ' ':
                    e.preventDefault();
                    this.next();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.prev();
                    break;
                case 'r':
                    this.restart();
                    break;
            }
        });

        // Sound toggle (decorative)
        document.getElementById('soundToggle').addEventListener('click', (e) => {
            e.stopPropagation();
            e.currentTarget.classList.toggle('on');
        });
    }

    getSceneDuration(index) {
        const scene = this.scenes[index];
        return parseInt(scene.dataset.duration) || 3000;
    }

    play() {
        this.isPlaying = true;
        this.showScene(this.currentScene);
    }

    pause() {
        this.isPlaying = false;
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
        if (this.progressTimer) {
            cancelAnimationFrame(this.progressTimer);
            this.progressTimer = null;
        }
    }

    resume() {
        if (!this.isPlaying) {
            this.isPlaying = true;
            this.scheduleNext(1000); // Resume with 1s remaining
        }
    }

    restart() {
        this.pause();
        this.resetAllProgress();
        this.currentScene = 0;
        this.scenes.forEach(s => {
            s.classList.remove('active', 'crossfade-out');
        });
        this.play();
    }

    showScene(index) {
        // Deactivate all scenes
        this.scenes.forEach((s, i) => {
            if (i !== index) {
                s.classList.remove('active');
                s.classList.add('crossfade-out');
                // Clean up after transition
                setTimeout(() => s.classList.remove('crossfade-out'), 600);
            }
        });

        // Activate current
        const scene = this.scenes[index];
        scene.classList.remove('crossfade-out');
        scene.classList.add('active');

        // Update progress bars
        this.updateProgressBars(index);

        // Schedule next scene
        const duration = this.getSceneDuration(index);
        this.animateProgress(index, duration);
        this.scheduleNext(duration);
    }

    scheduleNext(duration) {
        if (this.timer) clearTimeout(this.timer);

        this.timer = setTimeout(() => {
            if (!this.isPlaying) return;

            if (this.currentScene < this.totalScenes - 1) {
                this.currentScene++;
                this.showScene(this.currentScene);
            } else {
                // Loop - restart from beginning
                setTimeout(() => {
                    this.restart();
                }, 500);
            }
        }, duration);
    }

    updateProgressBars(activeIndex) {
        const segments = document.querySelectorAll('.progress-segment');
        segments.forEach((seg, i) => {
            const fill = seg.querySelector('.progress-fill');
            seg.classList.remove('active', 'completed');

            if (i < activeIndex) {
                seg.classList.add('completed');
                fill.style.width = '100%';
                fill.style.transition = 'none';
            } else if (i === activeIndex) {
                seg.classList.add('active');
                fill.style.width = '0%';
                fill.style.transition = 'none';
            } else {
                fill.style.width = '0%';
                fill.style.transition = 'none';
            }
        });
    }

    animateProgress(sceneIndex, duration) {
        const segment = document.querySelectorAll('.progress-segment')[sceneIndex];
        if (!segment) return;

        const fill = segment.querySelector('.progress-fill');
        const startTime = performance.now();

        const animate = (currentTime) => {
            if (!this.isPlaying) return;

            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            fill.style.width = `${progress * 100}%`;

            if (progress < 1) {
                this.progressTimer = requestAnimationFrame(animate);
            }
        };

        if (this.progressTimer) cancelAnimationFrame(this.progressTimer);
        this.progressTimer = requestAnimationFrame(animate);
    }

    resetAllProgress() {
        document.querySelectorAll('.progress-fill').forEach(fill => {
            fill.style.width = '0%';
            fill.style.transition = 'none';
        });
        document.querySelectorAll('.progress-segment').forEach(seg => {
            seg.classList.remove('active', 'completed');
        });
    }

    next() {
        if (this.timer) clearTimeout(this.timer);
        if (this.progressTimer) cancelAnimationFrame(this.progressTimer);

        if (this.currentScene < this.totalScenes - 1) {
            this.currentScene++;
        } else {
            this.currentScene = 0;
            this.resetAllProgress();
        }
        this.showScene(this.currentScene);
    }

    prev() {
        if (this.timer) clearTimeout(this.timer);
        if (this.progressTimer) cancelAnimationFrame(this.progressTimer);

        if (this.currentScene > 0) {
            this.currentScene--;
        }

        // Reset progress for scenes after current
        const segments = document.querySelectorAll('.progress-segment');
        segments.forEach((seg, i) => {
            if (i >= this.currentScene) {
                seg.querySelector('.progress-fill').style.width = '0%';
                seg.classList.remove('active', 'completed');
            }
        });

        this.showScene(this.currentScene);
    }
}

// Start
document.addEventListener('DOMContentLoaded', () => {
    new ReelPlayer();
});

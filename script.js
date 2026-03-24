/**
 * 禅園西梅田 - Instagram Reel Controller
 * Manages scene transitions, animations, and user controls
 */

class ReelController {
    constructor() {
        this.currentScene = 1;
        this.totalScenes = 5;
        this.sceneDuration = 4000; // 4 seconds per scene
        this.isPlaying = true;
        this.timer = null;
        this.startTime = null;

        this.progressFill = document.getElementById('progressFill');
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.restartBtn = document.getElementById('restartBtn');
        this.dots = document.querySelectorAll('.dot');

        this.init();
    }

    init() {
        this.bindEvents();
        this.startAutoPlay();
        this.updateProgress();
    }

    bindEvents() {
        // Play/Pause button
        this.playPauseBtn.addEventListener('click', () => this.togglePlayPause());

        // Restart button
        this.restartBtn.addEventListener('click', () => this.restart());

        // Navigation dots
        this.dots.forEach(dot => {
            dot.addEventListener('click', () => {
                const scene = parseInt(dot.dataset.scene);
                this.goToScene(scene);
            });
        });

        // Touch/Swipe support
        let touchStartY = 0;
        const reel = document.getElementById('reel');

        reel.addEventListener('touchstart', (e) => {
            touchStartY = e.touches[0].clientY;
        }, { passive: true });

        reel.addEventListener('touchend', (e) => {
            const touchEndY = e.changedTouches[0].clientY;
            const diff = touchStartY - touchEndY;

            if (Math.abs(diff) > 50) {
                if (diff > 0) {
                    this.nextScene();
                } else {
                    this.prevScene();
                }
            }
        }, { passive: true });

        // Keyboard support
        document.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowDown':
                case 'ArrowRight':
                case ' ':
                    e.preventDefault();
                    this.nextScene();
                    break;
                case 'ArrowUp':
                case 'ArrowLeft':
                    e.preventDefault();
                    this.prevScene();
                    break;
                case 'r':
                    this.restart();
                    break;
                case 'p':
                    this.togglePlayPause();
                    break;
            }
        });
    }

    startAutoPlay() {
        this.stopAutoPlay();
        this.isPlaying = true;
        this.playPauseBtn.textContent = '⏸';
        this.startTime = Date.now();

        this.timer = setInterval(() => {
            if (this.currentScene < this.totalScenes) {
                this.nextScene();
            } else {
                this.stopAutoPlay();
                this.playPauseBtn.textContent = '↺';
            }
        }, this.sceneDuration);
    }

    stopAutoPlay() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
        this.isPlaying = false;
        this.playPauseBtn.textContent = '▶';
    }

    togglePlayPause() {
        if (this.currentScene === this.totalScenes && !this.isPlaying) {
            this.restart();
            return;
        }

        if (this.isPlaying) {
            this.stopAutoPlay();
        } else {
            this.startAutoPlay();
        }
    }

    restart() {
        this.goToScene(1);
        this.startAutoPlay();
    }

    goToScene(sceneNumber) {
        if (sceneNumber < 1 || sceneNumber > this.totalScenes) return;
        if (sceneNumber === this.currentScene) return;

        // Deactivate current scene
        const currentEl = document.getElementById(`scene${this.currentScene}`);
        currentEl.classList.remove('active');
        currentEl.classList.add('fade-out');

        // Activate new scene
        this.currentScene = sceneNumber;
        const newEl = document.getElementById(`scene${this.currentScene}`);

        setTimeout(() => {
            currentEl.classList.remove('fade-out');
            newEl.classList.add('active');
        }, 100);

        // Update dots
        this.dots.forEach(dot => dot.classList.remove('active'));
        this.dots[this.currentScene - 1].classList.add('active');

        // Update progress
        this.updateProgress();

        // Reset autoplay timer
        if (this.isPlaying) {
            this.startAutoPlay();
        }
    }

    nextScene() {
        if (this.currentScene < this.totalScenes) {
            this.goToScene(this.currentScene + 1);
        }
    }

    prevScene() {
        if (this.currentScene > 1) {
            this.goToScene(this.currentScene - 1);
        }
    }

    updateProgress() {
        const progress = (this.currentScene / this.totalScenes) * 100;
        this.progressFill.style.width = `${progress}%`;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ReelController();
});

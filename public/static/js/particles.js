// Interactive Particle Background using HTML5 Canvas
class ParticleNetwork {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 150 };
        
        // Settings
        this.maxParticles = 80;
        this.connectionDistance = 120;
        this.speedMultiplier = 0.5;
        
        this.init();
        this.animate();
        this.registerEvents();
    }

    init() {
        this.resizeCanvas();
        this.particles = [];
        
        // Determine particle colors based on current theme (dark vs light)
        const isDark = document.documentElement.classList.contains('dark');
        this.particleColor = isDark ? 'rgba(168, 85, 247, 0.4)' : 'rgba(99, 102, 241, 0.3)';
        this.lineColor = isDark ? 'rgba(99, 102, 241, 0.12)' : 'rgba(168, 85, 247, 0.08)';

        // Adjust density for mobile devices
        if (window.innerWidth < 768) {
            this.maxParticles = 30;
            this.connectionDistance = 80;
        } else {
            this.maxParticles = 80;
            this.connectionDistance = 120;
        }

        for (let i = 0; i < this.maxParticles; i++) {
            const size = Math.random() * 3 + 1;
            const x = Math.random() * (this.canvas.width - size * 2) + size;
            const y = Math.random() * (this.canvas.height - size * 2) + size;
            const directionX = (Math.random() * 2 - 1) * this.speedMultiplier;
            const directionY = (Math.random() * 2 - 1) * this.speedMultiplier;

            this.particles.push({
                x, y,
                directionX, directionY,
                size
            });
        }
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    registerEvents() {
        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.init();
        });

        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        window.addEventListener('mouseleave', () => {
            this.mouse.x = null;
            this.mouse.y = null;
        });
        
        // Watch for theme changes from main.js theme toggler
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'class') {
                    const isDark = document.documentElement.classList.contains('dark');
                    this.particleColor = isDark ? 'rgba(168, 85, 247, 0.4)' : 'rgba(99, 102, 241, 0.3)';
                    this.lineColor = isDark ? 'rgba(99, 102, 241, 0.12)' : 'rgba(168, 85, 247, 0.08)';
                }
            });
        });
        observer.observe(document.documentElement, { attributes: true });
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        for (let i = 0; i < this.particles.length; i++) {
            let p = this.particles[i];
            
            // Move particle
            p.x += p.directionX;
            p.y += p.directionY;

            // Bounce off boundaries
            if (p.x > this.canvas.width || p.x < 0) p.directionX = -p.directionX;
            if (p.y > this.canvas.height || p.y < 0) p.directionY = -p.directionY;

            // Mouse interactivity - repel particles slightly
            if (this.mouse.x !== null && this.mouse.y !== null) {
                let dx = p.x - this.mouse.x;
                let dy = p.y - this.mouse.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < this.mouse.radius) {
                    let force = (this.mouse.radius - distance) / this.mouse.radius;
                    let angle = Math.atan2(dy, dx);
                    p.x += Math.cos(angle) * force * 2;
                    p.y += Math.sin(angle) * force * 2;
                }
            }

            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2, false);
            this.ctx.fillStyle = this.particleColor;
            this.ctx.fill();

            // Draw lines connecting particles
            for (let j = i + 1; j < this.particles.length; j++) {
                let p2 = this.particles[j];
                let dx = p.x - p2.x;
                let dy = p.y - p2.y;
                let dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < this.connectionDistance) {
                    let opacity = (1 - (dist / this.connectionDistance)) * 0.5;
                    this.ctx.strokeStyle = this.lineColor.replace(/[\d\.]+\)$/, `${opacity})`);
                    this.ctx.lineWidth = 0.8;
                    this.ctx.beginPath();
                    this.ctx.moveTo(p.x, p.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.stroke();
                }
            }
        }
        
        requestAnimationFrame(() => this.animate());
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ParticleNetwork('particles-canvas');
});

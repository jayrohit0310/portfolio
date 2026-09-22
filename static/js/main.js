// Main Application JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // 1. Theme Management (Dark / Light Mode)
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
    const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

    // Initialize theme based on localStorage or system preference
    if (localStorage.getItem('color-theme') === 'dark' || 
        (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        themeToggleLightIcon.classList.remove('hidden');
        themeToggleDarkIcon.classList.add('hidden');
    } else {
        document.documentElement.classList.remove('dark');
        themeToggleLightIcon.classList.add('hidden');
        themeToggleDarkIcon.classList.remove('hidden');
    }

    // Toggle theme action
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            themeToggleLightIcon.classList.toggle('hidden');
            themeToggleDarkIcon.classList.toggle('hidden');

            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('color-theme', 'light');
            } else {
                document.documentElement.classList.add('dark');
                localStorage.setItem('color-theme', 'dark');
            }
        });
    }

    // 2. Custom Cursor (Spring physics for smoothness)
    const cursorOutline = document.querySelector('.custom-cursor');
    const cursorDot = document.querySelector('.custom-cursor-dot');
    
    let mouseX = 0;
    let mouseY = 0;
    let cursorX = 0;
    let cursorY = 0;
    const speed = 0.15; // Speed factor for cursor easing

    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        // Move the inner dot immediately
        if (cursorDot) {
            cursorDot.style.left = `${mouseX}px`;
            cursorDot.style.top = `${mouseY}px`;
        }
    });

    // Animate outline with easing
    function animateCursor() {
        let distX = mouseX - cursorX;
        let distY = mouseY - cursorY;
        
        cursorX += distX * speed;
        cursorY += distY * speed;

        if (cursorOutline) {
            cursorOutline.style.left = `${cursorX}px`;
            cursorOutline.style.top = `${cursorY}px`;
        }

        requestAnimationFrame(animateCursor);
    }
    animateCursor();

    // Hover scale effects on interactive elements
    const hoverElements = document.querySelectorAll('a, button, select, input, textarea, .interactive-card');
    hoverElements.forEach(elem => {
        elem.addEventListener('mouseenter', () => {
            if (cursorOutline) cursorOutline.classList.add('hover');
        });
        elem.addEventListener('mouseleave', () => {
            if (cursorOutline) cursorOutline.classList.remove('hover');
        });
    });

    // 3. Dynamic Typing Animation in Hero
    const typeTarget = document.getElementById('typing-text');
    const words = ["IT Student", "Python Developer", "Web Developer", "Problem Solver"];
    let wordIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    let typingSpeed = 100;

    function type() {
        if (!typeTarget) return;
        const currentWord = words[wordIndex];
        
        if (isDeleting) {
            typeTarget.textContent = currentWord.substring(0, charIndex - 1);
            charIndex--;
            typingSpeed = 50; // faster deletion
        } else {
            typeTarget.textContent = currentWord.substring(0, charIndex + 1);
            charIndex++;
            typingSpeed = 150; // standard typing
        }

        // Typing logic transitions
        if (!isDeleting && charIndex === currentWord.length) {
            typingSpeed = 2000; // Pause at end of word
            isDeleting = true;
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            wordIndex = (wordIndex + 1) % words.length;
            typingSpeed = 500; // Pause before typing next word
        }

        setTimeout(type, typingSpeed);
    }
    
    if (typeTarget) {
        setTimeout(type, 1000);
    }

    // 4. Scroll Progress Indicator & Back to Top visibility
    const scrollBar = document.getElementById('scroll-progress');
    const backToTopBtn = document.getElementById('back-to-top');

    window.addEventListener('scroll', () => {
        const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (window.scrollY / totalHeight) * 100;
        
        if (scrollBar) {
            scrollBar.style.width = `${scrollPercent}%`;
        }

        if (backToTopBtn) {
            if (window.scrollY > 500) {
                backToTopBtn.classList.remove('opacity-0', 'pointer-events-none');
                backToTopBtn.classList.add('opacity-100');
            } else {
                backToTopBtn.classList.remove('opacity-100');
                backToTopBtn.classList.add('opacity-0', 'pointer-events-none');
            }
        }
    });

    // 5. Mobile Navbar Menu
    const menuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
            
            // Toggle hamburger icon animation/state
            const icons = menuBtn.querySelectorAll('svg');
            icons.forEach(icon => icon.classList.toggle('hidden'));
        });
        
        // Close menu when a link is clicked
        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                const hamburgerIcon = menuBtn.querySelector('svg:not(.hidden)');
                const closeIcon = menuBtn.querySelector('svg.hidden');
                
                // Reset icons
                if (hamburgerIcon && hamburgerIcon.classList.contains('close-icon')) {
                    hamburgerIcon.classList.add('hidden');
                }
                const firstIcon = menuBtn.querySelector('svg:first-child');
                const secondIcon = menuBtn.querySelector('svg:last-child');
                if (firstIcon && secondIcon) {
                    firstIcon.classList.remove('hidden');
                    secondIcon.classList.add('hidden');
                }
            });
        });
    }

    // 6. Project Category Filtering
    const filterButtons = document.querySelectorAll('.filter-btn');
    const projectCards = document.querySelectorAll('.project-card');

    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active classes from all buttons
            filterButtons.forEach(b => {
                b.classList.remove('bg-indigo-600', 'text-white');
                b.classList.add('bg-slate-200', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
            });
            
            // Add active styles to clicked button
            btn.classList.remove('bg-slate-200', 'dark:bg-slate-800', 'text-slate-700', 'dark:text-slate-300');
            btn.classList.add('bg-indigo-600', 'text-white');

            const category = btn.getAttribute('data-filter');

            projectCards.forEach(card => {
                const cardCategories = card.getAttribute('data-categories').split(' ');
                
                if (category === 'all' || cardCategories.includes(category)) {
                    card.style.display = 'block';
                    // Retrigger micro-animations if needed
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'scale(1)';
                    }, 50);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.95)';
                    // Delay display:none to let transition finish
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 200);
                }
            });
        });
    });

    // 7. Scroll-Triggered Viewport Animations (using Intersection Observer)
    const fadeElements = document.querySelectorAll('.fade-on-scroll');
    const skillBars = document.querySelectorAll('.skill-bar-fill');

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const scrollObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // If it's a general animated element
                if (entry.target.classList.contains('fade-on-scroll')) {
                    entry.target.classList.remove('opacity-0', 'translate-y-8');
                    entry.target.classList.add('opacity-100', 'translate-y-0');
                    observer.unobserve(entry.target);
                }
            }
        });
    }, observerOptions);

    fadeElements.forEach(el => {
        el.classList.add('transition-all', 'duration-700', 'ease-out', 'opacity-0', 'translate-y-8');
        scrollObserver.observe(el);
    });

    // Skill Bar Fill observer
    const skillObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const percent = entry.target.getAttribute('data-percent');
                entry.target.style.width = `${percent}%`;
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    skillBars.forEach(bar => {
        bar.style.width = '0%';
        skillObserver.observe(bar);
    });

    // 8. Coding Stats Integration API fetch
    fetch('/api/coding-stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const stats = data.stats;
                
                // Update LeetCode Elements
                const lcSolved = document.getElementById('lc-solved');
                const lcEasy = document.getElementById('lc-easy');
                const lcMedium = document.getElementById('lc-medium');
                const lcHard = document.getElementById('lc-hard');
                if (lcSolved) lcSolved.textContent = stats.leetcode.solved;
                if (lcEasy) lcEasy.textContent = stats.leetcode.easy;
                if (lcMedium) lcMedium.textContent = stats.leetcode.medium;
                if (lcHard) lcHard.textContent = stats.leetcode.hard;

                // Update CodeChef Elements
                const ccRating = document.getElementById('cc-rating');
                const ccStars = document.getElementById('cc-stars');
                if (ccRating) ccRating.textContent = stats.codechef.rating;
                if (ccStars) ccStars.textContent = stats.codechef.stars;

                // Update Codeforces
                const cfRating = document.getElementById('cf-rating');
                const cfRank = document.getElementById('cf-rank');
                if (cfRating) cfRating.textContent = stats.codeforces.rating;
                if (cfRank) cfRank.textContent = stats.codeforces.rank;
            }
        })
        .catch(err => console.error("Error loading coding profile stats: ", err));

    // Remove Loader Overlay
    const loader = document.getElementById('loader-overlay');
    const loaderBar = document.getElementById('loader-bar');
    const loaderText = document.getElementById('loader-text');
    if (loader && loaderBar && loaderText) {
        let progress = 1;
        const interval = setInterval(() => {
            progress += Math.floor(Math.random() * 10) + 5;
            if (progress > 100) progress = 100;
            loaderBar.style.width = `${progress}%`;
            loaderText.textContent = `${progress}%`;
            
            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    loader.style.opacity = '0';
                    setTimeout(() => {
                        loader.style.display = 'none';
                    }, 500);
                }, 400);
            }
        }, 50);
    } else if (loader) {
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 500);
        }, 800); // short delay to show futuristic loader
    }
});

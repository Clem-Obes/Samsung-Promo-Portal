// =============================================
// SAMSUNG PROMO PORTAL - Main JavaScript
// =============================================

document.addEventListener('DOMContentLoaded', function () {

    // Initialize AOS Animations
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out-cubic',
            once: true,
            offset: 80,
        });
    }

    // Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Animated Counter
    const counters = document.querySelectorAll('.counter');
    const counterSpeed = 50;

    const animateCounters = () => {
        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            const current = +counter.innerText;
            const increment = target / 100;

            if (current < target) {
                counter.innerText = Math.ceil(current + increment);
                setTimeout(() => animateCounters(), counterSpeed);
            } else {
                counter.innerText = target.toLocaleString();
            }
        });
    };

    // Intersection Observer for counters
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounters();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        observer.observe(statsSection);
    }

    // Countdown Timer
    const countdownEl = document.getElementById('promo-countdown');
    if (countdownEl) {
        const targetDate = new Date(countdownEl.dataset.target).getTime();

        const updateCountdown = () => {
            const now = new Date().getTime();
            const diff = targetDate - now;

            if (diff > 0) {
                const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);

                document.getElementById('countdown-days').textContent = String(days).padStart(2, '0');
                document.getElementById('countdown-hours').textContent = String(hours).padStart(2, '0');
                document.getElementById('countdown-minutes').textContent = String(minutes).padStart(2, '0');
                document.getElementById('countdown-seconds').textContent = String(seconds).padStart(2, '0');
            }
        };

        updateCountdown();
        setInterval(updateCountdown, 1000);
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Copy referral link
    const copyBtn = document.getElementById('copy-referral');
    if (copyBtn) {
        copyBtn.addEventListener('click', function () {
            const link = document.getElementById('referral-link');
            if (link) {
                navigator.clipboard.writeText(link.value).then(() => {
                    this.innerHTML = '<i class="bi bi-check-lg"></i> Copied!';
                    setTimeout(() => {
                        this.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
                    }, 2000);
                });
            }
        });
    }

    // Active navbar link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // =============================================
    // Social Proof Popup Notifications
    // =============================================
    const socialProofData = [
        { name: 'Adebayo O.', location: 'Lagos, Nigeria', action: 'just claimed a Galaxy S24 Ultra', time: '2 min ago', initial: 'A' },
        { name: 'Grace M.', location: 'Nairobi, Kenya', action: 'completed 5 referral milestone', time: '5 min ago', initial: 'G' },
        { name: 'Emmanuel K.', location: 'Accra, Ghana', action: 'upgraded to Ambassador tier', time: '8 min ago', initial: 'E' },
        { name: 'Fatima B.', location: 'Dar es Salaam', action: 'just registered for the promo', time: '10 min ago', initial: 'F' },
        { name: 'James T.', location: 'Kampala, Uganda', action: 'received Galaxy Buds Pro', time: '12 min ago', initial: 'J' },
        { name: 'Sarah N.', location: 'Kigali, Rwanda', action: 'earned 500 bonus points', time: '15 min ago', initial: 'S' },
        { name: 'Michael A.', location: 'Abuja, Nigeria', action: 'completed all campaign tasks', time: '18 min ago', initial: 'M' },
        { name: 'Blessing E.', location: 'Douala, Cameroon', action: 'just joined the Premium plan', time: '20 min ago', initial: 'B' },
    ];

    let proofIndex = 0;
    const proofPopup = document.getElementById('social-proof-popup');

    function showSocialProof() {
        if (!proofPopup) return;
        const data = socialProofData[proofIndex % socialProofData.length];
        proofPopup.querySelector('.sp-avatar').textContent = data.initial;
        proofPopup.querySelector('.sp-name').textContent = data.name;
        proofPopup.querySelector('.sp-action').textContent = data.action;
        proofPopup.querySelector('.sp-location').textContent = data.location;
        proofPopup.querySelector('.sp-time').textContent = data.time;

        proofPopup.classList.add('show');
        setTimeout(() => {
            proofPopup.classList.remove('show');
            proofIndex++;
        }, 5000);
    }

    if (proofPopup) {
        // First show after 8 seconds, then every 15 seconds
        setTimeout(showSocialProof, 8000);
        setInterval(showSocialProof, 15000);

        // Close on click
        proofPopup.addEventListener('click', function () {
            this.classList.remove('show');
        });
    }

    // =============================================
    // Typewriter Effect
    // =============================================
    const typewriterEls = document.querySelectorAll('.typewriter-text');
    typewriterEls.forEach(el => {
        const words = JSON.parse(el.dataset.words || '[]');
        if (words.length === 0) return;

        let wordIndex = 0;
        let charIndex = 0;
        let isDeleting = false;

        function typeLoop() {
            const currentWord = words[wordIndex % words.length];
            if (isDeleting) {
                el.textContent = currentWord.substring(0, charIndex - 1);
                charIndex--;
            } else {
                el.textContent = currentWord.substring(0, charIndex + 1);
                charIndex++;
            }

            let speed = isDeleting ? 50 : 100;

            if (!isDeleting && charIndex === currentWord.length) {
                speed = 2000; // Pause at end
                isDeleting = true;
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                wordIndex++;
                speed = 500;
            }

            setTimeout(typeLoop, speed);
        }

        typeLoop();
    });

    // =============================================
    // Parallax on scroll
    // =============================================
    window.addEventListener('scroll', function () {
        const parallaxEls = document.querySelectorAll('.parallax-slow');
        parallaxEls.forEach(el => {
            const speed = 0.3;
            const yPos = -(window.scrollY * speed);
            el.style.transform = `translateY(${yPos}px)`;
        });
    });

    // =============================================
    // Number counting for inline counters
    // =============================================
    const inlineCounters = document.querySelectorAll('.inline-counter');
    if (inlineCounters.length > 0) {
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const target = parseInt(el.dataset.target);
                    const suffix = el.dataset.suffix || '';
                    const prefix = el.dataset.prefix || '';
                    let current = 0;
                    const increment = target / 80;
                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= target) {
                            current = target;
                            clearInterval(timer);
                        }
                        el.textContent = prefix + Math.floor(current).toLocaleString() + suffix;
                    }, 25);
                    counterObserver.unobserve(el);
                }
            });
        }, { threshold: 0.5 });

        inlineCounters.forEach(el => counterObserver.observe(el));
    }

    // =============================================
    // FAQ search filter
    // =============================================
    const faqSearch = document.getElementById('faq-search');
    if (faqSearch) {
        faqSearch.addEventListener('input', function () {
            const query = this.value.toLowerCase();
            document.querySelectorAll('.accordion-item').forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    console.log('🚀 Samsung Promo Portal loaded successfully!');
});

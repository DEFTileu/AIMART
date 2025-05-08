document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    const overlay = document.getElementById('overlay');

    if (mobileMenuBtn && navLinks && overlay) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            overlay.classList.toggle('active');
        });

        overlay.addEventListener('click', function() {
            navLinks.classList.remove('active');
            overlay.classList.remove('active');
        });
    }

    // Shrink navbar on scroll
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Scroll to top button
    const scrollTopBtn = document.getElementById('scrollTop');
    if (scrollTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                scrollTopBtn.classList.add('visible');
            } else {
                scrollTopBtn.classList.remove('visible');
            }
        });

        scrollTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Add to cart functionality
    const addToCartBtns = document.querySelectorAll('.add-to-cart');
    addToCartBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-id');

            // Here you would typically send an AJAX request to add the item to cart
            // For now, just show a message
            alert('Товар добавлен в корзину!');
        });
    });

    // Add to wishlist functionality
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-id');

            // Toggle active class for visual feedback
            this.classList.toggle('active');

            // Here you would typically send an AJAX request to add/remove from wishlist
            if (this.classList.contains('active')) {
                this.innerHTML = '❤️';
                alert('Товар добавлен в избранное!');
            } else {
                this.innerHTML = '🤍';
                alert('Товар удален из избранного!');
            }
        });
    });

    // Product image hover effect
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const img = this.querySelector('.product-img');
            if (img) {
                img.style.transform = 'scale(1.05)';
            }
        });

        card.addEventListener('mouseleave', function() {
            const img = this.querySelector('.product-img');
            if (img) {
                img.style.transform = 'scale(1)';
            }
        });
    });

    // Banner slider (if multiple banners)
    const banners = document.querySelectorAll('.banner-slide');
    let currentBanner = 0;

    function showBanner(index) {
        banners.forEach((banner, i) => {
            if (i === index) {
                banner.style.display = 'block';
            } else {
                banner.style.display = 'none';
            }
        });
    }

    if (banners.length > 1) {
        setInterval(() => {
            currentBanner = (currentBanner + 1) % banners.length;
            showBanner(currentBanner);
        }, 5000); // Change banner every 5 seconds

        // Initially show the first banner
        showBanner(0);
    }
});
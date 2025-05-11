document.addEventListener("DOMContentLoaded", function () {
  // Mobile menu toggle
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const navLinks = document.getElementById("navLinks");
  const overlay = document.getElementById("overlay");

  if (mobileMenuBtn && navLinks && overlay) {
    mobileMenuBtn.addEventListener("click", function () {
      navLinks.classList.toggle("active");
      overlay.classList.toggle("active");
    });

    overlay.addEventListener("click", function () {
      navLinks.classList.remove("active");
      overlay.classList.remove("active");
    });
  }

  // Новый слайдер баннеров
  function initBannerSliderV2() {

    const slides = document.querySelectorAll(".banner-slide");
    const dots = document.querySelectorAll(".banner-dot");
    const prevBtn = document.querySelector(".banner-prev");
    const nextBtn = document.querySelector(".banner-next");
    const carousel = document.querySelector(".banner-carousel");
    let current = 0;
    let timer;
    const delay = 5000;


    function showSlide(idx) {
      slides.forEach((slide, i) => {
        slide.classList.toggle("active", i === idx);
      });
      dots.forEach((dot, i) => {
        dot.classList.toggle("active", i === idx);
      });
      current = idx;
    }

    function nextSlide() {
      showSlide((current + 1) % slides.length);
    }
    function prevSlide() {
      showSlide((current - 1 + slides.length) % slides.length);
    }

    function startAuto() {
      stopAuto();
      if (slides.length > 1) {
        timer = setInterval(nextSlide, delay);
      }
    }
    function stopAuto() {
      if (timer) clearInterval(timer);
    }

    if (prevBtn)
      prevBtn.onclick = () => {
        prevSlide();
        stopAuto();
        setTimeout(startAuto, delay);
      };
    if (nextBtn)
      nextBtn.onclick = () => {
        nextSlide();
        stopAuto();
        setTimeout(startAuto, delay);
      };
    dots.forEach((dot, i) => {
      dot.onclick = () => {
        showSlide(i);
        stopAuto();
        setTimeout(startAuto, delay);
      };
    });

    if (carousel) {
      carousel.addEventListener("mouseenter", stopAuto);
      carousel.addEventListener("mouseleave", startAuto);
    }

    // Клавиатура
    document.addEventListener("keydown", (e) => {
      if (
        document.activeElement.tagName === "INPUT" ||
        document.activeElement.tagName === "TEXTAREA"
      )
        return;
      if (e.key === "ArrowLeft") {
        prevSlide();
        stopAuto();
        setTimeout(startAuto, delay);
      }
      if (e.key === "ArrowRight") {
        nextSlide();
        stopAuto();
        setTimeout(startAuto, delay);
      }
    });

    showSlide(0);
    startAuto();
  }

  // Запускаем инициализацию слайдера баннеров
  initBannerSliderV2();

  // Shrink navbar on scroll
  const navbar = document.querySelector(".navbar");
  if (navbar) {
    window.addEventListener("scroll", function () {
      if (window.scrollY > 50) {
        navbar.classList.add("scrolled");
      } else {
        navbar.classList.remove("scrolled");
      }
    });
  }

  // Scroll to top button
  const scrollTopBtn = document.getElementById("scrollTop");
  if (scrollTopBtn) {
    window.addEventListener("scroll", function () {
      if (window.scrollY > 300) {
        scrollTopBtn.classList.add("visible");
      } else {
        scrollTopBtn.classList.remove("visible");
      }
    });

    scrollTopBtn.addEventListener("click", function () {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    });
  }

  // Add to cart functionality
  const addToCartBtns = document.querySelectorAll(".add-to-cart");
  addToCartBtns.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const productId = this.getAttribute("data-id");

      // Here you would typically send an AJAX request to add the item to cart
      // For now, just show a message
      alert("Товар добавлен в корзину!");
    });
  });

  // Add to wishlist functionality
  const wishlistBtns = document.querySelectorAll(".wishlist-btn");
  wishlistBtns.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const productId = this.getAttribute("data-id");

      // Toggle active class for visual feedback
      this.classList.toggle("active");

      // Here you would typically send an AJAX request to add/remove from wishlist
      if (this.classList.contains("active")) {
        this.innerHTML = "❤️";
        alert("Товар добавлен в избранное!");
      } else {
        this.innerHTML = "🤍";
        alert("Товар удален из избранного!");
      }
    });
  });

  // Product image hover effect
  const productCards = document.querySelectorAll(".product-card");
  productCards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      const img = this.querySelector(".product-img");
      if (img) {
        img.style.transform = "scale(1.05)";
      }
    });

    card.addEventListener("mouseleave", function () {
      const img = this.querySelector(".product-img");
      if (img) {
        img.style.transform = "scale(1)";
      }
    });
  });
});

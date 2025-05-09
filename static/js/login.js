document.addEventListener('DOMContentLoaded', function () {
    const cont = document.querySelector('.cont');
    const imgBtn = document.querySelector('.img-btn');
    const signInForm = document.querySelector('.sign-in');
    const signUpForm = document.querySelector('.sign-up');

    // Флаг, который будет блокировать переключение формы при отправке
    let isFormSubmitting = false;

    // Функция для переключения на Sign Up
    function showSignUp() {
        if (isFormSubmitting) return;  // Если форма отправляется, не переключаем
        cont.classList.add('s-signup');
        signInForm.style.display = 'none';
        signUpForm.style.display = 'block';
    }

    // Функция для переключения на Sign In
    function showSignIn() {
        if (isFormSubmitting) return;  // Если форма отправляется, не переключаем
        cont.classList.remove('s-signup');
        signInForm.style.display = 'block';
        signUpForm.style.display = 'none';
    }

    // Проверка атрибута data-show-form при загрузке страницы
    const showForm = cont.getAttribute('data-show-form');
    if (showForm === 'signup') {
        showSignUp();
    } else {
        showSignIn();
    }

    // Обработчик клика по кнопке переключения
    imgBtn.addEventListener('click', function () {
        if (isFormSubmitting) return;  // Если форма отправляется, не переключаем
        if (cont.classList.contains('s-signup')) {
            showSignIn();
        } else {
            showSignUp();
        }
    });

    // Обработчик отправки формы логина
    const loginForm = document.querySelector('.form.sign-in');
    if (loginForm) {
        loginForm.addEventListener('submit', function () {
            // Блокируем возможность переключать формы во время отправки
            isFormSubmitting = true;
        });
    }

    // Автоматическое исчезновение сообщений (ошибки/успех)
    const messages = document.querySelectorAll('.error, .success');
    if (messages.length > 0) {
        setTimeout(() => {
            messages.forEach(msg => {
                msg.style.opacity = '0';
                setTimeout(() => msg.remove(), 500);
            });
        }, 5000); // Сообщения исчезают через 5 секунд
    }
});

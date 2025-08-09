tailwind.config = {
    theme: {
        extend: {
            colors: {
                'olive': {
                    50: '#f7f8f3',
                    100: '#edeee3',
                    200: '#dcdfc8',
                    300: '#c4cba4',
                    400: '#adb982',
                    500: '#8a9b5d',
                    600: '#6f7d47',
                    700: '#58613a',
                    800: '#484e32',
                    900: '#3c422c',
                },
                'sage': {
                    50: '#f6f7f4',
                    100: '#e9ebe3',
                    200: '#d4d9c8',
                    300: '#b7c0a3',
                    400: '#98a67c',
                    500: '#7d8a5d',
                    600: '#626d47',
                    700: '#4d563a',
                    800: '#404732',
                    900: '#373d2c',
                }
            }
        }
    }
}

// تعريف الدالة toggleMobileMenu كدالة global علشان تشتغل مع onclick في HTML
window.toggleMobileMenu = function() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('hidden');
};

// إغلاق القائمة لما تضغط برة زر القائمة
document.addEventListener('click', function(event) {
    const menu = document.getElementById('mobile-menu');
    const button = event.target.closest('[onclick="toggleMobileMenu()"]');

    if (!button && !menu.contains(event.target)) {
        menu.classList.add('hidden');
    }
});

// كود يشتغل بعد تحميل الصفحة عشان يربط زر إضافة المنتج للCart
document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.add-to-cart-btn');

    buttons.forEach(button => {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-product-id');

            fetch(`/cart/add/${productId}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Produit ajouté au panier !');
                    const cartCountEl = document.getElementById('cart-count');
                    if (cartCountEl) cartCountEl.textContent = data.cart_count;
                } else {
                    alert('Erreur lors de l’ajout au panier.');
                }
            })
            .catch(() => alert('Erreur réseau ou serveur.'));
        });
    });
});

// ====== SHARE PRODUCT ======
window.shareProduct = function() {
    if (navigator.share) {
        navigator.share({
            title: window.productName || document.title,
            text: window.productDescription || '',
            url: window.location.href
        });
    } else {
        navigator.clipboard.writeText(window.location.href);
        alert('Lien copié dans le presse-papier !');
    }
}

// ====== STAR RATING ======
document.addEventListener('DOMContentLoaded', function () {
    const starInputs = document.querySelectorAll('input[name="rating"]');
    const starLabels = document.querySelectorAll('label[for^="rating-"]');

    function updateStars(ratingValue) {
        starLabels.forEach(label => {
            const starValue = parseInt(label.getAttribute('for').split('-')[1]);
            if (starValue <= ratingValue) {
                label.classList.add('text-yellow-500');
                label.classList.remove('text-stone-300');
            } else {
                label.classList.add('text-stone-300');
                label.classList.remove('text-yellow-500');
            }
        });
    }

    starLabels.forEach(label => {
        label.addEventListener('click', function () {
            const ratingValue = parseInt(this.getAttribute('for').split('-')[1]);
            updateStars(ratingValue);
        });
    });

    const checkedInput = document.querySelector('input[name="rating"]:checked');
    if (checkedInput) {
        updateStars(parseInt(checkedInput.value));
    } else {
        updateStars(0);
    }
});

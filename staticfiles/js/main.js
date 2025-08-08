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
    // يبحث إذا العنصر المضغوط عليه هو الزر اللي فيه onclick="toggleMobileMenu()"
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
                    // تحديث عداد السلة لو موجود
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

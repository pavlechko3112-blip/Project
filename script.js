  let cart = [];

// Елементи DOM
const cartBtn = document.getElementById('cartBtn');
const cartModal = document.getElementById('cartModal');
const closeCart = document.getElementById('closeCart');
const cartItemsContainer = document.getElementById('cartItems');
const cartCount = document.getElementById('cartCount');
const totalPriceElement = document.getElementById('totalPrice');
const checkoutBtn = document.getElementById('checkoutBtn');

// 1. Відкриття та закриття кошика
cartBtn.addEventListener('click', () => {
    cartModal.classList.add('open');
});

closeCart.addEventListener('click', () => {
    cartModal.classList.remove('open');
});

// 2. Додавання товару в кошик
document.querySelectorAll('.btn-add-to-cart').forEach(button => {
    button.addEventListener('click', (e) => {
        const name = e.target.getAttribute('data-name');
        const price = parseInt(e.target.getAttribute('data-price'));

        // Перевіряємо, чи є вже така гра в кошику
        const existingItem = cart.find(item => item.name === name);

        if (existingItem) {
            existingItem.quantity += 1; // Якщо є, збільшуємо кількість
        } else {
            cart.push({ name, price, quantity: 1 }); // Якщо немає, додаємо нову
        }

        updateCart();
    });
});

// 3. Оновлення відображення кошика
function updateCart() {
    // Очищаємо контейнер
    cartItemsContainer.innerHTML = '';

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p class="empty-message">Кошик порожній</p>';
    } else {
        // Рендеримо кожен товар
        cart.forEach((item, index) => {
            const itemElement = document.createElement('div');
            itemElement.classList.add('cart-item');
            itemElement.innerHTML = `
                <div class="cart-item-info">
                    <h4>${item.name}</h4>
                    <span>${item.price} грн x ${item.quantity}</span>
                </div>
                <button class="btn-remove" onclick="removeFromCart(${index})">Видалити</button>
            `;
            cartItemsContainer.appendChild(itemElement);
        });
    }

    // Рахуємо загальну кількість товарів для лічильника в шапці
    const totalCount = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.innerText = totalCount;

    // Рахуємо загальну суму
    const totalSum = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    totalPriceElement.innerText = totalSum;
}

// 4. Видалення товару з кошика
window.removeFromCart = function(index) {
    if (cart[index].quantity > 1) {
        cart[index].quantity -= 1; // Зменшуємо кількість на 1
    } else {
        cart.splice(index, 1); // Якщо був один, видаляємо повністю з масиву
    }
    updateCart();
};

// 5. Кнопка оформлення замовлення
checkoutBtn.addEventListener('click', () => {
    if (cart.length === 0) {
        alert('Ваш кошик порожній. Додайте гру перед оформленням!');
    } else {
        alert('Дякуємо за замовлення! Ключі активації надіслані на вашу пошту (імітація).');
        cart = []; // Очищаємо кошик після покупки
        updateCart();
        cartModal.classList.remove('open');
    }
});
if (localStorage.getItem('cart') == null) {
    var cart = {};
} else {
    cart = JSON.parse(localStorage.getItem('cart'));
    updateCartUI(cart);
    console.log(cart)
}

document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', addToCart);
});

function addToCart(event) {
    const button = event.target;
    const productId = button.dataset.id;
    const productName = button.dataset.name;
    const productPrice = parseFloat(button.dataset.price);
    const productImage = button.dataset.image;

    console.log(productId, productName, productPrice, productImage)
    
    if (cart[productId]) {
        cart[productId].quantity += 1;
    } else {
        cart[productId] = {
            id: productId,
            name: productName,
            price: productPrice,
            image: productImage,
            quantity: 1
        };
    }
    localStorage.setItem('cart', JSON.stringify(cart));

    updateCartUI(cart);
}

function updateCartUI(cart) {
  const cartDropdown = document.querySelector('.dropdown-menu.carts');
  const cartBadge = document.querySelector('.badge-number.cart');
  cartDropdown.innerHTML = '';

  var sum = 0;
  for(var prd in cart){
    sum = sum + cart[prd].quantity;
  }
  cartBadge.textContent = sum;

  const cartItemsCount = Object.keys(cart).length;
  if (cartItemsCount > 0) {
      const cartHeader = document.createElement('li');
      cartHeader.classList.add('dropdown-header');
      cartHeader.textContent = `You have ${cartItemsCount} products in your cart`;
      cartDropdown.appendChild(cartHeader);

      const cartDivider = document.createElement('li');
      cartDivider.innerHTML = `<hr class="dropdown-divider">`;
      cartDropdown.appendChild(cartDivider);

      for (const productId in cart) {
          const item = cart[productId];

          const cartItem = document.createElement('li');
          cartItem.classList.add('cart-item');
          cartItem.innerHTML = `
            <a href="#">
              <img src="${item.image}" alt="" class="rounded-circle">
              <div>
                <h4>${item.name}</h4>
                <p>Price: ${item.price}</p>
                <p>Quantity: ${item.quantity}</p>
                <p>Total: ${(item.price * item.quantity)}</p>
              </div>
            </a>`;
          cartDropdown.appendChild(cartItem);

          const cartItemDivider = document.createElement('li');
          cartItemDivider.innerHTML = `<hr class="dropdown-divider">`;
          cartDropdown.appendChild(cartItemDivider);
      }
  } else {
      const emptyCartMessage = document.createElement('li');
      emptyCartMessage.classList.add('dropdown-header');
      emptyCartMessage.textContent = 'Your cart is empty';
      cartDropdown.appendChild(emptyCartMessage);
  }
}
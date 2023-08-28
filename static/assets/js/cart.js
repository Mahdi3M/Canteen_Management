if (localStorage.getItem('cart') == null) {
    var cart = {};
    updateCartUI(cart);
    console.log("Hello",cart);
} else {
    cart = JSON.parse(localStorage.getItem('cart'));
    updateCartUI(cart);
    console.log("Hello",cart);
}

document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', addToCart);
});

function addToCart(event) {
    const button = event.target;
    const productId = button.dataset.id;
    const productName = button.dataset.name;
    const productAvailable = button.dataset.available;
    const productPrice = parseFloat(button.dataset.price);
    const productImage = button.dataset.image;

    console.log(productId, productName, productPrice, productImage, productAvailable)
    
    if (cart[productId]) {
        if(cart[productId].quantity<cart[productId].available){
            cart[productId].quantity += 1;
        } else{
          alert("No Items Left...")
        }   
    } else {
        cart[productId] = {
            id: productId,
            name: productName,
            price: productPrice,
            image: productImage,
            available: productAvailable,
            quantity: 1
        };
    }
    localStorage.setItem('cart', JSON.stringify(cart));

    updateCartUI(cart);
}

function clearCart(){
  cart = {};
  localStorage.removeItem('cart');
  updateCartUI(cart);
}

function plusProduct(productId){
  const item = cart[productId];
  if (item) {
    if(item.quantity < item.available){
      item.quantity += 1;
      localStorage.setItem('cart', JSON.stringify(cart));
      updateCartUI(cart);
    } else{
      alert("No Items Left...");
    }   
  } else {
    alert("Error...");
  }
}

function minusProduct(productId) {
  const item = cart[productId];
  if (item && item.quantity > 0) {
      item.quantity--;
      localStorage.setItem('cart', JSON.stringify(cart));
      updateCartUI(cart);
  } 
  // else {
  //   delete cart[productId];
  //   localStorage.setItem('cart', JSON.stringify(cart));
  //   updateCartUI(cart);
  // }
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
            <div class="d-flex">
              <div>
                <img src="${item.image}" alt="" class="rounded-circle">
                <div class="me-2 mt-3">
                  <button class="plus-button border-0 bg-white p-0" onclick="plusProduct('${productId}')">
                    <h6><span class="badge bg-success">+</span></h6>
                  </button>
                  <button class="minus-button border-0 bg-white" onclick="minusProduct('${productId}')">
                    <h6><span class="badge bg-danger">-</span></h6>
                  </button>
                </div>
              </div>
              <div>
                <h4>${item.name}</h4>
                <p>Price: ${item.price} Tk</p>
                <p>Quantity: ${item.quantity}</p>
                <p>Total: ${(item.price * item.quantity)} Tk</p>
              </div>
            </div>`;
          cartItem.addEventListener('click', event => event.stopPropagation());
          cartDropdown.appendChild(cartItem);

          const cartItemDivider = document.createElement('li');
          cartItemDivider.innerHTML = `<hr class="dropdown-divider">`;
          cartDropdown.appendChild(cartItemDivider);
      }
      
      const cartFooter = document.createElement('li');
      cartFooter.classList.add('dropdown-footer');
      cartFooter.classList.add('d-flex');
      cartFooter.classList.add('justify-content-between');

      const clearCartButton = document.createElement('button');
      clearCartButton.classList.add('btn', 'btn-danger');
      clearCartButton.textContent = 'Clear Cart';
      clearCartButton.classList.add('clear-cart-button');
      clearCartButton.setAttribute('onclick', 'clearCart()');
      cartFooter.appendChild(clearCartButton);

      const checkoutLink = document.createElement('a');
      checkoutLink.classList.add('btn', 'btn-primary', 'text-decoration-none', 'text-white', 'checkout-link');
      checkoutLink.textContent = 'Checkout';
      checkoutLink.href = "#";
      checkoutLink.classList.add('checkout-link');
      cartFooter.appendChild(checkoutLink);
      
      cartDropdown.appendChild(cartFooter);
  } else {
      const emptyCartMessage = document.createElement('li');
      emptyCartMessage.classList.add('dropdown-header');
      emptyCartMessage.textContent = 'Your cart is empty';
      cartDropdown.appendChild(emptyCartMessage);
  }
}
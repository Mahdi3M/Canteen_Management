const cartList = document.getElementById('cart-list');
const checkoutList = document.getElementById('checkout-list');
const scanList = document.getElementById('scan-list');

if (localStorage.getItem('cart') == null) {
    var cart = {};
} else {
    cart = JSON.parse(localStorage.getItem('cart'));
}

if (cartList) {
  updateCartUI(cart);
}
if (checkoutList) {
  updateCheckoutUI(cart);
}
if (scanList) {
  updateScanUI(cart);
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

  // console.log(productId, productName, productPrice, productImage, productAvailable)
  
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

  if (cartList) {
    updateCartUI(cart);
  }
  if (checkoutList) {
    updateCheckoutUI(cart);
  }
}

function addToScan(id, name, price, available, image){
  price = parseFloat(price);
  if (cart[id]) {
    if(cart[id].quantity<cart[id].available){
      cart[id].quantity += 1;
    } else{
      alert("No Items Left...")
    }   
  } else {
    cart[id] = {
      id: id,
      name: name,
      price: price,
      image: image,
      available: available,
      quantity: 1
    };
  }
  localStorage.setItem('cart', JSON.stringify(cart));
  console.log(cart)
}

function clearCart(){
  cart = {};
  localStorage.removeItem('cart');
  if (cartList) {
    updateCartUI(cart);
  }
  if (checkoutList) {
    updateCheckoutUI(cart);
  }
}

function plusProduct(productId){
  const item = cart[productId];
  if (item) {
    if(item.quantity < item.available){
      item.quantity += 1;
      localStorage.setItem('cart', JSON.stringify(cart));
      if (cartList) {
        updateCartUI(cart);
      }
      if (checkoutList) {
        updateCheckoutUI(cart);
      }
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
      if (cartList) {
        updateCartUI(cart);
      }
      if (checkoutList) {
        updateCheckoutUI(cart);
      }
  } 
  // else {
  //   delete cart[productId];
  //   localStorage.setItem('cart', JSON.stringify(cart));
  //   updateCartUI(cart);
    // if (checkoutList) {
    //   updateCheckoutUI(cart);
    // }
  // }
}


function removeProduct(productId){
  delete cart[productId];
  localStorage.setItem('cart', JSON.stringify(cart));
  if (cartList) {
    updateCartUI(cart);
  }
  if (checkoutList) {
    updateCheckoutUI(cart);
  }
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
            <div class="d-flex position-relative">
              <button class="btn btn-circle position-absolute top-0 end-0 p-0 m-0" aria-label="Close" onclick="removeProduct('${productId}')">
                  <i class="bi bi-x-circle"></i>
              </button>
              <div>
                <img src="${item.image}" class="rounded-circle">
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

      const checkoutLink = document.createElement('a');
      checkoutLink.classList.add('btn', 'btn-primary', 'text-decoration-none', 'text-white', 'checkout-link');
      checkoutLink.textContent = 'Checkout';
      checkoutLink.href = '/customer_checkout/';
      checkoutLink.classList.add('checkout-link');
      cartFooter.appendChild(checkoutLink);

      const clearCartButton = document.createElement('button');
      clearCartButton.classList.add('btn', 'btn-danger');
      clearCartButton.textContent = 'Clear Cart';
      clearCartButton.classList.add('clear-cart-button');
      clearCartButton.setAttribute('onclick', 'clearCart()');
      cartFooter.appendChild(clearCartButton);
      
      cartDropdown.appendChild(cartFooter);
  } else {
      const emptyCartMessage = document.createElement('li');
      emptyCartMessage.classList.add('dropdown-header');
      emptyCartMessage.textContent = 'Your cart is empty';
      cartDropdown.appendChild(emptyCartMessage);
  }
}



function updateCheckoutUI (cart){
  if (Object.keys(cart).length == 0) {
    checkoutList.innerHTML = '<div class="d-flex justify-content-center" style="width:100%;"><h1>Your Cart is Empty.</h1></div>';
    document.querySelector('.total').style.display = 'none';
  } else {
    checkoutList.innerHTML = '';
    document.querySelector('.total').style.display = 'flex';
  }

  var sum = 0;
  for(var prd in cart){
    sum = sum + (cart[prd].price * cart[prd].quantity);
  }

  for (const productId in cart) {
    const item = cart[productId];

    const listItem = document.createElement('li');
    listItem.classList.add('card', 'mb-3', 'mx-5', 'p-3', 'col-lg-5', 'col-md-7');

    const itemDetails = `
    <div class="d-flex flex-column">
      <h3 class="ms-md-3 mb-0">${item.name.length > 15 ? item.name.substring(0, 12) + '...' : item.name}</h3>

      <hr>
      <div class="d-flex flex-column flex-md-row">
        <div class="d-flex justify-content-center" style="width:150px">
            <img src="${item.image}" alt="Product 1" class="mx-auto my-auto" width=100px>
        </div>
        <div class="d-flex flex-column" style="width: 100%;">
          <div class="ms-lg-3">
            <p class="mt-3">Available: ${item.available}</p>
            <p>
              Quantity: ${item.quantity}
              <button class="plus-button border-0 bg-white p-0 ms-4" onclick="plusProduct('${productId}')">
                <h6><span class="badge bg-success">+</span></h6>
              </button>
              <button class="minus-button border-0 bg-white p-0" onclick="minusProduct('${productId}')">
                <h6><span class="badge bg-danger">-</span></h6>
              </button>
            </p>
            <p>Price: ${item.price} Tk</p>
          </div>
          <div class="d-flex flex-column flex-md-row justify-content-between align-items-center">
            <p id="cart-total" class="my-0 ms-lg-3 ms-sm-0 mb-3 mb-md-0">Total: ${item.quantity * item.price} Tk</p>
            <button class="checkout-remove btn btn-danger my-0" onclick="removeProduct('${productId}')">Remove</button>
          </div>
        </div>
      </div>
    </div>
    `;

    listItem.innerHTML = itemDetails;
    checkoutList.appendChild(listItem);
  }

  if (Object.keys(cart).length != 0) {
    document.getElementById('checkout-grand-total').textContent = sum;
    $('#cartJson').val(JSON.stringify(cart));
    $('#cartTotal').val(JSON.stringify(sum));
  }

// const totalCost = calculateTotalCost(cart);
// const totalCostElement = document.getElementById('cart-total');
// totalCostElement.textContent = `Total: ৳${totalCost.toFixed(2)}`;

}


function updateScanUI(cart) {
 
}
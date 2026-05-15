function addToCart(name, price){
    let cart = JSON.parse(localStorage.getItem("cart")) || [];

    cart.push({
        name: name,
        price: Number(price)
    });

    localStorage.setItem("cart", JSON.stringify(cart));
    alert("Added to cart 🛒");
}

function toggleFavorite(shopName){
    let favorites = JSON.parse(localStorage.getItem("favorites")) || [];

    if(favorites.includes(shopName)){
        favorites = favorites.filter(item => item !== shopName);
        alert("Removed from favorites");
    }else{
        favorites.push(shopName);
        alert("Added to favorites ❤️");
    }

    localStorage.setItem("favorites", JSON.stringify(favorites));
}

function toggleProductFavorite(name, price, image){
    let favorites = JSON.parse(localStorage.getItem("favoriteProducts")) || [];

    let exists = favorites.find(item => item.name === name);

    if(exists){
        favorites = favorites.filter(item => item.name !== name);
        alert("Removed from favorites");
    }else{
        favorites.push({
            name: name,
            price: Number(price),
            image: image
        });
        alert("Added to favorite products ❤️");
    }

    localStorage.setItem("favoriteProducts", JSON.stringify(favorites));
}
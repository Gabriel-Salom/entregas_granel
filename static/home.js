api_url_chart = '/produtos';

  
$.getJSON(api_url_chart, function(data) {
    for(var i =0; i < data.length; i++){
        
        var body = document.getElementById('content');

        var clickable = document.createElement('a');
        var product = document.createElement('div');
        var productImg = document.createElement('img');
        var productName = document.createElement('p');
        var productPrice = document.createElement('p');

        clickable.setAttribute('id', 'click' + i);
        product.setAttribute('id', 'product' + i);
        productImg.setAttribute('id', 'product-img' + i);
        productName.setAttribute('id', 'product-name' + i);
        productPrice.setAttribute('id', 'product-price' + i);

        body.appendChild(clickable);
        clickable.appendChild(product);
        product.appendChild(productImg); 
        product.appendChild(productName); 
        product.appendChild(productPrice); 

        clickable.setAttribute('href', "{{url_for(#)}")
        product.setAttribute('class', 'product');
        productImg.setAttribute('class', 'product-img');
        productName.setAttribute('class', 'product-name');
        productPrice.setAttribute('class', 'product-price');

        productName.innerHTML = "<span>" +data[i].Nome + "</span>";
        productPrice.innerHTML = "R$ <span>" +data[i].ValorUnitario + "</span>/" +data[i].Unidade;
        
        newImage = new Image();
        newImage.src = 'static/product_images/' + data[i].UrlImagem +'.png';
        productImg.src = newImage.src;

    }
})
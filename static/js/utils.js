$(document).ready(function($){

  document.querySelectorAll('a.nav-link[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();

      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });

  var elem = $('.new-product-name');
  var max_height = 0;
  for (var index = 0; index < $(elem).length; index++)
  {
    if ($(elem[index]).height() > max_height){
      max_height = $(elem[index]).height();
    }
  }

  $('.new-product-name').each(function(){
    $(this).height(max_height);
  });

  var searching_elem = $('.search-product-name');
  var searching_max_height = 0;
  for (var index = 0; index < $(searching_elem).length; index++)
  {
    if ($(searching_elem[index]).height() > searching_max_height){
      searching_max_height = $(searching_elem[index]).height();
    }
  }

  $('.search-product-name').each(function(){
    $(this).height(searching_max_height);
  });

  var filtering_elem = $('.filter-product-name');
  var filtering_max_height = 0;
  for (var index = 0; index < $(filtering_elem).length; index++)
  {
    if ($(filtering_elem[index]).height() > filtering_max_height){
      filtering_max_height = $(filtering_elem[index]).height();
    }
  }

  $('.filter-product-name').each(function(){
    $(this).height(filtering_max_height);
  });

  $('#category-select').change(function(){
    $('input[name="selected-category"]').val($('#category-select option:selected').text());
    $('input[name="selected-subcategory"]').val($('#subcategory-select option:selected').text());
    $('#pricelist-form').submit();
  });

  $('#search-category-select').change(function(){
    $('input[name="category"]').val($('#search-category-select option:selected').text());
    $('#search-form').submit();
  });

  $('#new-goods-container .new-price').each(function() {
    var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    $(this).html(new_price_format + ' ₽');
  });

  $('#new-goods-container .new-product-price').each(function() {
    var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    $(this).html(new_price_format + ' ₽');
  });

  $('#menu-on-sale-wrapper #menu-on-sale .pr-sale-price').each(function() {
    var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    $(this).html(new_price_format + ' ₽');
  });

  $('#menu-watched-products-wrapper #menu-watched-products-content .watched-product-item .pr-watched-price').each(function(){
    var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    $(this).html(new_price_format + ' ₽');
  });

  $('.product-detail-item .product-sizes span').on('click', function(){
    $('.product-detail-item .product-sizes span').removeAttr('is-active');
    $(this).attr('is-active', 'true');
    var new_price_format = $(this).attr('price-value').replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    $('.product-detail-item .product-price span:nth-child(2n)').html(new_price_format);

    var product_size_id = $(this).attr('product-size-id');
    data = {
        csrfmiddlewaretoken: csrftoken,
        product_size_id: product_size_id
    }
    $.ajax({
        type: "POST",
        url: select_product_color_url,
        data: data,
        success: function(data){
            var clear_data = data.colors;
            $('#collapseOne .row').empty();
            $.each(clear_data, function(index, color_item){
                $('#collapseOne .row').append(
                '<div class="col-xl-6">\
                    <label class="image-radio" prev-price="' + color_item[4] + '" color-price="' + color_item[3] + '">\
                        <img src="' + color_item[0] + '" class="img-fluid">\
                        <input type="radio" name="image-radio-input">\
                        <i class="fa fa-check" style="display: none;" aria-hidden="true"></i>\
                    </label>\
                </div>');
            });
        }
    })

  });

  $('#error_1_id_username').css('display', 'none');
  
  /* divide price value in subcategory */
  (function() {
    $('#category-subcategory-detail .filter-category-wrapper .filter-product-item .filter-product-price-nosale').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format + ' ₽');
    });

    $('#category-subcategory-detail .filter-category-wrapper .filter-product-item .filter-product-price').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format + ' ₽');
    });

    $('#category-subcategory-detail .filter-category-wrapper .filter-product-item .new-price').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format + ' ₽');
    });

  })();

  /* divide price value in pricelist */
  (function() {
    $('#price-list-content .main-content .product-price').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format);
    });
  })();

  /* divide price in product detail template */
  (function() {
    $('#product-detail-wrapper .main-content .product-detail-item table .product-price').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format + ' ₽');
    });
  })();

  /* divide price in comparison */
  (function() {
    $('#compare-content .main-content .comparison .product-price').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format + ' ₽');
    });
  })();

  (function() {
    $('.item-price-total').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format);
    });
  })();

  (function() {
    $('.per-item-price').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format);
    });
  })();

  (function() {
    $('.cart-total-price').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html("<b>" + new_price_format + "</b>");
    });
  })();

   (function() {
    $('.search-product-price').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format + ' ₽');
    });
  })();

  (function() {
    $('.search-product-price-nosale').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format + ' ₽');
    });
  })();

  (function() {
    $('.search-product-item .new-price').each(function(){
      var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
      $(this).html(new_price_format + ' ₽');
    });
  })();

  (function() {
    $('.product-price-value').each(function(){
        var new_price_format = $(this).text().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        $(this).html(new_price_format);
    });
  })();

  /* sort products  */
  $('.sort-products span').on('click', function() {
    $('.sort-products input[name="sort"]').val($(this).attr('sort-query'));
    $('.sort-products').submit();
  });

  $(".image-radio").each(function(){
    if($(this).find('input[type="radio"]').first().attr("checked")){
      $(this).addClass('image-radio-checked');
    }else{
      $(this).removeClass('image-radio-checked');
    }
  });

    // sync the input state
    $("#collapseOne").on("click", ".image-radio", function(e){
        if (!($(this).hasClass('image-radio-checked'))){
            $(".image-radio").removeClass('image-radio-checked');
            $(this).addClass('image-radio-checked');
            var $radio = $(this).find('input[type="radio"]');
            $radio.prop("checked",!$radio.prop("checked"));
            var color_price = $(this).attr('color-price');
            var color_price_format = color_price.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
            $('.product-detail-item .product-price span:nth-child(2n)').html(color_price_format);
        }
        else{
            $(".image-radio").removeClass('image-radio-checked');
            var color_price = $(this).attr('prev-price');
            var color_price_format = color_price.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
            $('.product-detail-item .product-price span:nth-child(2n)').html(color_price_format);

        }
        e.preventDefault();
    });

    /* slider changes */
    (function() {
      var parent = document.querySelector(".price-slider");
      if(!parent) return;
      var rangeS = parent.querySelectorAll("input[type=range]");
      rangeS.forEach(function(el) {
        el.oninput = function() {
          var slide1 = parseFloat(rangeS[0].value),
          slide2 = parseFloat(rangeS[1].value);
          if (slide1 > slide2) {
            [slide1, slide2] = [slide2, slide1];
          }
          $('.price-slider .to-price').html(slide2);
          $('.price-slider .from-price').html(slide1);
          $('input[name="from"]').val($('.price-slider .from-price').text());
          $('input[name="to"]').val($('.price-slider .to-price').text());
        }
      });
    })();

    function getCrsfCookie(name){
      var cookieValue = null;
      if (document.cookie && document.cookie !== ''){
        var cookies = document.cookie.split(';')
        for (var index = 0; index < cookies.length; index++){
          var cookie = jQuery.trim(cookies[index]);
          if (cookie.substring(0, name.length + 1) === (name + "=")){
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }

    var csrftoken = getCrsfCookie('csrftoken');

    $('.item-compare').on('click', function(){
      var compare_items_count = parseInt($('.compare-products span').html());
      if (compare_items_count == 4)
      {
        flash('Для сравнения можно выбрать только 4 товара.', {
          'bgColor': 'red'
        });
      }
      else
      {
        var product_id = $(this).attr('product-id');
        data = {
          product_id: product_id,
          csrfmiddlewaretoken: csrftoken
        }
        $.ajax({
          type: "POST",
          data: data,
          url: add_to_comparison_url,
          success: function(data){
            $('.compare-products span').html(data.total_comparison);
            flash('Товар добавлен в сравнение!', {
                'bgColor': 'green'
            });
          }
        });
      }
    });

    $('.item-add-to-card').on('click', function(){
        var size_chosen = false;
        var if_sizes_exists = false;
        $('.product-sizes span').each(function(){
            if_sizes_exists = true;
            if ($(this).attr('is-active') == 'true') {
                size_chosen = true;
            }
        });
        if (if_sizes_exists && !size_chosen) {
            flash('Вы не выбрали размер товара.', {
                'bgColor': 'red'
            });
        }
        else{
            if (if_sizes_exists){
                var product_id = $('.product-sizes span[is-active="true"]').attr('product-size-id');
            }
            else{
                var product_id = $(this).attr('product-id');
            }
            data = {
                product_id: product_id,
                csrfmiddlewaretoken: csrftoken
            }
            $.ajax({
                type: "POST",
                url: add_to_cart_url,
                data: data,
                success: function(data){
                  $('.cart-products span').html(data.total);
                  flash('Товар добавлен в корзину!', {
                    'bgColor': 'green'
                    });
                }
            });
        }
    });

    $('.add-complect-to-cart').on('click', function(){
        var complect_counter = 0;
        var complect_dict = {};
        $('.complect-count').each(function(){
            if ($(this).val() != 0) {
                complect_dict[$(this).attr('complect-id')] = parseInt($(this).val());
                complect_counter++;
            }
        });
        if (complect_counter == 0) {
            flash('Укажите количество комплектующих', {
                'bgColor': 'red'
            });
        }
        else {
            complect_dict['csrfmiddlewaretoken'] = csrftoken;
            $.ajax({
                type: "POST",
                url: add_complect_to_cart,
                data: complect_dict,
                success: function(data){
                    $('.cart-products span').html(data.total);
                    flash('Товар добавлен в корзину!', {
                        'bgColor': 'green'
                    });
                }
            });
        }
    });

    $('input[name="profile-phone"]').mask('9(999)999-99-99');

    $('#edit-profile-info').on('click', function(){
      $('#save-profile-info').css('display', 'inline-block');
      $('#profile-wrapper #profile-content .main-content .no-phone').attr('type', 'tel');
      $('#profile-wrapper #profile-content .main-content .no-phone').attr('name', 'profile-phone');
      $('#profile-wrapper #profile-content .main-content .no-phone').removeClass('no-phone');
      $('input[name="profile-phone"]').mask('9(999) 999-99-99');
      $('#profile-wrapper #profile-content .main-content input').removeAttr('readonly');
      $('#profile-wrapper #profile-content .main-content .only-read').attr('readonly', 'true');
      $('#profile-wrapper #profile-content .main-content input:not([class="only-read"])').css({
        'border-width': '1px',
        'border-style': 'solid',
        'border-color': 'lightgray'
      });
    });

    $('#send-feedback').on('click', function(){
        if ($('#send-feedback-form').valid()){
            var name = $('#id_name').val();
            var email_from = $('#id_email').val();
            var message = $('#id_message').val();
            data = {
                name: name,
                email_from: email_from,
                message: message,
                csrfmiddlewaretoken: csrftoken
            }
            $.ajax({
                type: "POST",
                url: send_feedback_url,
                data: data,
                success: function(data) {
                    // alert(1);
                }
            });
        }
    });

});
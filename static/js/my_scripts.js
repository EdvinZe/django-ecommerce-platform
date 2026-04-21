$("#changePassForm").submit(function (event) {
  var pass1 = $("#new_password1").val();
  var pass2 = $("#new_password2").val();

  $("#messageSuccess").addClass("d-none");
  $("#messageError").addClass("d-none");

  if (pass1 === pass2 && pass1 !== "") {
    $("#messageSuccess").removeClass("d-none");
  } else {
    $("#messageError").removeClass("d-none");
    return false;
  }
});

$(document).ready(function () {
  var successMessage = $("#jq-notification");

  $(document).on("click", ".add-to-cart", function (e) {
    e.preventDefault();

    $.ajax({
      type: "POST",
      url: $(this).attr("href"),
      data: {
        product_id: $(this).data("product-id"),
        csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
      },
      // success: function (data) {
      //   successMessage.html(data.message).fadeIn(300);
      //   setTimeout(function () { successMessage.fadeOut(400); }, 7000);

      //   if (data.success === false) return;

      //   if (data.cart_count !== undefined) {
      //     $("#products-in-cart-count").text(data.cart_count);
      //   }

      //   $("#cart-items-container").html(data.cart_items_html);
      // },

      success: function (data) {

        successMessage.html(data.message).fadeIn(300);
        setTimeout(function () { successMessage.fadeOut(400); }, 7000);
      
        if (data.success === false) return;
      
        // СНАЧАЛА перерисовываем корзину
        $("#cart-items-container").html(data.cart_items_html);
      
        // ПОТОМ обновляем число
        if (data.cart_count !== undefined) {
          $("#products-in-cart-count").text(data.cart_count);
        }
      },
      
      error: function () {
        console.log("Įdedant prekę į krepšelį įvyko klaida");
      },
    });
  });

  $(document).on("click", ".remove-from-cart", function (e) {
    e.preventDefault();

    $.ajax({
      type: "POST",
      url: $(this).attr("href"),
      data: {
        cart_id: $(this).data("cart-id"),
        csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
      },
      success: function (data) {
        successMessage.html(data.message).fadeIn(300);
        setTimeout(function () { successMessage.fadeOut(400); }, 7000);

        if (data.success === false) return;

        if (data.cart_count !== undefined) {
          $("#products-in-cart-count").text(data.cart_count);
        }

        $("#cart-items-container").html(data.cart_items_html);
      },
      error: function () {
        console.log("Įdedant prekę į krepšelį įvyko klaida");
      },
    });
  });

  $(document).on("click", ".decrement", function () {
    var url = $(this).data("cart-change-url");
    var cartID = $(this).data("cart-id");
    var $input = $(this).closest(".input-group").find(".number");
    var currentValue = parseInt($input.val());

    if (currentValue > 1) {
      updateCart(cartID, currentValue - 1, url, $input);
    }
  });

  $(document).on("click", ".increment", function () {
    var url = $(this).data("cart-change-url");
    var cartID = $(this).data("cart-id");
    var $input = $(this).closest(".input-group").find(".number");
    var currentValue = parseInt($input.val());

    updateCart(cartID, currentValue + 1, url, $input);
  });
  
  function updateCartCounter(cartCount) {
    $("#products-in-cart-count").text(cartCount);
  }
  

  function updateCart(cartID, quantity, url, $input) {
    $.ajax({
      type: "POST",
      url: url,
      data: {
        cart_id: cartID,
        quantity: quantity,
        csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
      },
      success: function (data) {
        successMessage.html(data.message).fadeIn(400);
        setTimeout(function () { successMessage.fadeOut(400); }, 7000);

        if (data.success === false) return;

        if (data.item_quantity !== undefined) {
          $input.val(data.item_quantity);
        } else {
          $input.val(quantity);
        }

        if (data.cart_count !== undefined) {
          $("#products-in-cart-count").text(data.cart_count);
        }

        $("#cart-items-container").html(data.cart_items_html);
      },

      error: function () {
        console.log("Įdedant prekę į krepšelį įvyko klaida");
      },
    });
  }
});


$(document).ready(function () {

  var counter = 60;
  var resendLink = $("#resendCodeLink");
  var interval;

  var toastElement = document.getElementById("liveToast");
  var toast = new bootstrap.Toast(toastElement, { delay: 3000 });

  function disableLink() {
    resendLink
      .addClass("disabled")
      .css({ "pointer-events": "none", "opacity": 0.5 });
  }

  function enableLink() {
    resendLink
      .removeClass("disabled")
      .css({ "pointer-events": "auto", "opacity": 1 })
      .text("Gauti kodą pakartotinai");
  }

  function StartCountdown(seconds) {
    counter = seconds;
    disableLink();
    resendLink.text("Gauti kodą pakartotinai (" + counter + ")");

    interval = setInterval(function () {
      counter--;
      resendLink.text("Gauti kodą pakartotinai (" + counter + ")");
      if (counter <= 0) {
        clearInterval(interval);
        enableLink();
      }
    }, 1000);
  }

  StartCountdown(60);

  resendLink.click(function () {
    if (resendLink.hasClass("disabled")) return;

    toast.show();
    StartCountdown(60);
  });
});


$(document).ready(function () {
  let lockers = { omniva: [], dpd: [], lp: []};

  const strawberryMarker = L.divIcon({
    className: "custom-map-marker",
    html: `
      <div class="marker-wrapper">
          <div class="marker-pin"></div>
          <div class="marker-shadow"></div>
      </div>
    `,
    iconSize: [30, 42],
    iconAnchor: [15, 42],
    popupAnchor: [0, -35]
  });


  const map = L.map('map').setView([55.1694, 23.8813], 7);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  const markersById = {};
  const providerById = {};

  function addAllMarkers() {
    for (let provider in lockers) {
      lockers[provider].forEach(loc => {
        const marker = L.marker([loc.lat, loc.lng],  { icon: strawberryMarker })
          .addTo(map)
          .bindPopup(loc.name)
          .on("click", () => highlightListItem(loc.id));

        markersById[loc.id] = marker;
        providerById[loc.id] = provider;
      });
    }
  }

  function createLockerList() {
    const $list = $("#lockerList");
    $list.empty();

    for (let provider in lockers) {
      lockers[provider].forEach(loc => {
        const $item = $("<button>")
          .attr("type", "button")
          .addClass("list-group-item list-group-item-action locker-item")
          .attr("data-id", loc.id)
          .attr("data-provider", provider)
          .text(`${loc.name} (${provider.toUpperCase()})`)
          .on('click', function () {
            const marker = markersById[loc.id];
            if (marker) {
              map.setView(marker.getLatLng(), 14);
              marker.openPopup();
              highlightListItem(loc.id);
            }
          });

        $list.append($item);
      });
    }
  }

  $("#lockerSearch").on("input", function () {
    const query = $(this).val().toLowerCase().trim();

    $(".locker-item").each(function () {
      const text = $(this).text().toLowerCase();
      $(this).toggle(text.includes(query));
    });
  });


  function highlightListItem(id) {
    $(".locker-item").removeClass("active");
    $('.locker-item[data-id="' + id + '"]').addClass("active");

    $("#selectedLockerId").val(id);

    let selectedLocker = null;
    let selectedProvider = null;

    for (let provider in lockers) {
      const found = lockers[provider].find(lock => lock.id === id);
      if (found) { selectedLocker = found; selectedProvider = provider; break; }
    }

    if (selectedLocker) {
      $("#lockerAddress").val(selectedLocker.name);
      $("#locker_company").val(selectedProvider);
    }
  }

  function updateUI() {
    const deliveryType = $('input[name="delivery_method"]:checked').val();
    if (deliveryType === "parcel") {
      $("#lockerBlock").show();
      $("#cash1").prop("disabled", true).prop("checked", false);
      $("#card1").prop("disabled", false);
    } else {
      $("#lockerBlock").hide();
      $("#cash1").prop("disabled", false);
      $("#card1").prop("disabled", false);
    }
  }

  function initLockers() {
    addAllMarkers();
    createLockerList();
    updateUI();
  }
  // here
  fetch("/lockers/all/")
    .then(res => res.json())
    .then(data => {
      lockers = { omniva: [], dpd: [], lp: [] };

      data.forEach(loc => {
        if (!lockers[loc.provider]) return;
        lockers[loc.provider].push(loc);
      });
      

      initLockers();
    })
    .catch(err => console.error("Failed to load lockers:", err));


  $("#providerFilter").on("change", function () {
    const provider = $(this).val();

    $(".locker-item").each(function () {
      const itemProvider = $(this).data("provider");
      const isVisible = provider === "all" || itemProvider === provider;
      $(this).toggle(isVisible);
    });

    for (let id in markersById) {
      const marker = markersById[id];
      const shouldShow = provider === "all" || providerById[id] === provider;
      if (shouldShow) marker.addTo(map);
      else map.removeLayer(marker);
    }
  });

  $('input[name="delivery_method"]').change(updateUI);
});


// const form = document.getElementById("orderForm");
// form.addEventListener("submit", function(event) {
//     event.preventDefault();
//     const paymentMethod = document.querySelector('input[name="choisePayment"]:checked').value;

//     if(paymentMethod === "cash") {
//         form.action = ""
//         form.submit();
//     } else if(paymentMethod === "card") {
//         fetch("/create-stripe-session", {
//             method: "POST",
//             body: new FormData(form)
//         })
//         .then(response => response.json())
//         .then(data => {
//             window.location.href = data.checkoutURL
//         });
//     }
// });

document.addEventListener("DOMContentLoaded", function () {

  const swiper = new Swiper(".aboutSwiper", {
    slidesPerView: 3,
    slidesPerGroup: 3,
    spaceBetween: 30,
    loop: true,
    grabCursor: true,
  
    pagination: {
      el: ".gallery-pagination",
      clickable: true,
      renderBullet: function (index, className) {
        return '<span class="' + className + '">' + (index + 1) + '</span>';
      },
    },
  
    breakpoints: {
      0: { slidesPerView: 1, slidesPerGroup: 1 },
      768: { slidesPerView: 2, slidesPerGroup: 2 },
      1200: { slidesPerView: 3, slidesPerGroup: 3 },
    }
  });
  
  /* стрелки */
  document.querySelector(".gallery-next-inline").addEventListener("click", function() {
    swiper.slideNext();
  });
  
  document.querySelector(".gallery-prev-inline").addEventListener("click", function() {
    swiper.slidePrev();
  });

});

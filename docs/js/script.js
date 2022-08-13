//$(function() {
//  //		smoothScroll Function
//function smoothScroll(duration) {
//  $('a[href^="#"]').on('click', function (event) {
//    var target = $($(this).attr('href'));
//    if (target.length) {
//      event.preventDefault();
//      $('html, body').animate({
//        scrollTop: target.offset().top
//      }, duration);
//    }
//  });
//}
//
//  smoothScroll(800);
//});

function submitToSales() {
       var data = {
          name : $("#name").val(),
          phone : $("#phone").val(),
          email : $("#email").val(),
          company : $("#company").val()
       };
       $.ajax({
         type: "POST",
         url : "https://np67ghzr49.execute-api.us-east-1.amazonaws.com/dev/email/send",
         dataType: "json",
         crossDomain: "true",
         contentType: "application/json; charset=utf-8",
         data: JSON.stringify(data),
       });
       alert("Thank you for submitting the form. Our sales representative will contact you.");
       document.getElementById("contact-sales").reset();
     };

function submitToSupport() {
       var data = {
          name : $("#name").val(),
          phone : $("#phone").val(),
          email : $("#email").val(),
          company : $("#company").val(),
          product: $("#product").val(),
          issue: $("#issue").val()
       };
       $.ajax({
         type: "POST",
         url : "https://hxvixjj5s9.execute-api.us-east-1.amazonaws.com/dev/email/send",
         dataType: "json",
         crossDomain: "true",
         issueType: "application/json; charset=utf-8",
         data: JSON.stringify(data),
       });
       alert("Thank you for submitting the form. Our team will contact you shortly.");
       document.getElementById("contact-support").reset();
     };

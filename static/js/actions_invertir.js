$(document).ready(function() {
          $("#slider").slider({
              animate: true,
              value:1000,
              min: 1000,
              max: 5000,
              step: 250,
              slide: function(event, ui) {
                  update(1,ui.value);
              }
          });
          $("#slider2").slider({
              animate: true,
              value: 1,
              min: 1,
              max: 4,
              step: 1,
              slide: function(event, ui) {
                  update(2,ui.value);
              }
          });
          $("#cantidad").val(1000);
          $("#duracion").val(1);
          $("#cantidad-label").text(1000);
          $("#duracion-label").text(1);

          update();
      });
      function update(slider,val) {
        var $cantidad = slider == 1?val:$("#cantidad").val();
        var $duracion = slider == 2?val:$("#duracion").val();
        var $subtotal = ($cantidad / $duracion) * 1.15;
        $total = "$" + $subtotal.toFixed(2);
         $( "#cantidad" ).val($cantidad);
         $( "#cantidad-label" ).text($cantidad);
         $( "#duracion" ).val($duracion);
         $( "#duracion-label" ).text($duracion);
         $( "#total" ).val($subtotal);
         $( "#total-label" ).text($total);

         $('#slider a').html('<label><span class="glyphicon glyphicon-chevron-left"></span> '+$cantidad+' <span class="glyphicon glyphicon-chevron-right"></span></label>');
         $('#slider2 a').html('<label><span class="glyphicon glyphicon-chevron-left"></span> '+$duracion+' <span class="glyphicon glyphicon-chevron-right"></span></label>');
      }

$(document).ready(function(){

    $.fn.dataTable.moment('DD/MM/YYYY');

    //ADD INGREDIENT
    var type_ing = $("#id_type_ingredient").val();
    $('#title-ingredient-information-form').hide();
    $('#div_id_ebc_min').hide();
    $('#div_id_ebc_max').hide();
    $('#div_id_attenuation_min').hide();
    $('#div_id_attenuation_max').hide();
    $('#div_id_acide_alpha').hide();

    //ADD INGREDIENT TO BRASSIN
    $('#div_id_temps_infusion').hide();

    if (type_ing == 'malt'){$('#div_id_ebc_min').show();$('#div_id_ebc_max').show();}
    if (type_ing == 'levure'){$('#div_id_attenuation_min').show();$('#div_id_attenuation_max').show();}
    if (type_ing == 'houblon'){$('#div_id_acide_alpha').show();}
    if (type_ing == 'autre'){$('#title-ingredient-information-form').hide();}

});

//UPDATE °P / SG FORM
function calc_SG(str,input_name)
{
  var id_input_to_update = input_name.substring(0,input_name.length-2);
  if (str.length > 0 && !isNaN(str))
    console.log('\"#' + id_input_to_update + '\"');
  {
    $('#' + id_input_to_update).val(Math.round(conversion_P_D(str)*1000)/1000);
    return;
  }
}

function conversion_P_D(P)
{
  var D = 1+P/(258.6-0.88*P);
  return D ;
}

function conversion_D_P(D)
{
  var d = parseFloat(D);
  var P = -616.868 + 1111.14*D - 630.272*Math.pow(d,2.0) + 135.997*Math.pow(d,3.0);
  return P ;
}

//DIFFERENCE 2 DATES
function diff_date(date1, date2)
{
  //Get 1 day in milliseconds
  var one_day=1000*60*60*24;

  // Convert both dates to milliseconds
  var date1_ms = new Date(date1).getTime();
  var date2_ms = new Date(date2).getTime();

  // Calculate the difference in milliseconds
  var difference_ms = date2_ms - date1_ms;

  // Convert back to days and return
  return Math.round(difference_ms/one_day);
}
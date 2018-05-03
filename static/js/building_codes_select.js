var default_selected = [];
document.addEventListener("DOMContentLoaded", function(event) {

        var codes_select = document.getElementById("building_codes_select");
        for (code_i in building_codes.sort()) {
            var option = document.createElement("option");
            if (default_selected.indexOf(building_codes[code_i]) >= 0) {
                option.selected = true;
            }
            option.text = building_codes[code_i];
            option.value = building_codes[code_i];
            codes_select.add(option);
        }
     });
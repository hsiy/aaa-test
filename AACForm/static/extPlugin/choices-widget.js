/**
 * Function to instantiate the ChoicesJS dropdown for SLOs
 * @class choices-widget
 */

/**
 * On load, create the dropdown
 * @method DOMContentLoaded
 */
document.addEventListener("DOMContentLoaded", function() {
const ch = new Choices(document.getElementById('id_slo'),{shouldSort:false, removeItemButton:true});
});
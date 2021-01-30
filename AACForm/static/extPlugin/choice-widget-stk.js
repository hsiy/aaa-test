/**
 * Function to instantiate the ChoicesJS dropdown for stakeholders
 * @class choice-widget-stk
 */

/**
 * On load, create the dropdown
 * @method DOMContentLoaded
 */
document.addEventListener("DOMContentLoaded", function() {
const ch = new Choices(document.getElementById('id_stk'),{shouldSort:false, removeItemButton:true});
});
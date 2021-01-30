    /**
     * Functions to properly show and hide boxes on the assessment forms
     * @class assessmentBoxes
     */
    
    /**
     * On load, calls the change function for allStudents and frequencyChoice
     * @method onLoad
     */
    jQuery(window).on("load", function(){

        $('#id_allStudents').change();
        $('#id_frequencyChoice').change();

    });
    /**
     * When allStudents change, hide or show the box to describe students
     * 
     * @method allStudents.change
     */
    $('#id_allStudents').change(function(){
        if(this.value == "True"){
            document.getElementById('hide-sam').style.display = 'none';
        } else {
            document.getElementById('hide-sam').style.display = 'block';
        }
    });
    /**
     * When frequencyChoice changes, hide or show the box to describe the frequency
     * 
     * @method frequencyChoice.change
     */
    $('#id_frequencyChoice').change(function(){
        if(this.value != "O"){
            document.getElementById('hide-freq').style.display = 'none';
        } else {
            document.getElementById('hide-freq').style.display = 'block';
        }
    });
$(document).ready(function(){
    $(".gioi_tinh").change(function() {
        if(this.checked && this.name === 'nam'){
            $('#profile input[name=nu]').prop('checked', false);
        }
        else if(this.checked && this.name === 'nu'){
            $('#profile input[name=nam]').prop('checked', false);
        }
    });
});


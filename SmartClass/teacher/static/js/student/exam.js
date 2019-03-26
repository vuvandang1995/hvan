$(document).ready(function(){
    function get_de(de_id){
        $.ajax({
            type: 'GET',
            url: '/student/exam/data_'+ de_id,
            success: function(data){
                $("#load_de").html(data);
                $('input[type=checkbox]').change(function(){
                    check_checked($(this).data('id'),$(this).data('ch_id'));
                });
                $('input[type=text]').change(function(){
                    check_empty($(this).data('id'),$(this).data('ch_id'));
                });

                $('textarea').change(function(){
                    var text = $(this).val();
                    var id = $(this).data('id');
                    if (!text.replace(/\s/g, '').length) {
                        $("#stt_"+id).find('span').first().removeClass("label-success").addClass("label-danger");
                        $("#stt_"+id).find('i').first().removeClass('fa-check').addClass('fa-close');
                    }else{
                        $("#stt_"+id).find('span').first().removeClass("label-danger").addClass("label-success");
                        $("#stt_"+id).find('i').first().removeClass('fa-close').addClass('fa-check');
                    }

                });
            },
        });
    };
    time_remain = window.atob(time_remain);
    de_id = window.atob(de_id);
    if(parseInt(time_remain) > 0){
        get_de(de_id);
        setTimeout(function(){
            countdowntime(time_remain);
        },500)
    }
    else if (parseInt(time_remain) == 0){
        $("#load_de").html(`<div style="text-align:center">
        <h1>Thời gian làm bài đã hết</h1><a href="/" class="btn btn-lg btn-primary">
        <i class="fa fa-mail-reply"> Thoát</a></div>`);
    }else{
        $("#load_de").html(`<div style="text-align:center">
        <h1>Bạn đã nộp bài</h1><a href="/" class="btn btn-lg btn-primary">
        <i class="fa fa-mail-reply"> Thoát</a></div>`);
    }
});

function check_checked(id,ch_id){
    var ar = []
    $("input[name=dap_an_"+ch_id+"]").each(function(){
        if($(this).is(":checked")){
            ar.push(1);
        }else{
            ar.push(0);
        }
    });
    if (jQuery.inArray(1, ar) == -1){
        $("#stt_"+id).find('span').first().removeClass("label-success").addClass("label-danger");
        $("#stt_"+id).find('i').first().removeClass('fa-check').addClass('fa-close');
    }else{
        $("#stt_"+id).find('span').first().removeClass("label-danger").addClass("label-success");
        $("#stt_"+id).find('i').first().removeClass('fa-close').addClass('fa-check');
    }
}

function check_empty(id,ch_id){
    var ar = []
    $("input[name=dap_an_"+ch_id+"]").each(function(){
        ar.push($(this).val());
    })

    if (jQuery.inArray("", ar) == -1){
        $("#stt_"+id).find('span').first().removeClass("label-danger").addClass("label-success");
        $("#stt_"+id).find('i').first().removeClass('fa-close').addClass('fa-check');
    }else{
        $("#stt_"+id).find('span').first().removeClass("label-success").addClass("label-danger");
        $("#stt_"+id).find('i').first().removeClass('fa-check').addClass('fa-close');
    }
}

function nopBai(){
    if(confirm("Bạn có chắc chắn nộp bài không ?")){
        var ds_dap_an = {}
        $(".dap_an").each(function(){
            if($(this).data('kind') == 'tn'){
                if($(this).is(":checked")){
                    ds_dap_an[$(this).data('ch_id')+'_'+$(this).data("da_id")] = true;
                }else{
                    ds_dap_an[$(this).data('ch_id')+'_'+$(this).data("da_id")] = false;
                }
            }
            else {
                ds_dap_an[$(this).data('ch_id')+'_'+$(this).data("da_id")] = $(this).val();
            }
            $(this).prop("disabled", true);
        });
        $("#processing").modal({backdrop: 'static', keyboard: false});
        $.ajax({
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                xhr.upload.addEventListener("progress", function(event){
                    var percent = Math.round((event.loaded / event.total) * 100) + '%';
                    $("#progressBar").attr("style","width:"+percent);
                    $("#progressBar").text(percent);
//                    $("#loaded_n_total").html("Tải lên " + event.loaded + " bytes của " + event.total);
                }, false);
                $("#cancel_upload").click(function(){
                    xhr.abort();
                });
                return xhr;
              },
            type: 'POST',
            url: location.href,
            data:{'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val(),'de_id':$("input[name=de_id]").val(),
            'ds_dap_an':JSON.stringify(ds_dap_an)},
            success:function(){
                $("#processing").modal('hide');
                location.reload();
            },
        });
    }
};

function countdowntime(dateend){
    // $('.demo').each(function(){
        var countDownDate = new Date().getTime() + dateend*1000;
        // var p = $(this);
        // Update the count down every 1 second
        var x = setInterval(function() {

            // Get todays date and time
            var now = new Date().getTime();

            // Find the distance between now and the count down date
            var distance = countDownDate - now;

            // Time calculations for days, hours, minutes and seconds
            var minutes = Math.floor(distance / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            document.getElementById("tg_lam").innerHTML = minutes + ":" + seconds;
            if (distance < 0) {
                clearInterval(x);
                document.getElementById("tg_lam").innerHTML = "Hết giờ!";
                document.getElementById("load_de").innerHTML = `
                <div style="text-align:center"><h1>Thời gian làm bài đã hết</h1>
                <a href="/" class="btn btn-lg btn-primary"><i class="fa fa-mail-reply"> Thoát</a></div>`;
            }
        }, 1000);
    // });
}


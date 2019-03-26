$(document).ready(function(){
    $("#ck_tn").change(function() {
        if(this.checked) {
            $("input[name=sl_tn]").prop("disabled",false);
            $("input[name=pt_tn]").prop("disabled",false);
            chon_tn = 0;
            max_tn = parseInt($("input[name=sl_tn]").val());
            $("#max_tn").html("Trắc nhiệm: "+chon_tn+ "/" + max_tn);
        }
        else{
            $("input[name=sl_tn]").prop("disabled",true);
            $("input[name=pt_tn]").prop("disabled",true);
            chon_tn = 0;
            max_tn = 0;
            $("#max_tn").html("Trắc nhiệm: "+chon_tn+ "/" + max_tn);
            $(".dch").each(function(){
                if(($(this).val()).includes("Trắc nhiệm")){
                    var row = $(this).parent().parent();
                    table_ques_selected.row(row).remove().draw();
                }
            });
        }
    });

    $("#ck_dt").change(function() {
        if(this.checked) {
            $("input[name=sl_dt]").prop("disabled",false);
            $("input[name=pt_dt]").prop("disabled",false);
            chon_dt = 0;
            max_dt = parseInt($("input[name=sl_dt]").val());
            $("#max_dt").html("Điền từ: "+chon_dt+ "/" + max_dt);
        }
        else{
            $("input[name=sl_dt]").prop("disabled",true);
            $("input[name=pt_dt]").prop("disabled",true);
            chon_dt = 0;
            max_dt = 0;
            $("#max_dt").html("Điền từ: "+chon_dt+ "/" + max_dt);
            $(".dch").each(function(){
                if(($(this).val()).includes("Điền từ")){
                    var row = $(this).parent().parent();
                    table_ques_selected.row(row).remove().draw();
                }
            });
        }
    });

    $("#ck_tl").change(function() {
        if(this.checked) {
            $("input[name=sl_tl]").prop("disabled",false);
            $("input[name=pt_tl]").prop("disabled",false);
            chon_tl = 0;
            max_tl = parseInt($("input[name=sl_tl]").val());
            $("#max_tl").html("Tự luận: "+chon_tl+ "/" + max_tl);
        }
        else{
            $("input[name=sl_tl]").prop("disabled",true);
            $("input[name=pt_tl]").prop("disabled",true);
            chon_tl = 0;
            max_tl = 0;
            $("#max_tl").html("Tự luận: "+chon_tl+ "/" + max_tl);
            $(".dch").each(function(){
                if(($(this).val()).includes("Tự luận")){
                    var row = $(this).parent().parent();
                    table_ques_selected.row(row).remove().draw();
                }
            });
        }
    });

    $("#ck_ga").change(function() {
        if(this.checked) {
            $("input[name=sl_ga]").prop("disabled",false);
            $("input[name=pt_ga]").prop("disabled",false);
            chon_ga = 0;
            max_ga = parseInt($("input[name=sl_ga]").val());
            $("#max_ga").html("Ghi âm: "+chon_ga+ "/" + max_ga);
        }
        else{
            $("input[name=sl_ga]").prop("disabled",true);
            $("input[name=pt_ga]").prop("disabled",true);
            chon_ga = 0;
            max_ga = 0;
            $("#max_ga").html("Ghi âm: "+chon_ga+ "/" + max_ga);
            $(".dch").each(function(){
                if(($(this).val()).includes("Ghi âm")){
                    var row = $(this).parent().parent();
                    table_ques_selected.row(row).remove().draw();
                }
            });
        }
    });

    $("#ck_gh").change(function() {
        if(this.checked) {
            $("input[name=sl_gh]").prop("disabled",false);
            $("input[name=pt_gh]").prop("disabled",false);
            chon_gh = 0;
            max_gh = parseInt($("input[name=sl_gh]").val());
            $("#max_gh").html("Ghi hình: "+chon_gh+ "/" + max_gh);
        }
        else{
            $("input[name=sl_gh]").prop("disabled",true);
            $("input[name=pt_gh]").prop("disabled",true);
            chon_gh = 0;
            max_gh = 0;
            $("#max_gh").html("Ghi hình: "+chon_gh+ "/" + max_gh);
            $(".dch").each(function(){
                if(($(this).val()).includes("Ghi hình")){
                    var row = $(this).parent().parent();
                    table_ques_selected.row(row).remove().draw();
                }
            });
        }
    });

    $(".r_check").on('change',function(){
        if (this.checked){
            $("."+$(this).attr('name')).prop('disabled',false)
        }else{
            $("."+$(this).attr('name')).prop('disabled',true)
        }
    });

    $("#r_tao_de").click(function(){
        var ten_de = $('input[name=r_ten_de]').val();
        if(ten_de == ''){
            alert("Chưa đặt tên");
            return false;
        }
        var cau_truc = {};
        var pham_tram = 0;
        $(".r_phan_tram").each(function(){
            if(typeof($(this).attr("disabled")) == 'undefined'){
                cau_truc[$(this).attr('name')] = parseInt($(this).val());
                pham_tram += parseInt($(this).val());
            }
            else{
                cau_truc[$(this).attr('name')] = (-1);
            }
        });
        if(pham_tram != 100){
            alert("Tổng phần trăm điểm số phải đủ 100%");
            return false;
        }
        if(jQuery.inArray(0, cau_truc) != -1){
            alert("Chưa chọn phần trăm điểm số");
            return false;
        }
        var chi_tiet_so_luong = {};
        var so_luong = 0;
        $(".r_so_luong").each(function(){
            if(typeof($(this).attr("disabled")) == 'undefined'){
                chi_tiet_so_luong[$(this).attr('name')] = parseInt($(this).val());
                so_luong += parseInt($(this).val());
            }
            else{
                chi_tiet_so_luong[$(this).attr('name')] = (-1);
            }
        });
        if(chi_tiet_so_luong['r_tn_d']+chi_tiet_so_luong['r_tn_tb']+chi_tiet_so_luong['r_tn_k'] =='000'){
            alert("Chưa chọn số lượng câu hỏi");
            return false;
        }
        if(chi_tiet_so_luong['r_dt_d']+chi_tiet_so_luong['r_dt_tb']+chi_tiet_so_luong['r_dt_k'] =='000'){
            alert("Chưa chọn số lượng câu hỏi");
            return false;
        }
        if(chi_tiet_so_luong['r_tl_d']+chi_tiet_so_luong['r_tl_tb']+chi_tiet_so_luong['r_tl_k'] =='000'){
            alert("Chưa chọn số lượng câu hỏi");
            return false;
        }
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
             type:'POST',
             url:location.href,
             data:{'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val(),'ten_de': ten_de, 'random': '',
                'mon': $('#r_gv_mon option:selected').val(),'loai_de': $('#r_loai_de option:selected').val(),
                'cau_truc': JSON.stringify(cau_truc),'chi_tiet_so_luong': JSON.stringify(chi_tiet_so_luong),
                'thoi_gian': $('input[name=r_thoi_gian]').val(),'so_luong':so_luong},
             success: function(msg, status, jqXHR){
                if (msg.status == 'failure'){
                    $("#cancel_upload").click();
                    alert(msg.messages);
                }else{
                    $("#processing").modal('hide');
                    location.reload();
                }
             },
        });
    });

});




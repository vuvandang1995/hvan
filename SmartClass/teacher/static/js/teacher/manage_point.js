$(document).ready(function(){
    var lop_ht = $('#lop_ht').val();
    var table_student = $('#list_student').DataTable({
        "ajax": {
            "type": "GET",
            "url": "/manage_point_data_"+lop_ht,
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            },
        },
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "displayLength": 25,
        dom: 'Bfrtip',
        buttons: ['csv', 'excel', 'print', 'pdf'],
    });

    $("#point").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var id_diem = button.data('id');
        $("#point_data").load("/manage_point_detail_"+ id_diem);
        setTimeout(function(){
            $(".nhan_xet").each(function(){
                $(this).val($(this).attr('placeholder'));
            });
        },500);
        $('#in').show();
        $('#cham_diem').show();
        $('#luu_diem').hide();
        $('#huy').hide();
        $("#close").show();
        $(".diem_tu_luan").prop("readonly",true)
        $(".nhan_xet").prop("readonly",true)
    });

    $("#cham_diem").click(function(){
        $('#in').hide();
        $(this).hide();
        $('#luu_diem').show();
        $('#huy').show();
        $("#close").hide();
        $(".diem_tu_luan").prop("readonly",false)
        $(".nhan_xet").prop("readonly",false)
    });

    $("#huy").click(function(){
        $('#in').show();
        $('#cham_diem').show();
        $('#luu_diem').hide();
        $(this).hide();
        $("#close").show();
        $(".diem_tu_luan").prop("readonly",true)
        $(".nhan_xet").prop("readonly",true)
    });

    $("#luu_diem").click(function(){
        $('#in').show();
        $('#cham_diem').show();
        $('#luu_diem').hide();
        $("#huy").hide();
        $("#close").show();
        $(".diem_tu_luan").prop("readonly",true);
        $(".nhan_xet").prop("readonly",true);
        var diem_tu_luan = {};
        var error = false;
        $(".diem_tu_luan").each(function(){
            var temp = parseFloat($(this).val())
            if((isNaN(temp)) || (temp > $(this).attr('max')) || (temp<$(this).attr('min'))){
                error = true;
                return false;
            }
            diem_tu_luan[$(this).data('id')]= temp;
            $(this).prop("readonly",true);
        });
        if(error){
            alert('nhập điểm không hợp lệ');
            return false;
        };
        var nhan_xet = {};
        $(".nhan_xet").each(function(){
            nhan_xet[$(this).data('id')]= $(this).val();
            $(this).prop("readonly",true);
        });
        $.ajax({
            type: "POST",
            url: location.href,
            data:{'diem_tu_luan': JSON.stringify(diem_tu_luan), 'nhan_xet': JSON.stringify(nhan_xet),
            "diem_id":$('#point input[name=diem_id]').val(),
            'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()},
            success: function(){
                $('#point').modal('hide');
                table_student.ajax.reload(null, false);
            }
        });
    });

});

function PrintElem(){
    $("body").first().html($("#point_data").html());
    window.print();
    location.reload();
    return true;
}

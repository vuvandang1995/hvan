$(document).ready(function(){
    var table_exam = $("#list_exam").DataTable({
        'ajax':{
            'type': "GET",
            'url': "/de_data_0",
            'data': function(result){
                return JSON.stringify(result);
            },
        },
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "displayLength": 10,
        "order": [[ 4, 'desc' ]],
        "scrollCollapse": false,
    });

    $('#list_exam tbody').on( 'click', 'tr', function () {
        var id = $(this).find('p').first().data("id");
        $.ajax({
            type:"GET",
            url:"/chi_tiet_de_data_" + id,
            success: function(data){
                $("#khung_exam").html(data);
                $("#exam").modal("show");
            },
        });
    });

    $('#delete_exam').click(function(){
        if(confirm("Bạn có chắc chắn muốn xóa ?")){
            $.ajax({
                url: location.href,
                type: "POST",
                data: {'id':$('#exam input[name=exam_id]').val(), 'delete':'',
                'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()},
                success: function(){
                    table_exam.ajax.reload(null, false);
                    $("#exam").modal("hide");
                }
            });
        };
    });



});




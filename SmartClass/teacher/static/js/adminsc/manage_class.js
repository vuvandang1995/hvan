$(document).ready(function(){
    var table_class = $('#list_class').DataTable({
        "ajax": {
            "type": "GET",
            "url": "/adminsc/manage_class/data",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            },
        },
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "displayLength": 50,
    });

    var table_teacher = $('#list_teacher').DataTable({
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "displayLength": 10,
    });

    $("#detail_teacher").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.data('title');
        $("#detail_teacher_title").text("Chi tiết lớp "+title);
        table_teacher.ajax.url("/adminsc/manage_teacher/data_" + title).load();
    });

    var table_student = $('#list_student').DataTable({
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "displayLength": 10,
    });

    $("#detail_student").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.data('title');
        $("#detail_student_title").text("Chi tiết lớp "+title);
        table_student.ajax.url("/adminsc/manage_student/data_" + title).load();
    });

    $("#list_class").on('click', '.btn-danger', function(){
        var id = $(this).attr('id').split('_')[1];
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if (confirm('Bạn có chắc ?')){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'delete':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    table_class.ajax.reload(null,false);
                }
           });
        }
    });

    $("#new_class").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.data('title');
        $("#new_class  input[name=kieu]").val(title);
        if (title === 'edit'){
            var id = button.attr('id').split('_')[1];
            $("#new_class input[name=id]").val(id);
            var ten = $("#ten_"+id).text();
            $("#new_class input[name=ten]").val(ten);
            var khoa = $("#khoa_"+id).text();
            $("#new_class input[name=khoa]").val(khoa);
            var nien_khoa = $("#nien_khoa_"+id).text();
            $("#new_class input[name=nien_khoa]").val(nien_khoa);
            $('#change_class_title').html("Chỉnh sửa lớp")
            $("#save_new_class").html("Chỉnh sửa");
        }else{
            $("#new_class input[name=id]").val(0);
            $('#change_class_title').html("Tạo mới lớp")
            $("#new_class input[name=ten]").val("");
            $("#new_class input[name=khoa]").val("");
            $("#new_class input[name=nien_khoa]").val("");
            $("#save_new_class").html("Tạo mới");
        }
    });

    $('#save_new_class').click( function(){
        var kieu = $("#new_class  input[name=kieu]").val();
        var token = $("#new_class input[name=csrfmiddlewaretoken]").val();
        var ten = $("#new_class input[name=ten]").val();
        var id = $("#new_class input[name=id]").val();
        var khoa = '';
        $("#ls option").each(function(){
            if($("#new_class input[name=khoa]").val() == $(this).val()){
                khoa = $(this).val();
                return false;
            }
        });
        if(khoa == ''){
            alert("Khoa không chính xác");
            return false;
        }
        var nien_khoa = '';
        $("#lss option").each(function(){
            if($("#new_class input[name=nien_khoa]").val() == $(this).val()){
                 nien_khoa = $(this).val();
                return false;
            }
        });
        if(nien_khoa == ''){
            alert("Khóa không chính xác");
            return false;
        }
        $.ajax({
            type:'POST',
            url:location.href,
            data: {'csrfmiddlewaretoken':token, 'kieu':kieu, 'ten': ten, 'id':id , 'khoa':khoa, 'nien_khoa':nien_khoa},
            success: function(){
                table_class.ajax.reload(null,false);
                $("#new_class").modal("hide");
            }
        });
    });

    var input_dom_element = document.getElementById("file");
    var result;

    function handle_fr(e) {
        result = [];
        var files = e.target.files, f = files[0];
        var reader = new FileReader();
        var rABS = !!reader.readAsBinaryString;
        reader.onload = function(e) {
            var data = e.target.result;
            if(!rABS) data = new Uint8Array(data);

            var wb = XLSX.read(data, {type: rABS ? 'binary' : 'array'});
            var ws = wb.Sheets[wb.SheetNames[0]];
            result = XLSX.utils.sheet_to_json(ws, {header:1});
//            wb.SheetNames.forEach(function(sheetName) {
//                var roa = XLSX.utils.sheet_to_json(wb.Sheets[sheetName], {header:1});
//                if(roa.length) result[sheetName] = roa;
//            });

        };
        if(rABS) reader.readAsBinaryString(f); else reader.readAsArrayBuffer(f);
    }
    var handler = handle_fr;
    if(input_dom_element.attachEvent) input_dom_element.attachEvent('onchange', handler);
    else input_dom_element.addEventListener('change', handler, false);

    $('#create_new_class_multi').click(function(){
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if (typeof result != 'undefined' ){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'csrfmiddlewaretoken':token, 'list_class':JSON.stringify(result)},
                success: function(msg){
                    alert(msg.messages);
                    table_class.ajax.reload(null,false);
                    $("#new_class_multi").modal("hide");
                }
           });
        }
    });

    $("#file_sample").click(function(){
        var excel = $JExcel.new("Calibri light 10 #333333");
        excel.set( {sheet:0,value:"Sheet 1" } );
        var formatHeader = excel.addStyle ( {font: "Calibri 12 #0000AA B"});

        excel.set(0, 0, 0, "Lớp", formatHeader)
        excel.set(0, 1, 0, "Khoa", formatHeader)
        excel.set(0, 2, 0, "Niên khóa", formatHeader)

        excel.set(0, 0, 1, "10A")
        excel.set(0, 1, 1, "Công nghệ thông tin")
        excel.set(0, 2, 1, "K64 - 2018")

        excel.set(0, 0, 2, "11B")
        excel.set(0, 1, 2, "Điện tử")
        excel.set(0, 2, 2, "K63 - 2017")

        excel.generate(`Mẫu_nhập_lớp.xlsx`);
    })

    $("#new_class_multi").on('show.bs.modal', function(event){
        $("#file").val("");
    })

});

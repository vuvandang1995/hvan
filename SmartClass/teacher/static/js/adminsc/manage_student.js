$(document).ready(function(){
    setTimeout(function(){$(".easy-autocomplete.eac-square").css("width","100%");},500);
    var table_student = $('#list_student').DataTable({
//        "columnDefs": [
//            { "width": "2%", "targets": 0 },
//            { "width": "12%", "targets": 1 },
//            { "width": "10%", "targets": 2 },
//            { "width": "10%", "targets": 3 },
//        ],
        "ajax": {
            "type": "GET",
            "url": "/adminsc/manage_student/data_all",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            },
//            "complete": function(){
//                setTimeout(function(){
//                    countdowntime();
//                }, 1000);
//            }
        },
//        'dom': 'Rlfrtip',
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "displayLength": 10,
    });

    $("#new_student").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.data('title');
        if (title === 'edit'){
            $('#new_student_title').html("Chỉnh sửa học sinh")
            var hsid = button.attr('id').split('_')[1];

            var fullname = $("#full_"+hsid).text();
            $("#new_student input[name=fullname]").val(fullname);

            $('body #list_lop').empty();
            $('body .list_lop'+hsid).each(function(){
                $('#new_student input[name=search_lop]').val($(this).text());
            });

            var gioi_tinh = $("#gioi_"+ hsid).text();
            if(gioi_tinh === 'Nam'){
                $('#gioi_tinh option[data-gioi_tinh="1"]').prop('selected', true);
                $('#gioi_tinh option[data-gioi_tinh="0"]').prop('selected', false);
            }else{
                $('#gioi_tinh option[data-gioi_tinh="1"]').prop('selected', false);
                $('#gioi_tinh option[data-gioi_tinh="0"]').prop('selected', true);
            }

            var username = $("#user_"+hsid).text();
            $("#new_student input[name=username]").val(username);
            $("#new_student input[name=username]").prop("readonly", true);

            var email = $("#email_"+hsid).text();
            $("#new_student input[name=email]").val(email);

            $(".passwd").each(function() {
                $(this).hide();
            });

            $("#new_student  input[name=kieu]").val("edit");

            $("#create_new_student").html("Chỉnh sửa");

        }else{
            $('#new_student_title').html("Thêm mới học sinh")
            $("#new_student input[name=gvid]").val(0);
            $("#new_student input[name=fullname]").val("");
            $("#new_student input[name=search_mon]").val("");
            $("#new_student input[name=search_lop]").val("");
            $("#new_student input[name=gioi_tinh]").val("");
            $("#new_student input[name=username]").val("");
            $("#new_student input[name=password]").val("");
            $("#new_student input[name=password2]").val("");
            $("#new_student input[name=email]").val("");
            $('#new_student input[name=search_lop]').val('');

            $("#new_student input[name=username]").prop("readonly", false);

            $(".passwd").each(function() {
                $(this).show();
            });

            $("#new_student  input[name=kieu]").val("new");
            $("#create_new_student").html("Thêm mới");
        }
    });

    $('#create_new_student').click( function(){
        var kieu = $("#new_student  input[name=kieu]").val();
        var token = $("#new_student input[name=csrfmiddlewaretoken]").val();
        var fullname = $("#new_student input[name=fullname]").val();
        var gioi_tinh= $('#gioi_tinh option:selected').data('gioi_tinh');
        var username = $("#new_student input[name=username]").val();
        var email = $("#new_student input[name=email]").val();
        var password = $("#new_student input[name=password]").val();
        var password2 = $("#new_student input[name=password2]").val();
        var list_lop = $('#new_student input[name=search_lop]').val();

        if(password === password2){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'csrfmiddlewaretoken':token, 'kieu':kieu, 'fullname': fullname, 'gioi_tinh': gioi_tinh,
                'list_lop': list_lop,'username': username,'email': email, 'password': password},
                success: function(){
                    $("#new_student").modal("hide");
                    $('#list_student').DataTable().ajax.reload(null,false);
                }
            });
        }
    });

//    $(".gioi_tinh").change(function() {
//        if(this.checked && this.name === 'nam'){
//            $('#new_student input[name=nu]').prop('checked', false);
//        }
//        else if(this.checked && this.name === 'nu'){
//            $('#new_student input[name=nam]').prop('checked', false);
//        }
//    });

    var options_lop = {
        url: "lop_data",

        getValue: function(element){
            return element.ten;
         },
        list: {
            match: {
                enabled: true
            },
        },
        theme: "square"
    };
    $("#search_lop").easyAutocomplete(options_lop);

    $("#list_student").on('click', '.btn-danger', function(){
        var id = $(this).attr('id').split('_')[1];
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if (confirm('Bạn có chắc ?')){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'delete':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    $('#list_student').DataTable().ajax.reload(null,false);
                }
           });
        }
    });

    $("#list_student").on('click', '.btn-warning', function(){
        var id = $(this).attr('id').split('_')[1];
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if (confirm('Bạn có chắc ?')){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'block':id, 'csrfmiddlewaretoken':token},
                success: function(){
                    $('#list_student').DataTable().ajax.reload(null,false);
                }
           });
        }
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

    $('#create_new_student_multi').click(function(){
//        console.log(typeof result);
        var token = $("input[name=csrfmiddlewaretoken]").val();
        if (typeof result != 'undefined' ){
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'csrfmiddlewaretoken':token, 'list_student':JSON.stringify(result)},
                success: function(msg){
                    alert(msg.messages);
                    $('#list_student').DataTable().ajax.reload(null,false);
                    $("#new_student_multi").modal("hide");
                }
           });
        }
    });

    $("#file_sample").click(function(){
        var excel = $JExcel.new("Calibri light 10 #333333");
        excel.set( {sheet:0,value:"Sheet 1" } );
        var formatHeader = excel.addStyle ( {font: "Calibri 12 #0000AA B"});

        excel.set(0, 0, 0, "Số thứ tự", formatHeader)
        excel.set(0, 1, 0, "Họ và tên", formatHeader)
        excel.set(0, 2, 0, "Giới tính", formatHeader)
        excel.set(0, 3, 0, "Lớp", formatHeader)

        excel.set(0, 0, 1, 1)
        excel.set(0, 1, 1, "Nguyễn Văn Nam")
        excel.set(0, 2, 1, "Nam")
        excel.set(0, 3, 1, "9A")

        excel.set(0, 0, 2, 2)
        excel.set(0, 1, 2, "Lê Thị Nữ")
        excel.set(0, 2, 2, "Nữ")
        excel.set(0, 3, 2, "10A")

        excel.generate(`Mẫu_nhập_học_sinh.xlsx`);
    })

    $("#new_student_multi").on('show.bs.modal', function(event){
        $("#file").val("");
    })

});

function change() {
    var lop_hs = '';
    $("#ls option").each(function(){
        if($('#data_lop').val() == $(this).val()){
            lop_hs = $('#data_lop').val();
        }
    });
    if(lop_hs == ''){
        alert("Lớp không chính xác");
    }else{
        if(lop_hs === 'Tất cả'){
            lop_hs = 'all'
        }
        stu_data =$("#list_student").DataTable();
        stu_data.ajax.url('/adminsc/manage_student/data_'+ lop_hs).load();
    }

};



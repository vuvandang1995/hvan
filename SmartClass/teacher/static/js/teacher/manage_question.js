$(document).ready(function(){
    create_editor_q(".editor_da");
    create_editor_q('.editor_nd');

    var table_question = $("#list_question").DataTable({
        "ajax": {
            "type": "GET",
            "url": "/question_data_" + $("#gv_mon option:selected").val() +"_0_0",
            "contentType": "application/json; charset=utf-8",
            "data": function(result){
                return JSON.stringify(result);
            },
        },
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "displayLength": 25,
        "order": [[ 5, 'desc' ]],
    });

    $("#gv_mon").on('change', function(){
        table_question.ajax.url("/question_data_" + $("#gv_mon option:selected").val()+"_0_0").load();
    });

    $('#list_question tbody').on( 'click', 'tr', function () {
        if(table_question.data().count() == 0){
            return false;
        }
        var id = $(this).find('p').first().attr('id').split("_")[2];
        var don = $(this).find('p').first().data('don');
        $.ajax({
            type: "GET",
            url: "question_data_detail_"+id+"_edit_"+don ,
            success: function(data){
                $("#khung_modal").html(data);
                var dang_cau_hoi = $("#khung_modal input[name=dang_cau_hoi]").val();
                if(dang_cau_hoi.includes("Hình ảnh")){
                    $("#khung_modal input[type=file]").first().change(function() {
                        readURL(this, 'hinh_anh_modal');
                    });
                }else if (dang_cau_hoi.includes("Âm thanh")){
                    var URL = window.URL || window.webkitURL;
                    var playSelectedFile = function (event) {
                        var file = this.files[0];
                        var type = file.type;
                        var videoNode = document.querySelector('#khung_modal audio');
                        var canPlay = videoNode.canPlayType(type);
                        if (canPlay === '') {
                            alert("can't play");
                        };
                        var fileURL = URL.createObjectURL(file);
                        videoNode.src = fileURL;
                    }
                    var inputNode = document.querySelector('#khung_modal input[type=file]');
                    inputNode.addEventListener('change', playSelectedFile, false);
                }else if (dang_cau_hoi.includes("Video")){
                    var URL = window.URL || window.webkitURL;
                    var playSelectedFile = function (event) {
                        var file = this.files[0];
                        var type = file.type;
                        var videoNode = document.querySelector('#khung_modal video');
                        var canPlay = videoNode.canPlayType(type);
                        if (canPlay === '') {
                            alert("can't play");
                        };
                        var fileURL = URL.createObjectURL(file);
                        videoNode.src = fileURL;
                    }
                    var inputNode = document.querySelector('#khung_modal input[type=file]');
                    inputNode.addEventListener('change', playSelectedFile, false);
                }
                $("#question").modal("show");
                create_editor_q("#khung_modal .editor_da")
            },
        });


    });

    $("#edit_question").on('click', function(event){
        var formData = new FormData();
        formData.append('csrfmiddlewaretoken',$("input[name=csrfmiddlewaretoken]").val());
        formData.append('edit',"");
        formData.append('id',$("#khung_modal input[name=id]").val());
        var noi_dung = $("#noi_dung_modal .ql-editor").html();
        formData.append('noi_dung',noi_dung);
        if(noi_dung == ''){
            alert("Chưa nhập nội dung");
            return false;
        }
        var dang_cau_hoi = $("#khung_modal input[name=dang_cau_hoi]").val();
        var so_cau_hoi = $("#khung_modal input[name=so_cau_hoi]").val();
        var nd_cau_hoi = [];
        var dap_an = [];
        var nd_dap_an = [];
        if (so_cau_hoi > 1){
            $("#khung_modal .nd_cau_hoi .ql-editor").each(function(){
                nd_cau_hoi.push($(this).html());
            });
            if (jQuery.inArray("<p><br></p>", nd_cau_hoi) != -1){
                alert("Chưa nhập nội dung câu hỏi");
                return false;
            }
            formData.append('nd_cau_hoi',JSON.stringify(nd_cau_hoi));
        }
        if (dang_cau_hoi.includes("Trắc nhiệm")){
            $("#khung_modal .dap_an").each(function(){
                if ($(this).is(':checked')){
                    dap_an.push(1);
                }else{
                    dap_an.push(0);
                }
            });
            formData.append('dap_an',JSON.stringify(dap_an));
            $("#khung_modal .nd_dap_an .ql-editor").each(function(){
                nd_dap_an.push($(this).html());
            });
            formData.append('nd_dap_an',JSON.stringify(nd_dap_an));
        }
        else if (dang_cau_hoi.includes("Điền từ")){
            $("#khung_modal .nd_dap_an .ql-editor").each(function(){
                nd_dap_an.push($(this).html());
            });
            formData.append('nd_dap_an',JSON.stringify(nd_dap_an));
        }

        if(!dang_cau_hoi.includes("Văn bản")&&(typeof($("#khung_modal input[type=file]")[0].files[0]) != "undefined")){
            formData.append('dinh_kem',$("#khung_modal input[type=file]")[0].files[0]);
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
            type : "POST",
            url : location.href,
            data : formData,
            contentType: false,
            processData: false,
            success : function(){
                $("#processing").modal('hide');
                $("#question").modal('hide');
                table_question.ajax.reload(null, false);
            },
        });
    });
});

function readURL(input,image) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();
    reader.onload = function(e) {
      $('#'+image).attr('src', e.target.result);
    }
    reader.readAsDataURL(input.files[0]);
  }
}

var options = {
  modules: {
    'syntax': true,
    'toolbar': [
      [ { 'size': [] }],
      [ 'bold', 'italic', 'underline', 'strike' ],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'script': 'super' }, { 'script': 'sub' }],
      [{ 'header': '1' }, { 'header': '2' } ],
      [{ 'list': 'ordered' }, { 'list': 'bullet'}, { 'indent': '-1' }, { 'indent': '+1' }],
      [ { 'align': [] }],
      [ 'formula' ],
    ],
  },
    placeholder: 'Nhập nội dung',
    theme: 'snow'
};

function create_editor_q(target){
    $(target).each(function(){
        var quill = new Quill("#"+$(this).attr('id'), options);
    });
}

$(document).ready(function(){
    create_editor_q(".editor_da");
    create_editor_q('.editor_nd');
    $("#dang_cau_hoi, #so_cau_hoi, #so_dap_an").on("change", function(){
        thayDoi();
    });

    $("#dang_media").on("change", function(){
        var dang_media = $("#dang_media option:selected").text();
        var ch ='<label>Nội dung:</label>';
        if ( dang_media.includes("Văn bản")){
            ch += `
            <div id="noi_dung" class="ques-container editor_nd" ></div>
            <br>
            `;
            $("#khung_cau_hoi").html(ch);
        }
        else if ( dang_media.includes("Hình ảnh")){
            ch += `
            <div class="row">
                <div class="col-md-8 col-sm-12 col-xs-12 form-group">
                    <img id="hinh_anh" style="max-height:600px;max-width:600px; display: block; margin-left: auto;margin-right: auto;" src="/static/image/placeholder.png" alt="chọn hình ảnh" />
                    <input type='file' style="display: block; margin-left: auto;margin-right: auto;" accept="image/*" />
                </div>
                <div class="col-md-4 col-sm-12 col-xs-12 form-group">
                  <div id="noi_dung" class="ques-container editor_nd"></div>
                </div>
            </div>
            <br>
            `;
            $("#khung_cau_hoi").html(ch);
            $("input[type=file]").first().change(function() {
                readURL(this, "hinh_anh");
            });
        }
        else if ( dang_media.includes("Âm thanh")){
            ch += `
            <div class="row">
                <div class="col-md-4 col-sm-12 col-xs-12 form-group">
                  <audio id="media" controls width="100%"></audio>
                  <input type="file" style="display: block; margin-left: auto;margin-right: auto;"  accept="audio/*">
                </div>
                <div class="col-md-8 col-sm-12 col-xs-12 form-group">
                  <div id="noi_dung" class="ques-container editor_nd"></div>
                </div>
            </div>
            <br>
            `;
            $("#khung_cau_hoi").html(ch);
            var URL = window.URL || window.webkitURL;
            var playSelectedFile = function (event) {
                var file = this.files[0];
                var type = file.type;
                var videoNode = document.querySelector('audio');
                var canPlay = videoNode.canPlayType(type);
                if (canPlay === '') {
                    alert("can't play");
                };
                var fileURL = URL.createObjectURL(file);
                videoNode.src = fileURL;
            }
            var inputNode = document.querySelector('input[type=file]');
            inputNode.addEventListener('change', playSelectedFile, false);
        }
        else if( dang_media.includes("Video")){
            ch += `
            <div class="row">
                <div class="col-md-8 col-sm-12 col-xs-12 form-group">
                  <video id="media" controls width="100%"></video>
                  <input type="file" style="display: block; margin-left: auto;margin-right: auto;" accept="video/*">
                </div>
                <div class="col-md-4 col-sm-12 col-xs-12 form-group">
                  <div id="noi_dung" class="ques-container editor_nd"></div>
                </div>
            </div>
            <br>
            `;
            $("#khung_cau_hoi").html(ch);
            var URL = window.URL || window.webkitURL;
            var playSelectedFile = function (event) {
                var file = this.files[0];
                var type = file.type;
                var videoNode = document.querySelector('video');
                var canPlay = videoNode.canPlayType(type);
                if (canPlay === '') {
                    alert("can't play");
                };
                var fileURL = URL.createObjectURL(file);
                videoNode.src = fileURL;
            }
            var inputNode = document.querySelector('input[type=file]');
            inputNode.addEventListener('change', playSelectedFile, false);
        }
        else{
            ch += `
            <div class="row">
                <div class="col-md-4 col-sm-12 col-xs-12 form-group">
                  <input type="file" style="display: block; margin-left: auto;margin-right: auto;">
                </div>
                <div class="col-md-8 col-sm-12 col-xs-12 form-group">
                  <div id="noi_dung" class="ques-container editor_nd"></div>
                </div>
            </div>
            <br>
            `;
            $("#khung_cau_hoi").html(ch);
        }
        create_editor_q(".editor_nd");
    });

    $("#luu_cau_hoi").on("click", function(){
        var formData = new FormData();
        formData.append('csrfmiddlewaretoken',$("input[name=csrfmiddlewaretoken]").val());
        formData.append('mon',$("#mon option:selected").text());
        var chu_de = $("#chu_de").val();
        if(chu_de == ''){
            alert("Chưa có chủ đề");
            return false;
        }
        formData.append('chu_de',chu_de);
        var noi_dung = $("#noi_dung .ql-editor").html();
        if(noi_dung == '<p><br></p>'){
            alert("Chưa nhập nội dung");
            return false;
        }
        formData.append('noi_dung',noi_dung);
        var so_cau_hoi = $('#so_cau_hoi').val();
        var dang_cau_hoi = $("#dang_cau_hoi option:selected").text();
        var dang_media = $('#dang_media option:selected').text();
        formData.append('dang_cau_hoi',dang_media + " + " + dang_cau_hoi);
        var nd_cau_hoi = [];
        var dap_an = [];
        var nd_dap_an = [];
        if (so_cau_hoi > 1){
            $("#tab_content1 .nd_cau_hoi .ql-editor").each(function(){
                nd_cau_hoi.push($(this).html());
            });
            if (jQuery.inArray("<p><br></p>", nd_cau_hoi) != -1){
                alert("Chưa nhập nội dung câu hỏi");
                return false;
            }
            formData.append('so_cau_hoi', so_cau_hoi);
            formData.append('so_dap_an',$("#so_dap_an").val());
            formData.append('nd_cau_hoi',JSON.stringify(nd_cau_hoi));
        }
        if (dang_cau_hoi.includes("Trắc nhiệm")){
            $("#tab_content1 .dap_an").each(function(){
                if ($(this).is(':checked')){
                    dap_an.push(1);
                }else{
                    dap_an.push(0);
                }
            });
            if (jQuery.inArray( 1, dap_an) == -1){
                alert("Chưa chọn đáp án đúng");
                return false;
            } else if (jQuery.inArray( 0, dap_an) == -1){
                alert("Không có đáp án sai");
                return false;
            }
            formData.append('dap_an',JSON.stringify(dap_an));

            $("#tab_content1 .nd_dap_an .ql-editor").each(function(){
                nd_dap_an.push($(this).html());
            });
            if (jQuery.inArray("<p><br></p>", nd_dap_an) != -1){
                alert("Chưa nhập nội dung đáp án");
                return false;
            }
            formData.append('nd_dap_an',JSON.stringify(nd_dap_an));
        }
        else if(dang_cau_hoi.includes("Điền từ")){
            $("#tab_content1 .nd_dap_an .ql-editor").each(function(){
                nd_dap_an.push($(this).html());
            });
            if (jQuery.inArray("<p><br></p>", nd_dap_an) != -1){
                alert("Chưa nhập nội dung đáp án");
                return false;
            }
            formData.append('nd_dap_an',JSON.stringify(nd_dap_an));
        }
        if(!dang_media.includes("Văn bản")){
            if (typeof($("#tab_content1 input[type=file]")[0].files[0]) == "undefined"){
                alert("Chưa chọn file");
                return false;
            }else{
                formData.append('dinh_kem',$("#tab_content1 input[type=file]")[0].files[0]);
            }
        }
        formData.append('do_kho',$("#do_kho option:selected").text());
        formData.append('dung_lam',$("#dung_lam option:selected").text());
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
                $("#noi_dung .ql-editor").empty();
                $("#tab_content1 .nd_cau_hoi .ql-editor").each(function(){
                    $(this).empty();
                });
                $("#tab_content1 .dap_an").each(function(){
                    $(this).prop('checked', false);
                });
                $("#tab_content1 .nd_dap_an .ql-editor").each(function(){
                    $(this).empty();
                });
                $("#hinh_anh").attr("src","/static/image/placeholder.png");
                $("#media").attr("src","");
                $("input[type=file]").val('');
                $("#processing").modal('hide');
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

function tracNhiem(){
    var nd='';
    var da='';
    if($('#so_cau_hoi').val() < 1){
        alert('Số câu hỏi phải >= 1');
        $('#so_cau_hoi').val(1);
    }else if ($('#so_cau_hoi').val() > 10) {
        alert('Số câu hỏi quá lớn');
        $('#so_cau_hoi').val(1);
    }else if ($('#so_dap_an').val() < 2) {
        alert('Số đáp án phải >= 2');
        $('#so_dap_an').val(2);
    }else if ($('#so_dap_an').val() > 10) {
        alert('Số đáp án quá lớn');
        $('#so_dap_an').val(2);
    }
    if ($('#so_cau_hoi').val() == 1){
        for (var i = 0; i < $('#so_dap_an').val(); i++){
            nd +=`
            <div class="row">
                <div class="col-md-1 col-sm-12 col-xs-12 form-group">
                    <input type="checkbox" class="form-control dap_an" style="transform:scale(0.6);" name="dap_an">
                </div>
                <div class="col-md-11 col-sm-12 col-xs-12 form-group">
                  <div id="dap_an_0_${i}" class="answer-container nd_dap_an editor_da"></div>
                </div>
            </div>
            `;
        }
    }else{
        for (var i = 0; i < $('#so_cau_hoi').val(); i++){
            for (var k = 0; k < $('#so_dap_an').val(); k++){
                da +=`
                <div class="row">
                    <div class="col-md-1 col-sm-12 col-xs-12 form-group">
                        <input type="checkbox" class="form-control dap_an" style="transform:scale(0.6);" name="dap_an">
                    </div>
                    <div class="col-md-11 col-sm-12 col-xs-12 form-group">
                      <div id="dap_an_${i}_${k}" class="answer-container nd_dap_an editor_da"></div>
                    </div>
                </div>
                `;
            };
            nd += `
            <div class="row">
                <div class="col-md-12 col-sm-12 col-xs-12 form-group">
                  <div id="cau_hoi_${i}" class="answer-container nd_cau_hoi editor_da"></div>
                </div>
            </div>
            ${da}
            `;
            da = '';
        };
    }
    $("#khung_dap_an").html(nd);
    create_editor_q('.editor_da');
}

function dienTu(){
    $('#so_cau_hoi').val(1);
    var nd='';
    var da='';
    if ($('#so_dap_an').val() < 1) {
        alert('Số đáp án phải >= 1');
        $('#so_dap_an').val(1);
    }else if ($('#so_dap_an').val() > 10) {
        alert('Số đáp án quá lớn');
        $('#so_dap_an').val(1);
    }
    for (var i = 0; i < $('#so_dap_an').val(); i++){
        nd +=`
        <div class="row">
            <div class="col-md-12 col-sm-12 col-xs-12 form-group">
              <div id="dap_an_0_${i}" class="answer-container nd_dap_an editor_da"></div>
            </div>
        </div>
        `;
    }
    $("#khung_dap_an").html(nd);
    create_editor_q('.editor_da');
}

function tuLuan(){
    $('#so_dap_an').val(1);
    var nd='';
    if($('#so_cau_hoi').val() < 1){
        alert('Số câu hỏi phải >= 1');
        $('#so_cau_hoi').val(1);
    }else if ($('#so_cau_hoi').val() > 10) {
        alert('Số câu hỏi quá lớn');
        $('#so_cau_hoi').val(1);
    }
    else if ($('#so_cau_hoi').val() == 1){
        $("#khung_dap_an").html('');
    }else{
        for (var i = 0; i < $('#so_cau_hoi').val(); i++){
            nd += `
            <div class="row">
                <div class="col-md-12 col-sm-12 col-xs-12 form-group">
                  <div id="cau_hoi_${i}" class="answer-container nd_cau_hoi editor_da"></div>
                </div>
            </div>
            `;
        };
    }
    $("#khung_dap_an").html(nd);
    create_editor_q('.editor_da');
}

function thayDoi(){
    var dang_cau_hoi = $("#dang_cau_hoi option:selected").text();
    if ( dang_cau_hoi.includes("Trắc nhiệm")){
        $('#so_cau_hoi').prop("readonly",false);
        $("#so_dap_an").prop("readonly", false);
        tracNhiem();
    }
    else if ( dang_cau_hoi.includes("Điền từ")){
        $('#so_cau_hoi').prop("readonly",true);
        $("#so_dap_an").prop("readonly", false);
        dienTu();
    }
    else{
        $('#so_cau_hoi').prop("readonly",false);
        $("#so_dap_an").prop("readonly", true);
        tuLuan();
    }
}

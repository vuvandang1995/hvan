$(document).ready(function(){
    thayDoi();

    $('#dang_cau_hoi, #so_cau_hoi, #so_dap_an, #dang_media').on("change", function(){
        thayDoi();
    })

    $('#luu_cau_hoi').click(function(){
        var formData = new FormData();
        formData.append('csrfmiddlewaretoken',$("input[name=csrfmiddlewaretoken]").val());
        formData.append('mon',$("#mon option:selected").val());
        var dang_media = $('#dang_media option:selected').text();
        var dang_cau_hoi = $("#dang_cau_hoi option:selected").text();
        formData.append('dang_cau_hoi',dang_media + " + " + dang_cau_hoi);
        formData.append("dung_lam", $("#dung_lam option:selected").text());
        var so_cau_hoi = $('#so_cau_hoi').val();
        formData.append('so_cau_hoi', so_cau_hoi);
        formData.append('so_dap_an', $("#so_dap_an").val());
        if (typeof result == 'undefined' ){
            alert("Chưa chon file excel");
            return false;
        }
        formData.append('data', JSON.stringify(result));
        if(!dang_media.includes("Văn bản")){
            var attach_files = $("#file_attach")[0].files;
            if(attach_files.length == 0){
                alert("Chưa chon file đính kèm");
                return false;
            }
            for(let i of attach_files){
                formData.append(i.name, i)
            }
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
            data: formData,
            contentType: false,
            processData: false,
            success: function(res){
                $("#processing").modal('hide');
                $("#file").val();
                $("#attach").val();
                alert(res.messages);
            }
       });
    });

    $("#file_sample").click(function(){
        var excel = $JExcel.new("Calibri light 10 #333333");
        excel.set( {sheet:0,value:"Sheet 1" } );
        var row = parseInt(0);
        var formatHeader = excel.addStyle ( {font: "Calibri 12 #0000AA B"});

        var mon = $("#mon option:selected").text();
        var dang_cau_hoi = $("#dang_cau_hoi option:selected").text();
        var dang_media = $("#dang_media option:selected").text();
        var dang_media_rg = dang_media.replace(" ", "_");
        var so_cau_hoi = parseInt($("#so_cau_hoi").val());
        var so_dap_an = parseInt($("#so_dap_an").val());
        var dang_rg ;

        excel.set(0,0,row, "Chủ đề", formatHeader)
        excel.set(0,1,row, "Độ khó", formatHeader)
        if(dang_cau_hoi=="Trắc nhiệm"){
            dang_rg = "Trắc_nhiệm";
            if(so_cau_hoi>1){
                var col = 3
                excel.set(0, 2, row, "Nội dung", formatHeader)
                if(dang_media != "Văn bản"){
                    excel.set(0, 3, row, "File đính kèm", formatHeader)
                    col = 4
                }
                for(let j=0; j<so_cau_hoi; j++){
                    let index = col+j*(so_dap_an+1);
                    excel.set(0, index, row, `Câu hỏi ${j+1}`, formatHeader)
                    for(let i=1; i<so_dap_an+1; i++){
                        if(i==1){
                            excel.set(0, index+i, row, `Đáp án ${i}(Đúng)`, formatHeader)
                        }
                        else{
                            excel.set(0, index+i, row, `Đáp án ${i}`, formatHeader)
                        }
                    }
                }
            }else{
                var col = 2
                excel.set(0, 2,row, "Câu hỏi", formatHeader)
                if(dang_media != "Văn bản"){
                    excel.set(0, 3, row, "File đính kèm", formatHeader)
                    col = 3
                }
                for(let i=1; i<so_dap_an+1; i++){
                    if(i==1){
                        excel.set(0, col+i, row, `Đáp án ${i}(Đúng)`, formatHeader)
                    }
                    else{
                        excel.set(0, col+i, row, `Đáp án ${i}`, formatHeader)
                    }
                }
            }
            row += 1;
            for(let cd in e_do_kho){
                excel.set(0, 0, row, `Chủ đề ${cd}`)
                excel.set(0, 1, row, e_do_kho[cd])
                excel.set(0, 2, row, `Nội dung ${cd}`)
                if(dang_media == "Hình ảnh"){
                    excel.set(0, 3, row, `image${cd}.PNG`)
                }else if(dang_media == 'Âm thanh'){
                    excel.set(0, 3, row, `audio${cd}.mp3`)
                }else if(dang_media == 'Video'){
                    excel.set(0, 3, row, `video${cd}.mp4`)
                }else if(dang_media == 'File'){
                    excel.set(0, 3, row, `file${cd}.pdf`)
                }
                row += 1;
            }

        }
        else if(dang_cau_hoi=="Điền từ"){
            dang_rg = "Điền_từ";
            excel.set(0, 2, row, "Câu hỏi", formatHeader)
            var col = 2
            if(dang_media != "Văn bản"){
                excel.set(0, 3, row, "File đính kèm", formatHeader)
                col = 3
            }
            for(let i=1; i<so_dap_an+1; i++){
                excel.set(0, col+i, row, `Đáp án ${i}`, formatHeader)
            }
            row += 1;
            for(let cd in e_do_kho){
                excel.set(0, 0, row, `Chủ đề ${cd}`)
                excel.set(0, 1, row, e_do_kho[cd])
                excel.set(0, 2, row, `Nội dung ${cd}`)
                if(dang_media == "Hình ảnh"){
                    excel.set(0, 3, row, `image${cd}.PNG`)
                }else if(dang_media == 'Âm thanh'){
                    excel.set(0, 3, row, `audio${cd}.mp3`)
                }else if(dang_media == 'Video'){
                    excel.set(0, 3, row, `video${cd}.mp4`)
                }else if(dang_media == 'File'){
                    excel.set(0, 3, row, `file${cd}.pdf`)
                }
                row += 1;
            }
        }
        else{
            dang_rg = "Tự_luận";
            var col = 2
            if(dang_media != "Văn bản"){
                excel.set(0, 3, row, "File đính kèm", formatHeader)
                col = 3
            }
            if(so_cau_hoi>1){
                excel.set(0, 2, row, "Nội dung", formatHeader)
                for(let i=1; i<so_cau_hoi+1; i++){
                    excel.set(0, col+i, row, `Câu hỏi ${i}`, formatHeader)
                }
            }
            else{
                excel.set(0, 2, row, "Câu hỏi", formatHeader)
            }

            row += 1;
            for(let cd in e_do_kho){
                excel.set(0, 0, row, `Chủ đề ${cd}`)
                excel.set(0, 1, row, e_do_kho[cd])
                excel.set(0, 2, row, `Nội dung ${cd}`)
                if(dang_media == "Hình ảnh"){
                    excel.set(0, 3, row, `image${cd}.PNG`)
                }else if(dang_media == 'Âm thanh'){
                    excel.set(0, 3, row, `audio${cd}.mp3`)
                }else if(dang_media == 'Video'){
                    excel.set(0, 3, row, `video${cd}.mp4`)
                }else if(dang_media == 'File'){
                    excel.set(0, 3, row, `file${cd}.pdf`)
                }
                row += 1;
            }
        }
        excel.generate(`Mẫu_${dang_rg}_${dang_media_rg}_${so_cau_hoi}_${so_dap_an}.xlsx`);
    })

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
    };
    if(rABS) reader.readAsBinaryString(f); else reader.readAsArrayBuffer(f);
}
var handler = handle_fr;
if(input_dom_element.attachEvent) input_dom_element.attachEvent('onchange', handler);
else input_dom_element.addEventListener('change', handler, false);

function thayDoi(){
    var dang = $("#dang_cau_hoi option:selected").text();
    var dang_media = $("#dang_media option:selected").text();
    if (dang == "Trắc nhiệm"){
        $('#so_cau_hoi').prop("readonly",false);
        $("#so_dap_an").prop("readonly", false);
    }else if (dang == "Điền từ"){
        $('#so_cau_hoi').val(1);
        $('#so_cau_hoi').prop("readonly", true);
        $("#so_dap_an").prop("readonly", false);
    }else{
        $('#so_cau_hoi').prop("readonly",false);
        $('#so_dap_an').val(1);
        $("#so_dap_an").prop("readonly", true);
    }

    if(dang_media != "Văn bản"){
        $("#attach").show();
        if(dang_media == 'Hình ảnh'){
            $("#file_attach").prop("accept", "image/*");
        }else if(dang_media == 'Âm thanh'){
            $("#file_attach").prop("accept", "audio/*");
        }else if(dang_media == 'Video'){
            $("#file_attach").prop("accept", "video/*");
        }else{
            $("#file_attach").prop("accept", "");
        }
    }else{
        $("#attach").hide();
    }

}



$(document).ready(function(){
    var class_ =  $('#lopht').text();
    // chatallSocket = new WebSocket(
    //    'ws://' + window.location.host +
    //    '/ws/' + userName + 'chatall'+class_+'/');
    
    chatallSocket = new WebSocket(
        'wss://' + window.location.host +
        '/ws/' + userName + 'chatall'+class_+'/');

    chatallSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var message = data['message'];
        var who = data['who'];
        var time = data['time'];
        if (time == 'key'){
            $("#videocall"+who).attr("name", message); 
        }else if (time == 'giotay'){
            $('#giotayxxx'+who).show();
        }else if (time == 'empty'){
		$(".frame > ul").empty();
        }else if ((time != 'None') && (time != 'call_time') && (time != 'teacher_change_group') && (time != 'teacher_call') && (message != 'new_chat') && (message.includes('Bắt đầu làm bài thi:') == false) && (message.includes('Giao bài tập') == false)){
            insertChat(who, message, time);
        }
        
    };

    // function reload(){
    //     $('body #list_group').html('');
    //     $.ajax({
    //         type:'GET',
    //         url: "/group_data/"+class_,
    //         success: function(data){
    //             $('body #list_group').html(data);
    //             $('body .delete_gr').on('click',function(){
    //                 var token = $("input[name=csrfmiddlewaretoken]").val();
    //                 var groupid = $(this).attr('name');
    //                 var r = confirm('Bạn chắc chắn xóa?');
    //                 if (r == true){
    //                     $.ajax({
    //                         type:'POST',
    //                         url:location.href,
    //                         data: {'delete_group':groupid, 'csrfmiddlewaretoken':token},
    //                         success: function(){
    //                             reload();
    //                         }
    //                    });
    //                 }
    //             });
    //         }
    //     });
    // }
    // $('#btn_random_group').hide();
    $('body #profile-tab').on('click',function(){
        $('#btn_random_group').show();
        $('#btn_manual_group').show();
        $('#btn_audiocall').show();
        $('#audio_all').hide();
    });
    $('body #home-tab').on('click',function(){
		$('#btn_random_group').hide();
        $('#btn_manual_group').hide();
        $('#btn_audiocall').hide();
        $('#audio_all').show();
    });

    function countdowntime(dateend){
        // $('.demo').each(function(){
            var countDownDate = new Date().getTime() + dateend*60000;
            // var p = $(this);
            // Update the count down every 1 second
            var x = setInterval(function() {

                // Get todays date and time
                var now = new Date().getTime();
                
                // Find the distance between now and the count down date
                var distance = countDownDate - now;
                
                // Time calculations for days, hours, minutes and seconds
                var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                document.getElementById("demo").innerHTML = "Thời gian còn lại: "+ minutes + "phút " + seconds + "giây ";
                if (distance < 0) {
                    clearInterval(x);
                    document.getElementById("demo").innerHTML = "Hết giờ!";
                }
            }, 1000);
        // });
    }

    function makeOrJoinRoom(roomid, gr_chat_name) {
        connection.videosContainer = document.getElementById('videos-container'+roomid);
        connection.onstream = function(event) {
            var existing = document.getElementById(event.streamid);
            if(existing && existing.parentNode) {
              existing.parentNode.removeChild(existing);
            }
            event.mediaElement.removeAttribute('src');
            event.mediaElement.removeAttribute('srcObject');
            //event.mediaElement.muted = true;
            //event.mediaElement.volume = 0;
            var video = document.createElement('audio');
            try {
                video.setAttributeNode(document.createAttribute('autoplay'));
                video.setAttributeNode(document.createAttribute('playsinline'));
            } catch (e) {
                video.setAttribute('autoplay', true);
                video.setAttribute('playsinline', true);
            }
            if(event.type === 'local') {
              video.volume = 0;
              try {
                  video.setAttributeNode(document.createAttribute('muted'));
              } catch (e) {
                  video.setAttribute('muted', true);
              }
            }
            video.srcObject = event.stream;
            var width = parseInt(connection.videosContainer.clientWidth / 3) - 20;
            var mediaElement = getHTMLMediaElement(video, {
                title: event.userid,
                // buttons: ['full-screen'],
                width: 'auto',
                height: 'auto',
                // showOnMouseEnter: false
            });
            connection.videosContainer.appendChild(mediaElement);
            setTimeout(function() {
                mediaElement.media.play();
            }, 5000);
            mediaElement.id = event.streamid;
            $('#videos-container'+roomid+' .media-container .media-controls').hide();
        };


        var group_name = roomid+'_'+class_+'_'+userName;
        connection.checkPresence(group_name, function(roomExist, group_name) {
            if (roomExist === true) {
                connection.join(group_name);
            } else {
                connection.open(group_name);
                // var xxx = new WebSocket(
                //    'ws://' + window.location.host +
                //    '/ws/' + gr_chat_name + 'chatgroup/');
                
                var xxx = new WebSocket(
                    'wss://' + window.location.host +
                    '/ws/' + gr_chat_name + 'chatgroup/');

                xxx.onopen = function (event) {
                    xxx.send(JSON.stringify({
                        'message' : 'teacher_call',
                        'who' : userName,
                        'time' : 'teacher_call'
                    }));
                };
                setTimeout(function(){
                    xxx.close();
                 }, 3000);
            }
        });
    }


    function reload(){
        $('body .list_group_all').html('');
        $.ajax({
            type:'GET',
            url: "/group_data/"+class_,
            success: function(data){
                $('body .list_group_all').html(data);

                $('body .delete_gr').on('click',function(event){
                    event.stopPropagation();
                    var token = $("input[name=csrfmiddlewaretoken]").val();
                    var groupid = $(this).attr('name');
                    var r = confirm('Bạn chắc chắn xóa?');
                    var chatgroup = $(this).parent().parent().parent().parent().children('p').text();
                    if (r == true){
                        $.ajax({
                            type:'POST',
                            url:location.href,
                            data: {'delete_group':groupid, 'csrfmiddlewaretoken':token},
                            success: function(){
                                reload();
                            }
                        
                        });
                        if (dict_group_chat[chatgroup] != undefined){
                            dict_group_chat[chatgroup].close();
                            delete dict_group_chat[chatgroup];
                        };
                    }
                });

                $('body .join_gr').on('click',function(event){
                    event.stopPropagation();
                    var gr_name = $(this).attr("name");
                    $('#videos-container'+gr_name).show();
                    var gr_chat_name = $(this).parent().parent().parent().parent().children('p').first().text();
                    makeOrJoinRoom(gr_name, gr_chat_name);
                    $('body .join_gr').each(function(){
                        $(this).hide();
                    });
                    var done = $(this).next();

                    done.show();
                    done.click(function(){
                        event.stopPropagation();
                        // connection.attachStreams.forEach(function(localStream) {
                        //     localStream.stop();
                        // });
                    
                        // // close socket.io connection
                        // connection.close();

                        if (connection.isInitiator) {
                            connection.closeEntireSession(function() {
                                console.log('close');
                            });
                        } else {
                            connection.leave();
                            connection.attachStreams.forEach(function(localStream) {
                                localStream.stop();
                            });
                        }
                        $('.done_gr').hide();
                        $('body .join_gr').each(function(){
                            $(this).show();
                        });
                    });


                });
                
                click_group_chat();
                search_std();
            }
        });
    }
    reload();


    $("#save_audiocall").click(function() {
        var call_time = $("input[name=call_time]").val();
        var date = formatAMPM(new Date());
        // $.ajax({
        //     type:'POST',
        //     url:location.href,
        //     data: {'call_time': call_time, 'csrfmiddlewaretoken':token},
        //     success: function(){
        //         document.getElementById("close_modal_audiocall").click();
        //     }
        // });

        chatallSocket.send(JSON.stringify({
            'message' : call_time,
            'who' : userName,
            'time' : 'call_time'
        }));
        document.getElementById("close_modal_audiocall").click();
        countdowntime(call_time);
    });

	
    $("body #chinhsua").on('show.bs.modal', function(event){
        var button = $(event.relatedTarget);
        var title = button.parent().parent().parent().children().children('.left').children('.list-unstyled').children('li');
        title.each(function(){
            
        });
    });

    $('body #btn_random_group').on('click',function(){
		$('#group_random').modal('show');
    });
 

    $('body #btn_manual_group').on('click',function(){
		$('#group_manual').modal('show');
    });

    $('body #btn_audiocall').on('click',function(){
		$('#audiocall').modal('show');
    });
    

    $("body #group_random").on('show.bs.modal', function(event){
        $("input[name=number_mem]").val("2");
    });


    $("body #group_manual").on('show.bs.modal', function(event){
        $("input[name=groupname]").val("");
        $("input[name=search]").val("");
        $("input[name=search_std]").val("");
        $('body #list_std').empty();
    });

    $("body #audiocall").on('show.bs.modal', function(event){
        $("input[name=call_time]").val("1");
    });

    $('body').on('click', '#save_create_group', function(){
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var number_mem = $("input[name=number_mem]").val();
        $.ajax({
            type:'POST',
            url:location.href,
            data:{'csrfmiddlewaretoken': token, 'number_mem':number_mem},
            success: function(){
                document.getElementById("close_modal_create").click();
                // chatallSocket.send(JSON.stringify({
                //     'message' : 'teacher_change_group',
                //     'who' : userName,
                //     'time' : 'teacher_change_group'
                // }));
                reload();
            }
        });
    })

	$('.mail_list').on('click',function(){
        var std_username = $(this).children('p').text();
        var std_fullname = $(this).data("fullname");
        if ($('#inbox'+std_username).css('display') == 'block'){
            userSocket.send(JSON.stringify({
                'message' : 'seen',
                'who' : std_username,
                'time' : ''
            }));
            $('#inbox'+std_username).hide();
        }
        if (($('#'+std_username).length == 0) || ($("body .chat"+std_username).css('display') == 'none')){
            register_popup_teacher(std_username, std_fullname);
            //  $("body .noti_chat"+std_username).hide();
            $('body #'+std_username).children('.frame_std').show();
            //  if (typeof(Storage) !== "undefined") {
            //     var herf = $(this).attr('href');
            //     var chat = herf.substring(herf.indexOf("(")+1, herf.indexOf(")")) + ',' + std_username;
            //     // Gán dữ liệu
            //     sessionStorage.setItem(std_username, chat);
                
            //     // Lấy dữ liệu
            // } else {
            //     document.write('Trình duyệt của bạn không hỗ trợ local storage');
            // }

            if (dict_ws[std_username] == undefined){
            //    dict_ws[std_username] = new WebSocket(
            //    'ws://' + window.location.host +
            //    '/ws/' + std_username + userName +class_+'chat11/');
                 dict_ws[std_username] = new WebSocket(
                 'wss://' + window.location.host +
                 '/ws/' + std_username + userName +class_+'chat11/');
                $("body .chat"+std_username+" > ul").empty();
                var me = {};
                me.avatar = "https://cdn2.iconfinder.com/data/icons/perfect-flat-icons-2/512/User_man_male_profile_account_person_people.png";

                var you = {};
                you.avatar = "https://cdn2.iconfinder.com/data/icons/rcons-users-color/32/support_man-512.png";      

                //-- No use time. It is a javaScript effect.
                function insertChat1(who, text, time){
                    if (time === undefined){
                        time = 0;
                    }
                    var control = "";
                    var date = time;
                    
                    if (who == userName){
                        control = '<li style="padding-top: 15px;margin-left: 5em;width:75%;">' +
                                    '<div class="msj-rta macro" style="background-color: #BFE9F9;">' +
                                        '<div class="text text-r">' +
                                            '<p style="color: #444950;line-height: 17px;word-break: break-all;">'+text+'</p>' +
                                            '<p><small style="color: #444950;">'+date+'</small></p>' +
                                        '</div></div></li>';
                    }else{
                        control = '<li style="width:75%">' +
                            '<h4 style="margin-bottom: -3px;margin-left: 10%;font-size: 12px;">'+who+'</h4>'+
                            '<div class="avatar" style="padding:5px 0px 0px 10px;width: 20%;margin-left: -12%;margin-top: 5%; !important"><img class="img-circle" style="width:90%;" src="https://cdn2.iconfinder.com/data/icons/perfect-flat-icons-2/512/User_man_male_profile_account_person_people.png" /></div>'+
                            '<div class="msj-rta macro">' +
                                '<div class="text text-r">' +
                                    '<p style="color: #444950;line-height: 17px;word-break: break-all;">'+text+'</p>' +
                                    '<p><small style="color: #444950;">'+date+'</small></p>' +
                                '</div></div>' +
                            '</li>';
                    }
                    setTimeout(
                        function(){                        
                            $(".chat"+std_username).children('ul').append(control).scrollTop($(".chat"+std_username).children('ul').prop('scrollHeight'));
                        }, time);
                    
                }

                
                dict_ws[std_username].onmessage = function(e) {
                    var data = JSON.parse(e.data);
                    var message = data['message'];
                    var who = data['who'];
                    var time = data['time'];
			if (time == 'empty'){
                		$(".chat"+std_username).children('ul').empty();
        		}else{
                    		insertChat1(who, message, time);
			}
                };
            }
        }

     });

    $('body').on('click', '.xxx', function(){
        $("body .mytext").trigger({type: 'keydown', which: 13, keyCode: 13});
    })
    $("body .mytext").focus();
    $('body').on('keyup', '.mytext', function(e){
        if (e.keyCode === 13) {
            $(this).parent().parent().next().children('span').click();
        }
    })
    $('body').on('click', '.xxx', function(){
        var message = $(this).parent().parent().children().children().children('input').val();
        message = escapeHtml(message);
        var date = formatAMPM(new Date());
        if (message != ''){
            chatallSocket.send(JSON.stringify({
                'message' : message,
                'who' : userName,
                'time' : date
            }));
        }
        $(this).parent().parent().children().children().children('input').val('');
        
    })

    var dict_group_chat = {};
    function click_group_chat(){
        $('.group_class').on('click',function(){
            for(var key in dict_group_chat) {
                if (dict_group_chat[key]){
                    dict_group_chat[key].close();
                    delete dict_group_chat[key];
                }
                
            }
            var group_chat_name = $(this).children('p').first().text();
            if (dict_group_chat[group_chat_name] == undefined){
            //    dict_group_chat[group_chat_name] = new WebSocket(
            //    'ws://' + window.location.host +
            //    '/ws/' + group_chat_name + 'chatgroup/');
                dict_group_chat[group_chat_name] = new WebSocket(
                'wss://' + window.location.host +
                '/ws/' + group_chat_name + 'chatgroup/');
            }
            var group_name = $(this).children('p').next('p').text();
            $('#title-chat').html(group_name);
            $("#chat-group-text").prop('disabled', false);
            $(".frame2").children('ul').empty();
            // if (typeof(Storage) !== "undefined") {
            //     // Gán dữ liệu
            //     sessionStorage.group_chat_name = chatgroup;
            // } else {
            //     document.write('Trình duyệt của bạn không hỗ trợ local storage');
            // }
             var me = {};
             me.avatar = "https://cdn2.iconfinder.com/data/icons/perfect-flat-icons-2/512/User_man_male_profile_account_person_people.png";
    
             var you = {};
             you.avatar = "https://cdn2.iconfinder.com/data/icons/rcons-users-color/32/support_man-512.png";      
    
             //-- No use time. It is a javaScript effect.
             function insertChat2(who, text, time){
                 if (time === undefined){
                     time = 0;
                 }
                 var control = "";
                 var date = time;
                 
                 if (who == userName){
                    control = '<li style="padding-top: 15px;margin-left: 5em;width:75%;">' +
                                  '<div class="msj-rta macro" style="background-color: #BFE9F9;">' +
                                      '<div class="text text-r">' +
                                          '<p style="color: #444950;word-break: break-all;">'+text+'</p>' +
                                          '<p><small style="color: #444950;">'+date+'</small></p>' +
                                      '</div></div></li>';
                  }else{
                    control = '<li style="width:75%">' +
                        '<h4 style="margin-bottom: -3px;margin-left: 10%;font-size: 12px;">'+who+'</h4>'+
                        '<div class="avatar" style="padding:5px 0px 0px 10px !important"><img class="img-circle" style="width:90%;" src="https://cdn2.iconfinder.com/data/icons/perfect-flat-icons-2/512/User_man_male_profile_account_person_people.png" /></div>'+
                        '<div class="msj-rta macro">' +
                            '<div class="text text-r">' +
                                '<p style="color: #444950;word-break: break-all;">'+text+'</p>' +
                                '<p><small style="color: #444950;">'+date+'</small></p>' +
                            '</div></div>' +
                        '</li>';
                  }
                 setTimeout(
                     function(){                        
                         $(".frame2").children('ul').append(control).scrollTop($(".frame2").children('ul').prop('scrollHeight'));
                     }, time);
                 
             }
    
             
            dict_group_chat[group_chat_name].onmessage = function(e) {
                var data = JSON.parse(e.data);
                var message = data['message'];
                var who = data['who'];
                var time = data['time'];
                if (time == 'history_noti'){
                    $('.noti_noti').prepend(message);
                }else if (message.includes('Giao bài tập')){
                    $('.noti_noti').prepend(message);
                    try {
                        $('body .num_noti').remove();
                    }
                    catch(err) {
                    }
                    $('body .chat_noti').show();
                }else if (time == 'empty'){
                        $(".frame2").children('ul').empty();
                }else{
                    insertChat2(who, message, time);
                }
            };

            $('body').on('click', '.zzz', function(){
                $("body .mytext2").trigger({type: 'keydown', which: 13, keyCode: 13});
            })
            $("body .mytext2").focus();
            $('body').on('keyup', '.mytext2', function(e){
                if (e.keyCode === 13) {
                    $(this).parent().parent().next().children('span').click();
                }
            })
    
        });

        $('body').on('click', '.zzz', function(){
            var message = $(this).parent().parent().children().children().children('input').val();
            var group_chat_name =  class_+'gr_'+userName+'gr_'+ $('#title-chat').text();
            message = escapeHtml(message);
            var date = formatAMPM(new Date());
            if (message != ''){
                dict_group_chat[group_chat_name].send(JSON.stringify({
                    'message' : message,
                    'who' : userName,
                    'time' : date
                }));
            }
            $(this).parent().parent().children().children().children('input').val('');
            
        })
    
    }
    
    function search_std(){
        var options_std = {
            url: "/std/"+class_+'/'+userName,
            getValue: function(element){
                return element.fullname;
             },
            template: {
                type: "description",
                fields: {
                    description: "username"
                }
            },
            
            list: {
                match: {
                    enabled: true
                },
                onChooseEvent: function() {
                    var fullname = $("#search_std").getSelectedItemData().fullname;
                    var username = $("#search_std").getSelectedItemData().username;
                    var element = '<li style="list-style: none;" ><input style="transform: scale(1.3)" type="checkbox" class="check_agent" name="'+username+'" value="'+username+'" checked >'+fullname+'</li>';
                    var list_old = $("#list_std").text();
                    if (list_old.includes(fullname) == false){
                        $('#list_std').append(element);
                    }
                    $("#search_std").val("");
                }
            },
            theme: "square"
        };
        $("#search_std").easyAutocomplete(options_std);

        $('body #list_std').on('change', '.check_agent', function() {
            $(this).parent().remove();
        });
    }

    $("#save_create_group_manual").click(function() {
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var groupname = $("input[name=groupname]").val();
        var list_std = [];
        var date = formatAMPM(new Date());
        $('#group_manual input:checkbox').each(function() {
            if ($(this).is(":checked")){
                list_std.push(this.name);
            }
        });
        $("#nameerr").html("");
        if (groupname==''){
            $("#nameerr").html("Vui lòng không để trống");
        }else{
            $.ajax({
                type:'POST',
                url:location.href,
                data: {'list_std[]': JSON.stringify(list_std), 'groupname': groupname, 'csrfmiddlewaretoken':token},
                success: function(){
                    document.getElementById("close_modal_create_manual").click();
                    reload();
                }
            });
        }
    });

    $("#phat_de").click(function(){
        if($("#ky_thi input[name='de_thi']").val() == ''){
            alert("Chưa chọn đề thi");
            return false;
        }
        $("#de_thi option").each(function(){
            if($(this).val()== $("input[name=de_thi]").val()){
                var id = $(this).data('id');
                var thoi_gian = $(this).data('thoi_gian');
                var currentdate = new Date();
                var now = `${currentdate.getHours()}:${currentdate.getMinutes()}:${currentdate.getSeconds()}`
                var data = window.btoa(id+"_"+now);
                var date = formatAMPM(new Date());
                var href = location.href.split('/')[0]+location.href.split('/')[1]+location.href.split('/')[2]+"/student/exam_"+data
                chatallSocket.send(JSON.stringify({
                  'message' : `<li><a href="/student/exam_${data}"><span class="image"><img src="/static/images/img.jpg" alt="Profile Image" /></span><span><span>`+userName+`</span><span class="time">`+date+`</span></span><span class="message">Bắt đầu làm bài thi: ${$(this).val()}</span></a></li>`,
                  'who' : userName,
                  'time' : date
                }));
                $('#ky_thi').modal("hide");
                return false;
            }
        });
    });

    $("#send").on("show.bs.modal", function(event){
        var btn = $(event.relatedTarget);
        var group = btn.attr('name');
        $("#send_title").text("Giao bài tập cho "+group);
        $("#send input[name=gr_name]").val(group);
        $("#send input[name='bai_tap']").val("");
    });

    $("#ky_thi").on("show.bs.modal", function(event){
        $("#ky_thi input[name='de_thi']").val("");
    });

    $("#send_bai_tap").click(function(){
        if($("#send input[name='bai_tap']").val() == ''){
            alert("Chưa chọn bài tập");
            return false;
        }
        $("#ds_bai_tap option").each(function(){
            if($(this).val()== $("input[name=bai_tap]").val()){
                var id = $(this).data('id');
                var thoi_gian = $(this).data('thoi_gian');
                var currentdate = new Date();
                var now = `${currentdate.getHours()}:${currentdate.getMinutes()}:${currentdate.getSeconds()}`
                var data = window.btoa(id+"_"+now);
                var date = formatAMPM(new Date());
                var href = location.href.split('/')[0]+location.href.split('/')[1]+location.href.split('/')[2]+"/student/exam_"+data
                var group = $("#send input[name='gr_name']").val();
                if(group == "tất cả"){
                    chatallSocket.send(JSON.stringify({
                        'message' : `<li><a href="/student/exam_${data}"><span class="image"><img src="/static/images/img.jpg" alt="Profile Image" /></span><span><span>`+userName+`</span><span class="time">`+date+`</span></span><span class="message">Giao bài tập: ${$(this).val()}</span></a></li>`,
                        'who' : userName,
                        'time' : date
                    }));
                }else{
                    var group_chat_name =  class_ +'gr_'+userName+'gr_'+group
                    dict_group_chat[group_chat_name].send(JSON.stringify({
                        'message' : `<li><a href="/student/exam_${data}"><span class="image"><img src="/static/images/img.jpg" alt="Profile Image" /></span><span><span>`+userName+`</span><span class="time">`+date+`</span></span><span class="message">Giao bài tập nhóm: ${$(this).val()}</span></a></li>`,
                        'who' : userName,
                        'time' : date
                    }));
                }
                $('#send').modal("hide");
                return false;
            }
        });
    });
});


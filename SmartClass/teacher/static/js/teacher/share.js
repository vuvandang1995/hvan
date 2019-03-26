$(document).ready(function(){
    // shareAllSocket = new WebSocket(
    //     'ws://' + window.location.host +
    //     '/ws/' + userName + 'shareAll'+lopht+'/');

    shareAllSocket = new WebSocket(
        'wss://' + window.location.host +
        '/ws/' + userName + 'shareAll'+lopht+'/');

    shareAllSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var message = data['message'];
        var who = data['who'];
        var time = data['time'];
        if (time == 'giotay'){
            $('#giotay_'+who).show();
        }
    };

    $("#start-screen").click(function(){
        openRoom();
        shareAllSocket.send(JSON.stringify({
            'message' : 'start_screen',
            'who' : 'start_screen',
            'time' : 'start_screen'
        }));
        $("#start-screen").hide();
        $("#share-screen").show();
        $("#stop-screen").show();
        $("#back").hide();
    });

    $("#stop-screen").click(function(){
        closeRoom();
        shareAllSocket.send(JSON.stringify({
            'message' : 'stop_screen',
            'who' : 'stop_screen',
            'time' : 'stop_screen'
        }));
        $(".giotay_std").children().attr('class','fa fa-hand-paper-o')
        $(".giotay_std").hide();
        $("#start-screen").show();
        $("#share-screen").hide();
        $("#stop-screen").hide();
        $("#back").show();
    });

    $('#back').click(function(){
        window.history.back();
    });

    $(".giotay_std").click(function(event){
        event.stopPropagation();
        var name = $(this).parent().parent().parent().find('p').first().text();
        if($(this).children().attr('class') == 'fa fa-hand-paper-o'){
            name
            if(confirm("Cho phép "+$(this).parent().parent().parent().data("fullname") + " phát biểu")){
                shareAllSocket.send(JSON.stringify({
                    'message' : 'enable_share',
                    'who' : name,
                    'time' : 'enable_share'
                }));
                $(this).children().attr('class','fa fa-volume-up');
            }else{
                shareAllSocket.send(JSON.stringify({
                    'message' : 'tu_choi_giotay',
                    'who' : name,
                    'time' : 'tu_choi_giotay'
                }));
                $(this).hide();
            };
        }else{
            if(confirm("Hủy quyền phát biểu của "+$(this).parent().parent().parent().data("fullname"))){
                shareAllSocket.send(JSON.stringify({
                    'message' : 'disable_share',
                    'who' : name,
                    'time' : 'disable_share'
                }));
                $(".media-container[data-username="+name+"]").remove();
                $(this).children().attr('class','fa fa-hand-paper-o');
                $(this).hide();
            };
        }
    });

    $(".mail_list").click(function(){
        if(confirm("Cho phép "+$(this).data("fullname") + " phát biểu")){
            name = $(this).find('p').first().text();
            shareAllSocket.send(JSON.stringify({
                'message' : 'enable_share',
                'who' : name,
                'time' : 'enable_share'
            }));
            $('#giotay_'+name).children().attr('class','fa fa-volume-up');
            $('#giotay_'+name).show();
        };
    });
});
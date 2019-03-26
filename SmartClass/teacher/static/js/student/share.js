$(document).ready(function(){
    // var shareAllSocket = new WebSocket(
    //    'ws://' + window.location.host +
    //    '/ws/' + teacher_name + 'shareAll'+lopht+'/');

    var shareAllSocket = new WebSocket(
        'wss://' + window.location.host +
        '/ws/' + teacher_name + 'shareAll'+lopht+'/');

    $('body').on('click', '#giotay', function(){
        shareAllSocket.send(JSON.stringify({
            'message' : 'giotay',
            'who' : userName,
            'time' : 'giotay'
        }));
        $("#giotay").hide();
        setTimeout(function(){$("#bogiotay").show();},2000);
    });

    $('body').on('click', '#bogiotay', function(){
        shareAllSocket.send(JSON.stringify({
            'message' : 'bogiotay',
            'who' : userName,
            'time' : 'bogiotay'
        }));
        $("#bogiotay").hide();
        setTimeout(function(){$("#giotay").show();},2000);
    });

    $('body').on('click', '#reconnect', function(){
        reconnect();
    });

    $('#back').click(function(){
        window.history.back();
    });

    shareAllSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var message = data['message'];
        var who = data['who'];
        var time = data['time'];
        if ((time == 'enable_share') && (userName == who)){
            NtoB();
            $("#giotay").hide();
            $("#bogiotay").hide();
            $("#share-screen").show();
        }else if (time == 'disable_share'){
            if(userName == who){
                BtoN();
                $("#giotay").show();
                $("#bogiotay").hide();
                $("#share-screen").hide();
            };
            $(".media-container[data-username="+who+"]").remove();
        }else if(time == 'start_screen'){
            BtoN();
            $("#giotay").show();
            $("#bogiotay").hide();
            $("#share-screen").hide();
        }else if(time == 'stop_screen'){
            closeRoom();
            $("#giotay").hide();
            $("#bogiotay").hide();
            $("#share-screen").hide();
//            setTimeout(function(){
//                window.history.back();
//            },2000);
        }else if ((time == 'tu_choi_giotay') && (userName == who)){
            setTimeout(function(){
                $("#giotay").show();
                $("#bogiotay").hide();
                $("#share-screen").hide();
            },2000);
        }
    };

});
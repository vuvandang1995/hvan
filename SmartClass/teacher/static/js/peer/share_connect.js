var audio_broad = new RTCMultiConnection();
var roomName = window.atob(location.href.split("_")[1]);
audio_broad.socketURL = 'https://192.168.200.4:9443/';
audio_broad.extra = {
    username: ten_dang_nhap,
    fullname: ho_ten,
};
audio_broad.getScreenConstraints = function(callback) {
    getScreenConstraints(function(error, screen_constraints) {
        if (!error) {
            screen_constraints = audio_broad.modifyScreenConstraints(screen_constraints);
            callback(error, screen_constraints);
            return;
        }
        throw error;
    });
};

audio_broad.socketMessageEvent = 'multi-broadcasters-demo';
audio_broad.session = {
    audio: true,
};


audio_broad.sdpConstraints.mandatory = {
    OfferToReceiveAudio: true,
    OfferToReceiveVideo: true
};

audio_broad.mediaConstraints.video = false;
audio_broad.enableLogs = false;
audio_broad.videosContainer = document.getElementById('videos-container');
audio_broad.onstream = function(event) {
    if(document.getElementById(event.streamid)) {
        var existing = document.getElementById(event.streamid);
        existing.parentNode.removeChild(existing);
        if(audio_broad.extra.broadcaster === false){
            BtoN();
            return false;
        }
    }
    var width = parseInt(audio_broad.videosContainer.clientWidth / 2) - 20;

    if(event.stream.isScreen === true) {
        width = audio_broad.videosContainer.clientWidth - 20;
    }

    var mediaElement = getMediaElement(event.mediaElement, {
        title: event.userid,
        buttons: ['full-screen'],
        width: width,
        showOnMouseEnter: false
    });

    audio_broad.videosContainer.appendChild(mediaElement);
    setTimeout(function() {
        mediaElement.media.play();
    }, 5000);

    mediaElement.id = event.streamid;
    var audio = mediaElement.getElementsByTagName("audio");
    mediaElement.setAttribute('data-username',event.extra.username);
    mediaElement.getElementsByClassName("media-box")[0].style.textAlign = 'center' ;
    if(audio.length == 1){
        var title = mediaElement.getElementsByTagName("h2")[0].innerHTML = event.extra.fullname
        mediaElement.getElementsByClassName("media-controls")[0].style.display = 'none' ;
        mediaElement.getElementsByClassName("media-box")[0].style.height = '30px';
    }else{
        var title = `<h2 style="color: rgb(160, 160, 160); font-size: 20px; text-shadow: rgb(255, 255, 255) 1px 1px; padding: 0px; margin: 0px;">${event.extra.fullname}</h2>`
        $("#"+mediaElement.id+" .media-box").first().prepend(title);
    }
};

//audio_broad.onspeaking = function (e) {
//    console.log("speak");
//    e.mediaElement.style.border = '1px solid red';
//};
//
//audio_broad.onsilence = function (e) {
//    console.log("silence");
//    e.mediaElement.style.border = '';
//};

audio_broad.onstreamended = function(event) {
    var mediaElement = document.getElementById(event.streamid);
    if (mediaElement) {
        mediaElement.parentNode.removeChild(mediaElement);
    }
};



function joinBroadcastLooper(roomid) {
    (function reCheckRoomPresence() {
        audio_broad.checkPresence(roomid, function(isRoomExist) {
            if (isRoomExist) {
                audio_broad.join(roomid, function() {});
                return;
            }
            setTimeout(reCheckRoomPresence, 5000);
        });
    })();
}

function NtoB(){
//    audio_broad.leave();
//    audio_broad.close();
    audio_broad.disconnect();
    audio_broad.extra.broadcaster = true;
    audio_broad.dontCaptureUserMedia = false;
    joinBroadcastLooper(roomName);
}

function BtoN(){
    audio_broad.attachStreams.forEach(function(localStream) {
        localStream.stop();
    });
//    audio_broad.leave();
//    audio_broad.close();
    audio_broad.disconnect();
    audio_broad.extra.broadcaster = false;
    audio_broad.dontCaptureUserMedia = true;
    joinBroadcastLooper(roomName);
}

function openRoom(){
    audio_broad.openOrJoin(roomName, function(isRoomExist, roomid) {});
}

$('#share-screen').click(function(){
    audio_broad.addStream({
        screen: true,
    });
});



function closeRoom(){
    audio_broad.attachStreams.forEach(function(stream) {
        stream.stop();
    });
    audio_broad.getRemoteStreams().forEach(function(reStream) {
        reStream.stop();
    });
    audio_broad.close();
    audio_broad.disconnect();
    audio_broad.closeSocket();
}

function closeRemote(){
    audio_broad.getRemoteStreams().forEach(function(reStream) {
        reStream.stop();
    });
}

function reconnect(){
    audio_broad.checkPresence(roomName, function(isRoomExist){
        if (isRoomExist){
            if(audio_broad.extra.broadcaster == true){
                NtoB();
            }else{
                BtoN();
            };
            $("#giotay").show();
            $("#bogiotay").hide();
            $("#share-screen").hide();
        };
    });
}



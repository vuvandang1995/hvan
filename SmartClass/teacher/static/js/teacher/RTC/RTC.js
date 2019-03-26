window.enableAdapter = true;

var connection = new RTCMultiConnection();
connection.socketURL = "https://192.168.200.4:443/";
connection.session = {
    audio: true,
    video: false,
    data: false
};
connection.sdpConstraints.mandatory = {
    OfferToReceiveAudio: true,
    OfferToReceiveVideo: false
};
connection.mediaConstraints.video = false;

connection.maxParticipantsAllowed = 100; // one-to-one
connection.onRoomFull = function(roomid) {
  alert('Room is full.');
};


// set this line to close room as soon as owner leaves
connection.autoCloseEntireSession = true;

// connection.onUserStatusChanged = function(event) {
//     if (event.status === 'offline') {
//       // Is the room owner here?
//       var remoteUserId = connection.sessionid; // chat_room is the room name, set higher in the script.
//       var chatters = [connection.userid] // initialize array of users with me.
//       var isUserConnectedWithYou = connection.getAllParticipants().indexOf(remoteUserId) !== -1;
//       if (isUserConnectedWithYou) {
//         // The owner is here...
//         console.log('Primary user is here. Nothing to do.');
//       } else {
//         console.log('Primary user is not here!');
//         connection.attachStreams.forEach(function(localStream) {
//             localStream.stop();
//         });

//         // close socket.io connection
//         connection.close();
//       }
//     }
// };


connection.onUserStatusChanged = function(event) {
    if (event.status === 'offline') {
        if (event.userid == connection.sessionid){
            connection.closeEntireSession(function() {
                console.log('close');
            });
        }
    }
};

connection.onstreamended = function(event) {
    var mediaElement = document.getElementById(event.streamid);
    if (mediaElement) {
        mediaElement.parentNode.removeChild(mediaElement);
    }
};
connection.onMediaError = function(e) {
    if (e.message === 'Concurrent mic process limit.') {
        if (DetectRTC.audioInputDevices.length <= 1) {
            alert('Please select external microphone. Check github issue number 483.');
            return;
        }
        var secondaryMic = DetectRTC.audioInputDevices[1].deviceId;
        connection.mediaConstraints.audio = {
            deviceId: secondaryMic
        };
        connection.join(connection.sessionid);
    }
};

connection.onclose = function() {
    connection.attachStreams.forEach(function(localStream) {
        localStream.stop();
    });
    connection.close();
};


connection.onEntireSessionClosed = function(event) {
    connection.attachStreams.forEach(function(stream) {
        stream.stop();
    });
    $('#giotay').hide();
    // don't display alert for moderator
    if (connection.userid === event.userid) return;
        console.log('close');
};
connection.onUserIdAlreadyTaken = function(useridAlreadyTaken, yourNewUserId) {
    // seems room is already opened
    connection.join(useridAlreadyTaken);
};


(function() {
    var params = {},
        r = /([^&=]+)=?([^&]*)/g;
    function d(s) {
        return decodeURIComponent(s.replace(/\+/g, ' '));
    }
    var match, search = window.location.search;
    while (match = r.exec(search.substring(1)))
        params[d(match[1])] = d(match[2]);
    window.params = params;
})();

if(navigator.connection &&
   navigator.connection.type === 'cellular' &&
   navigator.connection.downlinkMax <= 0.115) {
  alert('2G is not supported. Please use a better internet service.');
}

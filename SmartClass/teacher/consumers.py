# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from channels.auth import login, logout, get_user
import fileinput
from datetime import datetime
from datetime import timedelta
from teacher.models import *


def removeLines(path, number):
    try:
        lines = open(path).readlines()
        if(len(lines) > number):
            file = open(path,'w')
            file.writelines(lines[-number:-1])
            file.close()
    except:
        pass


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        if 'chatall' in self.room_name:
            if '*std*' in self.room_name:
                self.room_group_name = self.room_name.split('*std*')[0]
                self.std_username = self.room_name.split('*std*')[1]
            else:
                self.room_group_name = self.room_name
        elif 'chat11' in self.room_name:
            self.room_group_name = 'chat11_%s' % self.room_name
        elif 'chatgroup' in self.room_name:
            self.room_group_name = 'chatgroup_%s' % self.room_name
        else:
            self.room_group_name = self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({
                        'message': 'empty',
                        'who': 'empty',
                        'time' : 'empty'
                    }))
        try:
            f = r'notification/chat/class/'+self.room_group_name+'.txt'
            file = open(f,'r')
            # if len(open(f).readlines()) > 40:
            #     count = len(open(f).readlines()) - 40
            #     for i, line in enumerate(file):
            #         if i > count:
            #             message = line.split('^%$^%$&^')[0]
            #             who = line.split('^%$^%$&^')[1].strip()
            #             time = line.split('^%$^%$&^')[2].strip()
            #              self.send(text_data=json.dumps({
            #                     'message': message,
            #                     'who': who,
            #                     'time' : time
            #                 }))
            #         # else:
                        
            # else:
            for line in file:
                message = line.split('^%$^%$&^')[0]
                who = line.split('^%$^%$&^')[1].strip()
                time = line.split('^%$^%$&^')[2].strip()
                self.send(text_data=json.dumps({
                        'message': message,
                        'who': who,
                        'time' : time,
                        'an' : 'an_tab_chat'
                    }))
        except:
            pass

        try:
            f = r'notification/chat/noti/'+self.room_group_name+'.txt'
            file = open(f,'r')
            # if len(open(f).readlines()) > 40:
            #     count = len(open(f).readlines()) - 40
            #     for i, line in enumerate(file):
            #         if i > count:
            #             message = line.split('^%$^%$&^')[0]
            #             who = line.split('^%$^%$&^')[1].strip()
            #             time = line.split('^%$^%$&^')[2].strip()
            #              self.send(text_data=json.dumps({
            #                     'message': message,
            #                     'who': who,
            #                     'time' : time
            #                 }))
            #         # else:
                        
            # else:
            for line in file:
                 self.send(text_data=json.dumps({
                        'message': line,
                        'who': line,
                        'time' : line
                    }))
        except:
            pass

        try:
            f = r'notification/chat/noti/'+self.room_group_name+'_thongbaothi'+'.txt'
            file = open(f,'r')
            # if len(open(f).readlines()) > 40:
            #     count = len(open(f).readlines()) - 40
            #     for i, line in enumerate(file):
            #         if i > count:
            #             message = line
            #             who = 'teacher'
            #             time = 'history_noti'
            #              self.send(text_data=json.dumps({
            #                     'message': message,
            #                     'who': who,
            #                     'time' : time
            #                 }))
            # else:
            for line in file:
                message = line
                who = 'teacher'
                time = 'history_noti'
                self.send(text_data=json.dumps({
                        'message': message,
                        'who': who,
                        'time' : time
                    }))
        except:
            pass

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        


    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        who = text_data_json['who']
        time = text_data_json['time']
        if message == 'seen':
            # Xóa 1 dòng trong file theo string hoặc chỉ số dòng
            f = r'notification/chat/noti/'+self.room_group_name+'.txt'
            with open(f, "r") as infile:
                lines = infile.readlines()

            with open(f, "w") as outfile:
                for i, line in enumerate(lines):
                    if who not in line:
                        outfile.write(line)
        elif 'Bắt đầu làm bài thi:' in message:
            f = r'notification/chat/noti/'+self.room_group_name+'_thongbaothi'+'.txt'
            removeLines(path=f,number=40)
            file = open(f,'a')
            file.write(message + "\n")
            file.close()
            lop = self.room_group_name.split('chatall')[1]
            ls_chi_tiet = ChiTietLop.objects.filter(lop_id=Lop.objects.get(ten=lop)).values('myuser_id')
            ls_student = MyUser.objects.filter(id__in=ls_chi_tiet, position=0)
            for std in ls_student:
                std.noti_noti = std.noti_noti + 1
                std.save()
        elif 'Giao bài tập nhóm' in message:
            f = r'notification/chat/noti/'+self.room_group_name+'_thongbaothi'+'.txt'
            removeLines(path=f,number=40)
            file = open(f,'a')
            file.write(message + "\n")
            file.close()
            lop = self.room_group_name.split('gr_')[0].split('_')[1]
            teacher_name = self.room_group_name.split('gr_')[1]
            group_name = self.room_group_name.split('gr_')[2].split('chatgroup')[0]
            nhom = Nhom.objects.get(myuser_id=MyUser.objects.get(username=teacher_name), lop_id=Lop.objects.get(ten=lop), ten_nhom=group_name)
            for std in ChiTietNhom.objects.filter(nhom_id=nhom):
                std.myuser_id.noti_noti = std.myuser_id.noti_noti + 1
                std.myuser_id.save()
        elif 'Giao bài tập' in message:
            f = r'notification/chat/noti/'+self.room_group_name+'_thongbaothi'+'.txt'
            removeLines(path=f,number=40)
            file = open(f,'a')
            file.write(message + "\n")
            file.close()
            lop = self.room_group_name.split('chatall')[1]
            ls_chi_tiet = ChiTietLop.objects.filter(lop_id=Lop.objects.get(ten=lop)).values('myuser_id')
            ls_student = MyUser.objects.filter(id__in=ls_chi_tiet, position=0)
            for std in ls_student:
                std.noti_noti = std.noti_noti + 1
                std.save()
        elif message == 'new_chat_for_teaccher':
            f = r'notification/chat/noti/'+who+'07112016_teacher'+'.txt'
            removeLines(path=f,number=40)
            file = open(f,'a')
            if time not in open(f).read():
                file.write(time + "\n")
                file.close()
                # teacher = MyUser.objects.get(username=who)
                # teacher.noti_noti = teacher.noti_noti + 1
                # teacher.save()
        elif time != 'None' and time != 'call_time' and time != 'teacher_change_group' and time != 'teacher_call' and time != 'key' and message != 'new_chat' and 'shareAll' not in self.room_group_name:
            f = r'notification/chat/class/'+self.room_group_name+'.txt'
            removeLines(path=f,number=40)
            file = open(f,'a')
            file.write(message + "^%$^%$&^"+ who +"^%$^%$&^"+ time + "\n") 
            file.close()  
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'who': who,
                'time' : time,
                'noti_noti': '.'
            }
        )
        print(self.room_group_name)


    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        who = event['who']
        time = event['time']
        noti_noti = event['noti_noti']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'who': who,
            'time': time,
            'noti_noti': noti_noti
        }))


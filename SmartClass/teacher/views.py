import random
import json
import threading
import os
import re
from itertools import chain
import base64

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login, logout
from django.core.mail import EmailMessage
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.safestring import mark_safe
from django.utils.encoding import force_bytes, force_text
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from teacher.models import *
from teacher.forms import UserForm, authenticate, UserResetForm, get_email, ResetForm
from .tokens import account_activation_token


def randomNhom(myList, number):
    list_group = []
    while len(myList) !=0 :
        if len(myList) <= number:
            list_group.append(myList)
            myList = []
        else:
            group = []
            while len(group) != number:
                a = random.choice(myList)
                del myList[myList.index(a)]
                group.append(a)
            list_group.append(group)
    return list_group


class EmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.email = email

    def run(self):
        self.email.send()


def home(request):
    user = request.user
    if user.is_authenticated and user.position == 1:
        content = {'username': mark_safe(json.dumps(user.username)),
                   'list_lop': ChiTietLop.objects.filter(myuser_id=user)}
        return render(request, 'teacher/base.html', content)
    else:
        return HttpResponseRedirect('/')


def manage_class(request, id):
    user = request.user
    if user.is_authenticated and user.position == 1:
        lop = Lop.objects.get(id=id)
        ls_chi_tiet = ChiTietLop.objects.filter(lop_id=lop).values('myuser_id')
        ls_student = MyUser.objects.filter(id__in=ls_chi_tiet, position=0)
        try:
            so_lop = int(lop.ten[:2])
        except:
            so_lop = int(lop.ten[0])
        gvm = GiaoVienMon.objects.filter(myuser_id=user).values('mon_id')
        ds_de = De.objects.filter(myuser_id=user, mon_id__in=Mon.objects.filter(id__in=gvm, lop=so_lop), dung_lam='Thi')
        ds_bai_tap = De.objects.filter(myuser_id=user, mon_id__in=Mon.objects.filter(id__in=gvm, lop=so_lop),
                                       dung_lam='Bài tập')
        content = {'username': mark_safe(json.dumps(user.username)),
                   'list_lop': ChiTietLop.objects.filter(myuser_id=user),
                   'lop_ht': lop, 'ls_student': ls_student, 'ds_de': ds_de, 'ds_bai_tap': ds_bai_tap}
        list_std = []
        for std in ls_student:
            list_std.append(std)
        if request.method == "POST":
            if 'number_mem' in request.POST:
                number_mem = request.POST['number_mem']
                list_group = randomNhom(list_std, int(number_mem))
                try:
                    Nhom.objects.filter(myuser_id=user, lop_id=lop).delete()
                except:
                    pass
                for lg in list_group:
                    ten_nhom = 'Group' +str(list_group.index(lg))
                    nhom = Nhom.objects.create(ten_nhom=ten_nhom, myuser_id=user, lop_id=lop)
                    for std in lg:
                        ChiTietNhom.objects.create(nhom_id=nhom, myuser_id=std)
            elif 'delete_group' in request.POST:
                groupid = request.POST['delete_group']
                try:
                    Nhom.objects.get(id=groupid).delete()
                except:
                    pass
            elif 'groupname' in request.POST:
                list_std = request.POST['list_std[]']
                list_std = json.loads(list_std) 
                ten_nhom = request.POST['groupname']
                try:
                    nhom = Nhom.objects.create(ten_nhom=ten_nhom, myuser_id=user, lop_id=lop)
                    for std in list_std:
                        ChiTietNhom.objects.create(nhom_id=nhom, myuser_id=MyUser.objects.get(username=std))
                except:
                    pass
        return render(request, 'teacher/manage_class.html', content)
    else:
        return HttpResponseRedirect('/')


def fullname_std_data(request, lop, teacher_name):
    user = request.user
    if user.is_authenticated and user.position == 1:
        ls_chi_tiet = ChiTietLop.objects.filter(lop_id=Lop.objects.get(ten=lop)).values('myuser_id')
        ls_student = MyUser.objects.filter(id__in=ls_chi_tiet, position=0)
        ls_nhom = Nhom.objects.filter(myuser_id=MyUser.objects.get(username=teacher_name))
        list_std = []
        for std in ls_student:
            try:
                ChiTietNhom.objects.get(myuser_id=std,nhom_id__in=ls_nhom)
            except:
                list_std.append({"username": std.username, "fullname": std.fullname})
        return JsonResponse(list_std, safe=False)
    else:
        return redirect('/')

# def group_data(request, lop):
#     user = request.user
#     if user.is_authenticated and user.position == 1:
#         # data = []
#         ls_nhom = Nhom.objects.filter(myuser_id=user, lop_id=Lop.objects.get(ten=lop))
#         html = ''
#         for lsg in ls_nhom:
#             html += '''
#                 <div class="col-md-3 col-sm-4 col-xs-12 profile_details" >
#                             <div class="well profile_view">
#                                 <div class="col-sm-12">
#                                 <h4 class="brief">
#                                 <i>'''+lsg.ten_nhom+'''</i>
#                                 <button type="button" class="btn btn-danger btn-xs delete_gr" name="'''+str(lsg.id)+'''">Xóa</button>
#                                 <button type="button" class="btn btn-primary btn-xs" data-toggle="modal" data-target="#chinhsua" name="dang">Chỉnh sửa</button>
#                                 </h4>
#                                 <div class="left col-xs-7">
#                                     <h2>Thành viên</h2>
#                                     <ul class="list-unstyled">
#             '''
#             for std in ChiTietNhom.objects.filter(nhom_id=lsg):
#                 html += '''<li id="drag1" draggable="true"><i class="fa fa-user"></i>'''+std.myuser_id.fullname+'''</li>'''
#             html += '''</ul>
#                               </div>
                              
#                             </div>
#                             <div class="col-xs-12 bottom text-center">
#                               <div class="col-xs-12 col-sm-6 emphasis">
#                               </div>
#                               <div class="col-xs-12 col-sm-6 emphasis">
#                                 <button type="button" class="btn btn-danger btn-xs delete_gr" name="'''+str(lsg.id)+'''">Xóa</button>
#                                 <button type="button" class="btn btn-primary btn-xs" data-toggle="modal" data-target="#chinhsua" name="dang">
#                                   Chỉnh sửa
#                                 </button>
#                               </div>
#                             </div>
#                           </div>
#                         </div>'''
#             # data.append(html)

#         # json_data = json.loads(json.dumps({"data": data}))
#         return HttpResponse(html)


def group_data(request, lop):
    user = request.user
    if user.is_authenticated and user.position == 1:
        # data = []
        html = ''
        try:
            ls_nhom = Nhom.objects.filter(myuser_id=user, lop_id=Lop.objects.get(ten=lop))
            for lsg in ls_nhom:
                html += '''
                        <div class="mail_list group_class">
                        <p hidden>'''+lop+'gr_'+user.username+'gr_'+lsg.ten_nhom+'''</p>
                        <p hidden>'''+lsg.ten_nhom+'''</p>
                        <div class="right">
                            <h3>'''+lsg.ten_nhom+'''<small>
                                <button type="button" class="btn btn-danger btn-xs delete_gr" name="'''+str(lsg.id)+'''">Xóa</button>
                                <button type="button" class="btn btn-primary btn-xs join_gr" name="'''+lsg.ten_nhom+'''">Audio</button>
                                <button style="display:none;" type="button" class="btn btn-primary btn-xs done_gr" name="'''+lsg.ten_nhom+'''">Kết thúc</button>
                                <button type="button" class="btn btn-success btn-xs send_gr" name="'''+lsg.ten_nhom+'''" data-toggle="modal" data-target="#send">Giao bài</button>
                                </small></h3>
                '''
                for std in ChiTietNhom.objects.filter(nhom_id=lsg):
                    html += '''<p><i class="fa fa-user"></i> '''+std.myuser_id.fullname+'''</p>'''
                html += '''<div class="mail_list">
                                <section class="make-center">
                                    <div id="videos-container'''+lsg.ten_nhom+'''">
                                    </div>
                                </section>
                            </div></div></div>'''
        except:
            pass
        return HttpResponse(html)


def manage_point(request, lop):
    user = request.user
    if user.is_authenticated and user.position == 1:
        try:
            lop_Ob = Lop.objects.get(ten=lop)
            ChiTietLop.objects.get(myuser_id=user, lop_id=lop_Ob)
        except ObjectDoesNotExist:
            return HttpResponseRedirect('/')
        if request.method == "POST":
            da_cham_diem = True
            diem_tu_luan = json.loads(request.POST['diem_tu_luan'])
            nhan_xet = json.loads(request.POST['nhan_xet'])
            diem = DiemSo.objects.get(id=request.POST['diem_id'])
            diem_cham_tay = 0
            for key, value in diem_tu_luan.items():
                diem_cham_tay += float(value)
                search = 'data-start_d="{0}"(.*)data-end_d="{0}"'.format(key)
                temp = re.search(search, diem.bai_lam)
                diem.bai_lam = diem.bai_lam.replace(temp.group(1), ' value="{}" '.format(value))
            for key, value in nhan_xet.items():
                search = 'data-start_nx="{0}"(.*)data-end_nx="{0}"'.format(key)
                temp = re.search(search, diem.bai_lam)
                diem.bai_lam = diem.bai_lam.replace(temp.group(1), ' placeholder="{}" '.format(value))
            diem.diem_cham_tay = round(diem_cham_tay, 2)
            diem.da_cham_diem = True
            diem.save()
        content = {'username': mark_safe(json.dumps(user.username)),
                   'list_lop': ChiTietLop.objects.filter(myuser_id=user),
                   'lop_ht': lop}
        return render(request, 'teacher/manage_point.html', content)
    else:
        return HttpResponseRedirect('/')


def manage_point_data(request, lop):
    user = request.user
    if user.is_authenticated and user.position == 1:
        data = []
        try:
            lop_Ob = Lop.objects.get(ten=lop)
            ChiTietLop.objects.get(myuser_id=user, lop_id=lop_Ob)
        except ObjectDoesNotExist:
            return JsonResponse(json.loads(json.dumps({"data": []})))
        else:
            ls_chi_tiet = ChiTietLop.objects.filter(lop_id=lop_Ob).values('myuser_id')
            ls_student = MyUser.objects.filter(id__in=ls_chi_tiet, position=0)
            mon_id = GiaoVienMon.objects.filter(myuser_id=user).values('mon_id')
            try:
                lp = int(lop[:2])
            except:
                lp = int(lop[0])
            mon = Mon.objects.get(id__in=mon_id, lop=lp)
            for student in ls_student:
                fullname = '<h5 id="full_{}">{}</h5>'.format(student.id, student.fullname)
                diem_thi = '<h4>'
                for diem in DiemSo.objects.filter(myuser_id=student, mon_id=mon):
                    tong_diem = diem.diem_auto + diem.diem_cham_tay
                    ten_de = ''
                    if diem.de_id is not None:
                       ten_de = diem.de_id.ten
                    if not diem.da_cham_diem:
                        loai = 'default'
                    elif tong_diem < 5.0:
                        loai = "danger"
                    elif tong_diem >= 5.0 and tong_diem < 6.5:
                        loai = "warning"
                    elif tong_diem >= 6.5 and tong_diem < 8.0:
                        loai = "info"
                    else:
                        loai = "success"
                    temp = '''
                    <span class="label label-{2}" data-id="{0}" data-toggle="modal" data-target="#point" >{3}: {1}</span>
                    '''.format(diem.id, round(tong_diem,2), loai, ten_de)
                    diem_thi += temp
                diem_thi += '</h4>'
                data.append([fullname, diem_thi])
        big_data = {"data": data}
        json_data = json.loads(json.dumps(big_data))
        return JsonResponse(json_data)


def manage_point_detail(request, id):
    user = request.user
    if user.is_authenticated and user.position == 1:
        diem = DiemSo.objects.get(id=id)
        content = '''
        <input type='hidden' name='diem_id' value="{6}">
        <div class="row">
            <div class="col-md-2" style="text-align:center">
                <p style="color:red; font-size: 50px;border: 2px solid gray; border-radius: 5px;">{5}</p>
            </div>
            <div class="col-md-10">
                <div class="row">
                    <div class="col-md-6 col-sm-6 col-xs-12 form-group has-feedback">
                      <input type="text" class="form-control has-feedback-left" value="{0}" readonly>
                      <span class="fa fa-user form-control-feedback left" aria-hidden="true"></span>
                    </div>
                    <div class="col-md-6 col-sm-6 col-xs-12 form-group has-feedback">
                      <input type="text" class="form-control has-feedback-left" value="{1}" readonly>
                      <span class="fa fa-book form-control-feedback left" aria-hidden="true"></span>
                    </div>
                    <div class="col-md-6 col-sm-6 col-xs-12 form-group has-feedback">
                      <input type="date" class="form-control has-feedback-left" value="{2}" readonly>
                      <span class="fa fa-calendar form-control-feedback left" aria-hidden="true"></span>
                    </div>
                    <div class="col-md-6 col-sm-6 col-xs-12 form-group has-feedback">
                      <input type="text" class="form-control has-feedback-left" value="{3}" readonly>
                      <span class="fa fa-clock-o form-control-feedback left" aria-hidden="true"></span>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-12 col-sm-12 col-xs-12">
            {4}
        </div>
        <div class="clearfix"></div>
        '''.format(diem.myuser_id.fullname, diem.de_id.ten,str(diem.ngay_lam),
                   diem.loai_diem, diem.bai_lam, diem.diem_auto + diem.diem_cham_tay, diem.id)
        return HttpResponse(content)    
    

def manage_de(request):
    user = request.user
    if user.is_authenticated and user.position == 1:
        if request.method == "POST":
            if 'random' in request.POST:
                mon = Mon.objects.get(id=request.POST['mon'])
                chi_tiet_so_luong = json.loads(request.POST['chi_tiet_so_luong'])
                cau_truc = json.loads(request.POST['cau_truc'])
                trac_nhiem_de = CauHoi.objects.filter(do_kho=0, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                      dang_cau_hoi__contains="Trắc nhiệm")
                if chi_tiet_so_luong['r_tn_d'] > len(trac_nhiem_de):
                    return HttpResponse("Không đủ số lượng câu hỏi trắc nhiệm dễ trong ngân hàng câu hỏi")

                trac_nhiem_tb = CauHoi.objects.filter(do_kho=1, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                      dang_cau_hoi__contains="Trắc nhiệm")
                if chi_tiet_so_luong['r_tn_tb'] > len(trac_nhiem_tb):
                    return HttpResponse("Không đủ số lượng câu hỏi trắc nhiệm trung bình trong ngân hàng câu hỏi")

                trac_nhiem_kho = CauHoi.objects.filter(do_kho=2, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                       dang_cau_hoi__contains="Trắc nhiệm")
                if chi_tiet_so_luong['r_tn_k'] > len(trac_nhiem_kho):
                    return HttpResponse("Không đủ số lượng câu hỏi trắc nhiệm khó trong ngân hàng câu hỏi")

                dien_tu_de = CauHoi.objects.filter(do_kho=0, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                   dang_cau_hoi__contains="Điền từ")
                if chi_tiet_so_luong['r_dt_d'] > len(dien_tu_de):
                    return HttpResponse("Không đủ số lượng câu hỏi điền từ dễ trong ngân hàng câu hỏi")

                dien_tu_tb = CauHoi.objects.filter(do_kho=1, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                   dang_cau_hoi__contains="Điền từ")
                if chi_tiet_so_luong['r_dt_tb'] > len(dien_tu_tb):
                    return HttpResponse("Không đủ số lượng câu hỏi điền từ trung bình trong ngân hàng câu hỏi")
                dien_tu_kho = CauHoi.objects.filter(do_kho=2, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                    dang_cau_hoi__contains="Điền từ")
                if chi_tiet_so_luong['r_dt_k'] > len(dien_tu_kho):
                    return HttpResponse("Không đủ số lượng câu hỏi điền từ khó trong ngân hàng câu hỏi")

                tu_luan_de = CauHoi.objects.filter(do_kho=0, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                   dang_cau_hoi__contains="Tự luận")
                if chi_tiet_so_luong['r_tl_d'] > len(tu_luan_de):
                    return HttpResponse("Không đủ số lượng câu hỏi tự luận dễ trong ngân hàng câu hỏi")

                tu_luan_tb = CauHoi.objects.filter(do_kho=1, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                   dang_cau_hoi__contains="Tự luận")
                if chi_tiet_so_luong['r_tl_tb'] > len(tu_luan_tb):
                    return HttpResponse("Không đủ số lượng câu hỏi tự luận trung bình trong ngân hàng câu hỏi")

                tu_luan_kho = CauHoi.objects.filter(do_kho=2, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                    dang_cau_hoi__contains="Tự luận")
                if chi_tiet_so_luong['r_tl_k'] > len(tu_luan_kho):
                    return HttpResponse("Không đủ số lượng câu hỏi tự luận khó trong ngân hàng câu hỏi")

                de = De.objects.create(ten=request.POST['ten_de'], dung_lam=request.POST['loai_de'],
                                       thoi_gian=request.POST['thoi_gian'], cau_truc=request.POST['cau_truc'],
                                       so_luong=request.POST['so_luong'],
                                       chi_tiet_so_luong=request.POST['chi_tiet_so_luong'],
                                       mon_id=mon, myuser_id=user)
                diem_tn = round(float(cau_truc['r_pt_tn'] / 10 / (chi_tiet_so_luong['r_tn_d'] +
                                                                  chi_tiet_so_luong['r_tn_tb'] +
                                                                  chi_tiet_so_luong['r_tn_k'])), 2)
                diem_dt = round(float(cau_truc['r_pt_dt'] / 10 / (chi_tiet_so_luong['r_dt_d'] +
                                                                  chi_tiet_so_luong['r_dt_tb'] +
                                                                  chi_tiet_so_luong['r_dt_k'])), 2)
                diem_tl = round(float(cau_truc['r_pt_tl'] / 10 / (chi_tiet_so_luong['r_tl_d'] +
                                                                  chi_tiet_so_luong['r_tl_tb'] +
                                                                  chi_tiet_so_luong['r_tl_k'])), 2)
                randomCauHoi(trac_nhiem_de, chi_tiet_so_luong['r_tn_d'], de, diem_tn)
                randomCauHoi(trac_nhiem_tb, chi_tiet_so_luong['r_tn_tb'], de, diem_tn)
                randomCauHoi(trac_nhiem_kho, chi_tiet_so_luong['r_tn_k'], de, diem_tn)
                randomCauHoi(dien_tu_de, chi_tiet_so_luong['r_dt_d'], de, diem_dt)
                randomCauHoi(dien_tu_tb, chi_tiet_so_luong['r_dt_tb'], de, diem_dt)
                randomCauHoi(dien_tu_kho, chi_tiet_so_luong['r_dt_k'], de, diem_dt)
                randomCauHoi(tu_luan_de, chi_tiet_so_luong['r_tl_d'], de, diem_tl)
                randomCauHoi(tu_luan_tb, chi_tiet_so_luong['r_tl_tb'], de, diem_tl)
                randomCauHoi(tu_luan_kho, chi_tiet_so_luong['r_tl_k'], de, diem_tl)
            elif 'delete' in request.POST:
                De.objects.get(id=request.POST['id']).delete()
            else:
                mon = Mon.objects.get(id=request.POST['mon'])
                chi_tiet_so_luong = json.loads(request.POST['chi_tiet_so_luong'])
                cau_truc = json.loads(request.POST['cau_truc'])
                de = De.objects.create(ten=request.POST['ten_de'], dung_lam=request.POST['loai_de'],
                                       thoi_gian=request.POST['thoi_gian'], cau_truc=request.POST['cau_truc'],
                                       so_luong=request.POST['so_luong'],
                                       chi_tiet_so_luong=request.POST['chi_tiet_so_luong'],
                                       mon_id=mon, myuser_id=user)
                diem_tn = round(float(cau_truc['pt_tn'] / 10 / chi_tiet_so_luong['sl_tn']), 2)
                diem_dt = round(float(cau_truc['pt_dt'] / 10 / chi_tiet_so_luong['sl_dt']), 2)
                diem_tl = round(float(cau_truc['pt_tl'] / 10 / chi_tiet_so_luong['sl_tl']), 2)
                for temp in json.loads(request.POST['list_ques']):
                    id, don = temp.split("_")
                    if don == 'don':
                        ch = CauHoi.objects.get(id=int(id))
                        if "Trắc nhiệm" in ch.dang_cau_hoi:
                            diem = diem_tn
                        elif "Điền từ" in ch.dang_cau_hoi:
                            diem = diem_dt
                        elif "Tự luận" in ch.dang_cau_hoi:
                            diem = diem_tl
                        ChiTietDe.objects.create(cau_hoi_id=ch, de_id=de, diem=diem)
                    else:
                        ch = CauHoiDa.objects.get(id=int(id))
                        if "Trắc nhiệm" in ch.dang_cau_hoi:
                            diem = diem_tn
                        elif "Điền từ" in ch.dang_cau_hoi:
                            diem = diem_dt
                        elif "Tự luận" in ch.dang_cau_hoi:
                            diem = diem_tl
                        ChiTietDe.objects.create(cau_hoi_da_id=ch, de_id=de, diem=diem*ch.so_cau_hoi)
        content = {'username': mark_safe(json.dumps(user.username)),
                   'list_lop': ChiTietLop.objects.filter(myuser_id=user),
                   'list_mon': GiaoVienMon.objects.filter(myuser_id=user)}
        return render(request, 'teacher/manage_exam.html', content)
    else:
        return HttpResponseRedirect('/')


def de_manual(request):
    user = request.user
    if user.is_authenticated and user.position == 1:
        if request.method == "POST":
            mon = Mon.objects.get(id=request.POST['mon'])
            chi_tiet_so_luong = json.loads(request.POST['chi_tiet_so_luong'])
            cau_truc = json.loads(request.POST['cau_truc'])
            de = De.objects.create(ten=request.POST['ten_de'], dung_lam=request.POST['loai_de'],
                                   thoi_gian=request.POST['thoi_gian'], cau_truc=request.POST['cau_truc'],
                                   so_luong=request.POST['so_luong'],
                                   chi_tiet_so_luong=request.POST['chi_tiet_so_luong'],
                                   mon_id=mon, myuser_id=user)
            diem_tn = round(float(cau_truc['pt_tn'] / 10 / chi_tiet_so_luong['sl_tn']), 2)
            diem_dt = round(float(cau_truc['pt_dt'] / 10 / chi_tiet_so_luong['sl_dt']), 2)
            diem_tl = round(float(cau_truc['pt_tl'] / 10 / chi_tiet_so_luong['sl_tl']), 2)
            for temp in json.loads(request.POST['list_ques']):
                id, don = temp.split("_")
                if don == 'don':
                    ch = CauHoi.objects.get(id=int(id))
                    if "Trắc nhiệm" in ch.dang_cau_hoi:
                        diem = diem_tn
                    elif "Điền từ" in ch.dang_cau_hoi:
                        diem = diem_dt
                    elif "Tự luận" in ch.dang_cau_hoi:
                        diem = diem_tl
                    ChiTietDe.objects.create(cau_hoi_id=ch, de_id=de, diem=diem)
                else:
                    ch = CauHoiDa.objects.get(id=int(id))
                    if "Trắc nhiệm" in ch.dang_cau_hoi:
                        diem = diem_tn
                    elif "Điền từ" in ch.dang_cau_hoi:
                        diem = diem_dt
                    elif "Tự luận" in ch.dang_cau_hoi:
                        diem = diem_tl
                    ChiTietDe.objects.create(cau_hoi_da_id=ch, de_id=de, diem=diem * ch.so_cau_hoi)
            return JsonResponse({"status": "success", "messages": "Thành công"})
        content = {'username': mark_safe(json.dumps(user.username)),
                   'list_lop': ChiTietLop.objects.filter(myuser_id=user),
                   'list_mon': GiaoVienMon.objects.filter(myuser_id=user)}
        return render(request, 'teacher/manage_exam_manual.html', content)
    else:
        return HttpResponseRedirect('/')


def de_auto(request):
    user = request.user
    if user.is_authenticated and user.position == 1:
        if request.method == "POST":
            mon = Mon.objects.get(id=request.POST['mon'])
            chi_tiet_so_luong = json.loads(request.POST['chi_tiet_so_luong'])
            cau_truc = json.loads(request.POST['cau_truc'])
            trac_nhiem_de = CauHoi.objects.filter(do_kho=0, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                  dang_cau_hoi__contains="Trắc nhiệm")
            if chi_tiet_so_luong['r_tn_d'] > len(trac_nhiem_de):
                return JsonResponse({"status": "failure",
                                     "messages": "Không đủ số lượng câu hỏi trắc nhiệm dễ trong ngân hàng câu hỏi"})
            trac_nhiem_tb = CauHoi.objects.filter(do_kho=1, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                  dang_cau_hoi__contains="Trắc nhiệm")
            if chi_tiet_so_luong['r_tn_tb'] > len(trac_nhiem_tb):
                return JsonResponse({"status": "failure",
                                     "messages": "Không đủ số lượng câu hỏi trắc nhiệm trung bình"
                                                 " trong ngân hàng câu hỏi"})

            trac_nhiem_kho = CauHoi.objects.filter(do_kho=2, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                   dang_cau_hoi__contains="Trắc nhiệm")
            if chi_tiet_so_luong['r_tn_k'] > len(trac_nhiem_kho):
                return JsonResponse({"status": "failure",
                                     "messages": "Không đủ số lượng câu hỏi trắc nhiệm khó trong ngân hàng câu hỏi"})

            dien_tu_de = CauHoi.objects.filter(do_kho=0, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                               dang_cau_hoi__contains="Điền từ")
            if chi_tiet_so_luong['r_dt_d'] > len(dien_tu_de):
                return JsonResponse({"status": "failure",
                                     "messages": "Không đủ số lượng câu hỏi điền từ dễ trong ngân hàng câu hỏi"})

            dien_tu_tb = CauHoi.objects.filter(do_kho=1, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                               dang_cau_hoi__contains="Điền từ")
            if chi_tiet_so_luong['r_dt_tb'] > len(dien_tu_tb):
                return JsonResponse({"status": "failure",
                                     "messages": "Không đủ số lượng câu hỏi điền từ trung bình trong ngân hàng câu hỏi"})
            dien_tu_kho = CauHoi.objects.filter(do_kho=2, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                dang_cau_hoi__contains="Điền từ")
            if chi_tiet_so_luong['r_dt_k'] > len(dien_tu_kho):
                return JsonResponse({"status": "failure",
                                     "messages": "Không đủ số lượng câu hỏi điền từ khó trong ngân hàng câu hỏi"})

            tu_luan_de = CauHoi.objects.filter(do_kho=0, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                               dang_cau_hoi__contains="Tự luận")
            if chi_tiet_so_luong['r_tl_d'] > len(tu_luan_de):
                return JsonResponse({"status": "failure",
                                     "messages": "Không đủ số lượng câu hỏi tự luận dễ trong ngân hàng câu hỏi"})

            tu_luan_tb = CauHoi.objects.filter(do_kho=1, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                               dang_cau_hoi__contains="Tự luận")
            if chi_tiet_so_luong['r_tl_tb'] > len(tu_luan_tb):
                return JsonResponse({"status": "failure",
                                     "messages": "Không đủ số lượng câu hỏi tự luận trung bình trong ngân hàng câu hỏi"})

            tu_luan_kho = CauHoi.objects.filter(do_kho=2, don=True, mon_id=mon, dung_lam=request.POST['loai_de'],
                                                dang_cau_hoi__contains="Tự luận")
            if chi_tiet_so_luong['r_tl_k'] > len(tu_luan_kho):
                return JsonResponse({"status": "failure",
                                     "messages": "Không đủ số lượng câu hỏi tự luận khó trong ngân hàng câu hỏi"})

            de = De.objects.create(ten=request.POST['ten_de'], dung_lam=request.POST['loai_de'],
                                   thoi_gian=request.POST['thoi_gian'], cau_truc=request.POST['cau_truc'],
                                   so_luong=request.POST['so_luong'],
                                   chi_tiet_so_luong=request.POST['chi_tiet_so_luong'],
                                   mon_id=mon, myuser_id=user)
            diem_tn = round(float(cau_truc['r_pt_tn'] / 10 / (chi_tiet_so_luong['r_tn_d'] +
                                                              chi_tiet_so_luong['r_tn_tb'] +
                                                              chi_tiet_so_luong['r_tn_k'])), 2)
            diem_dt = round(float(cau_truc['r_pt_dt'] / 10 / (chi_tiet_so_luong['r_dt_d'] +
                                                              chi_tiet_so_luong['r_dt_tb'] +
                                                              chi_tiet_so_luong['r_dt_k'])), 2)
            diem_tl = round(float(cau_truc['r_pt_tl'] / 10 / (chi_tiet_so_luong['r_tl_d'] +
                                                              chi_tiet_so_luong['r_tl_tb'] +
                                                              chi_tiet_so_luong['r_tl_k'])), 2)
            randomCauHoi(trac_nhiem_de, chi_tiet_so_luong['r_tn_d'], de, diem_tn)
            randomCauHoi(trac_nhiem_tb, chi_tiet_so_luong['r_tn_tb'], de, diem_tn)
            randomCauHoi(trac_nhiem_kho, chi_tiet_so_luong['r_tn_k'], de, diem_tn)
            randomCauHoi(dien_tu_de, chi_tiet_so_luong['r_dt_d'], de, diem_dt)
            randomCauHoi(dien_tu_tb, chi_tiet_so_luong['r_dt_tb'], de, diem_dt)
            randomCauHoi(dien_tu_kho, chi_tiet_so_luong['r_dt_k'], de, diem_dt)
            randomCauHoi(tu_luan_de, chi_tiet_so_luong['r_tl_d'], de, diem_tl)
            randomCauHoi(tu_luan_tb, chi_tiet_so_luong['r_tl_tb'], de, diem_tl)
            randomCauHoi(tu_luan_kho, chi_tiet_so_luong['r_tl_k'], de, diem_tl)
            return JsonResponse({"status": "success", "messages": "Thành công"})
        content = {'username': mark_safe(json.dumps(user.username)),
                   'list_lop': ChiTietLop.objects.filter(myuser_id=user),
                   'list_mon': GiaoVienMon.objects.filter(myuser_id=user)}
        return render(request, 'teacher/manage_exam_auto.html', content)
    else:
        return HttpResponseRedirect('/')


def de_data(request, all):
    user = request.user
    if user.is_authenticated and user.position == 1:
        data = []
        if all == 0:
            list_exam = De.objects.filter(myuser_id=user)
        else:
            user_mon = GiaoVienMon.objects.filter(myuser_id=user).values('mon_id')
            list_exam = CauHoi.objects.filter(mon_id__in=user_mon)
        for exam in list_exam:
            mon = '<p data-id="{}">{} - {}</p>'.format(exam.id, exam.mon_id.ten, exam.mon_id.lop)
            if all == 0:
                data.append([mon, exam.ten, exam.dung_lam, str(exam.thoi_gian) + " phút", str(exam.ngay_tao)])
            else:
                data.append([mon, exam.ten, exam.dung_lam, str(exam.thoi_gian) + " phút", exam.myuser_id.fullname,
                             str(exam.ngay_tao)])
        json_data = json.loads(json.dumps({"data": data}))
        return JsonResponse(json_data)


def chi_tiet_de_data(request, id):
    user = request.user
    if user.is_authenticated and user.position == 1:
        list_ques = ChiTietDe.objects.filter(de_id=id)
        content = '<input name="exam_id" value="{}" hidden>'.format(id)
        for i, ch in enumerate(list_ques):
            dap_an = ''
            if ch.cau_hoi_da_id is not None:
                ques = ch.cau_hoi_da_id
                for index, cht in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ques)):
                    result = re.search('<p>(.*)</p>', cht.cau_hoi_id.noi_dung)
                    dap_an += '''
                    <p>{3}.{0} ({2} điểm):{1}</p>
                    '''.format(index+1, result.group(1), round(ch.diem / ques.so_cau_hoi, 2), i+1)
                    if "Trắc nhiệm" in ques.dang_cau_hoi:
                        for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=cht.cau_hoi_id)):
                            s = chr(ord(str(k)) + 17)
                            if da.dap_an_dung:
                                dung = '(Đúng)'
                            else:
                                dung = ''
                            result = re.search('<p>(.*)</p>', da.noi_dung)
                            dap_an += '''
                            <p>{0}: {2} {1}</p>
                            '''.format(s, dung, result.group(1))
            else:
                ques = ch.cau_hoi_id
                if "Trắc nhiệm" in ques.dang_cau_hoi:
                    for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=ques)):
                        s = chr(ord(str(k)) + 17)
                        if da.dap_an_dung:
                            dung = '(Đúng)'
                        else:
                            dung = ''
                        result = re.search('<p>(.*)</p>', da.noi_dung)
                        dap_an += '''
                        <p>{0}: {2} {1}</p>
                        '''.format(s, dung, result.group(1))

                elif "Điền từ" in ques.dang_cau_hoi:
                    for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=ques)):
                        result = re.search('<p>(.*)</p>', da.noi_dung)
                        dap_an += '''
                        <p>({0}): {1}</p>
                        '''.format(k + 1, result.group(1))
            media = ''
            if "Hình ảnh" in ques.dang_cau_hoi:
                media = '<img style="max-height:600px;max-width:600px; display: block; margin-left: auto;margin-right: auto;" src="/media/{}" alt="không tồn tại" />'.format(ques.dinh_kem)
            elif "Âm thanh" in ques.dang_cau_hoi:
                media = '<br><audio controls width="100%" src="/media/{}"></audio>'.format(ques.dinh_kem)
            elif "Video" in ques.dang_cau_hoi:
                media = '<video controls width="100%" src="/media/{}"></video>'.format(ques.dinh_kem)
            else:
                media = '<a href="/media/{}" download></a>'.format(ques.dinh_kem)
            content += '''
            <label>Câu hỏi {0} ({4} điểm):</label>
            {3}
            <ul class="list-unstyled msg_list">
            <li><a>{1}{2}</a></li>
            '''.format(i+1, ques.noi_dung, dap_an, media, ch.diem)
        return HttpResponse(content)


def manage_question(request):
    user = request.user
    if user.is_authenticated and user.position == 1:
        content = {'username': mark_safe(json.dumps(user.username)),
                   'list_lop': ChiTietLop.objects.filter(myuser_id=user),
                   'list_mon': GiaoVienMon.objects.filter(myuser_id=user)}
        if request.method == 'POST':
            if 'nd_cau_hoi' in request.POST:
                ch = CauHoiDa.objects.get(id=request.POST['id'])
                ch.noi_dung = request.POST['noi_dung']
                if request.FILES.get('dinh_kem') is not None:
                    try:
                        os.remove(os.path.join(settings.MEDIA_ROOT, str(ch.dinh_kem)))
                    except:
                        pass
                    ch.dinh_kem = request.FILES['dinh_kem']
                    ch.save()
                    handle_uploaded_file(request.FILES['dinh_kem'])
                ch.save()
                nd_cau_hoi = json.loads(request.POST['nd_cau_hoi'])
                for i, ques in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ch)):
                    chdon = CauHoi.objects.get(id=ques.cau_hoi_id.id)
                    chdon.noi_dung = nd_cau_hoi[i]
                    if "Trắc nhiệm" in ch.dang_cau_hoi:
                        DapAn.objects.filter(cau_hoi_id=chdon).delete()
                        dap_an = json.loads(request.POST['dap_an'])
                        nd_dap_an = json.loads(request.POST['nd_dap_an'])
                        so_dap_an_dung = 0
                        so_dap_an = int(len(dap_an) / ch.so_cau_hoi)
                        for k in range(i*so_dap_an, i*so_dap_an + so_dap_an):
                            if dap_an[k] == 0:
                                dung = False
                            else:
                                dung = True
                                so_dap_an_dung += 1
                            DapAn.objects.create(cau_hoi_id=chdon, mon_id=ch.mon_id, noi_dung=nd_dap_an[k],
                                                 dap_an_dung=dung)
                        chdon.so_dap_an_dung = so_dap_an_dung
                    chdon.save()
            else:
                ch = CauHoi.objects.get(id=request.POST['id'])
                ch.noi_dung = request.POST['noi_dung']
                if request.FILES.get('dinh_kem') is not None:
                    try:
                        os.remove(os.path.join(settings.MEDIA_ROOT, str(ch.dinh_kem)))
                    except:
                        pass
                    ch.dinh_kem = request.FILES['dinh_kem']
                    ch.save()
                    handle_uploaded_file(request.FILES['dinh_kem'])
                ch.save()
                if "Trắc nhiệm" in ch.dang_cau_hoi:
                    DapAn.objects.filter(cau_hoi_id=ch).delete()
                    dap_an = json.loads(request.POST['dap_an'])
                    nd_dap_an = json.loads(request.POST['nd_dap_an'])
                    for i in range(len(dap_an)):
                        if dap_an[i] == 0:
                            dung = False
                        else:
                            dung = True
                        DapAn.objects.create(cau_hoi_id=ch, mon_id=ch.mon_id, noi_dung=nd_dap_an[i],
                                             dap_an_dung=dung)
                elif "Điền từ" in ch.dang_cau_hoi:
                    DapAn.objects.filter(cau_hoi_id=ch).delete()
                    nd_dap_an = json.loads(request.POST['nd_dap_an'])
                    for nd in nd_dap_an:
                        DapAn.objects.create(cau_hoi_id=ch, mon_id=ch.mon_id, noi_dung=nd, dap_an_dung=True)
        return render(request, 'teacher/manage_question.html', content)
    else:
        return HttpResponseRedirect('/')


def question_create(request):
    user = request.user
    if user.is_authenticated and user.position == 1:
        content = {'username': mark_safe(json.dumps(user.username)),
                   'list_lop': ChiTietLop.objects.filter(myuser_id=user),
                   'list_mon': GiaoVienMon.objects.filter(myuser_id=user)}
        if request.method == 'POST':
            ten_mon, lop_mon = request.POST['mon'].split(" - ")
            mon = Mon.objects.get(ten=ten_mon, lop=lop_mon)
            if request.POST['do_kho'] == 'Dễ':
                do_kho = 0
            elif request.POST['do_kho'] == 'Trung bình':
                do_kho = 1
            else:
                do_kho = 2
            if 'nd_cau_hoi' in request.POST:
                ch = CauHoiDa.objects.create(myuser_id=user, mon_id=mon, noi_dung=request.POST['noi_dung'],
                                             do_kho=do_kho, chu_de=request.POST['chu_de'],
                                             dung_lam=request.POST['dung_lam'],
                                             so_cau_hoi=request.POST['so_cau_hoi'],
                                             dang_cau_hoi=request.POST['dang_cau_hoi'])
                i = 0
                for nd in json.loads(request.POST['nd_cau_hoi']):
                    cht = CauHoi.objects.create(myuser_id=user, mon_id=mon, noi_dung=nd, do_kho=do_kho, don=False,
                                                dung_lam=request.POST['dung_lam'], chu_de=request.POST['chu_de'],
                                                dang_cau_hoi=request.POST['dang_cau_hoi'])
                    ChiTietCauHoiDa.objects.create(cau_hoi_id=cht, cau_hoi_da_id=ch)
                    if "Trắc nhiệm" in ch.dang_cau_hoi:
                        dap_an = json.loads(request.POST['dap_an'])
                        nd_dap_an = json.loads(request.POST['nd_dap_an'])
                        for k in range(i, i + int(request.POST['so_dap_an'])):
                            if dap_an[k] == 0:
                                dung = False
                            else:
                                dung = True
                            DapAn.objects.create(cau_hoi_id=cht, mon_id=ch.mon_id, noi_dung=nd_dap_an[k],
                                                 dap_an_dung=dung)
                        i += int(request.POST['so_dap_an'])
            else:
                ch = CauHoi.objects.create(myuser_id=user, mon_id=mon, noi_dung=request.POST['noi_dung'],
                                           do_kho=do_kho, chu_de=request.POST['chu_de'], don=True,
                                           dung_lam=request.POST['dung_lam'],
                                           dang_cau_hoi=request.POST['dang_cau_hoi'])
                if "Trắc nhiệm" in ch.dang_cau_hoi:
                    dap_an = json.loads(request.POST['dap_an'])
                    nd_dap_an = json.loads(request.POST['nd_dap_an'])
                    for i in range(len(dap_an)):
                        if dap_an[i] == 0:
                            dung = False
                        else:
                            dung = True
                        DapAn.objects.create(cau_hoi_id=ch, mon_id=ch.mon_id, noi_dung=nd_dap_an[i],
                                             dap_an_dung=dung)
                elif "Điền từ" in ch.dang_cau_hoi:
                    nd_dap_an = json.loads(request.POST['nd_dap_an'])
                    for nd in nd_dap_an:
                        DapAn.objects.create(cau_hoi_id=ch, mon_id=ch.mon_id, noi_dung=nd, dap_an_dung=True)

            if request.FILES.get('dinh_kem') is not None:
                ch.dinh_kem = request.FILES['dinh_kem']
                ch.save()
        return render(request, 'teacher/manage_question_create.html', content)
    else:
        return HttpResponseRedirect('/')


def manage_question_excel(request):
    user = request.user
    if user.is_authenticated and user.position == 1:
        content = {'username': mark_safe(json.dumps(user.username)),
                   'list_mon': GiaoVienMon.objects.filter(myuser_id=user)}
        if request.method == 'POST':
            data = json.loads(request.POST['data'])
            data.remove(data[0])
            try:
                mon = Mon.objects.get(id=int(request.POST['mon']))
            except ObjectDoesNotExist:
                return JsonResponse({"status": "Failure", "messages": "Lỗi môn"})
            dang_media, dang_cau_hoi = request.POST['dang_cau_hoi'].split(" + ")
            so_cau_hoi = int(request.POST['so_cau_hoi'])
            so_dap_an = int(request.POST['so_dap_an'])
            for dt in data:
                if len(dt) == 0:
                    continue
                if dt[1] == 'Dễ':
                    do_kho = 0
                elif dt[1] == 'Trung bình':
                    do_kho = 1
                else:
                    do_kho = 2
                if dang_media != "Văn bản":
                    row = 4
                    dinh_kem = request.FILES.get(dt[3])
                    if dinh_kem is None:
                        continue
                else:
                    row = 3
                    dinh_kem = ''
                if so_cau_hoi > 1:
                    chd = CauHoiDa.objects.create(myuser_id=user, mon_id=mon, noi_dung="<p>%s</p>" % dt[2],
                                                  do_kho=do_kho, chu_de=dt[0],
                                                  dung_lam=request.POST['dung_lam'],
                                                  so_cau_hoi=so_cau_hoi,
                                                  dang_cau_hoi=request.POST['dang_cau_hoi'],
                                                  dinh_kem=dinh_kem)
                    for n in range(so_cau_hoi):
                        chi_so = row + n * (so_dap_an + 1)
                        ch = CauHoi.objects.create(myuser_id=user, mon_id=mon, noi_dung="<p>%s</p>" % dt[chi_so],
                                                   do_kho=do_kho, don=False,
                                                   dung_lam=request.POST['dung_lam'],
                                                   chu_de=dt[0],
                                                   dang_cau_hoi=request.POST['dang_cau_hoi'])
                        ChiTietCauHoiDa.objects.create(cau_hoi_id=ch, cau_hoi_da_id=chd)
                        if dang_cau_hoi == "Trắc nhiệm":
                            for k in range(so_dap_an):
                                if k == 0:
                                    dung = True
                                else:
                                    dung = False
                                DapAn.objects.create(cau_hoi_id=ch, mon_id=ch.mon_id,
                                                     noi_dung="<p>%s</p>" % dt[chi_so + 1 + k],
                                                     dap_an_dung=dung)
                        elif dang_cau_hoi == "Điền từ":
                            for k in range(so_dap_an):
                                DapAn.objects.create(cau_hoi_id=ch, mon_id=ch.mon_id,
                                                     noi_dung="<p>%s</p>" % dt[chi_so + 1 + k],
                                                     dap_an_dung=True)

                else:
                    ch = CauHoi.objects.create(myuser_id=user, mon_id=mon, noi_dung="<p>%s</p>" % dt[2],
                                               do_kho=do_kho, chu_de=dt[0], don=True,
                                               dung_lam=request.POST['dung_lam'],
                                               dang_cau_hoi=request.POST['dang_cau_hoi'],
                                               dinh_kem=dinh_kem)
                    if dang_cau_hoi == "Trắc nhiệm":
                        for k in range(so_dap_an):
                            if k == 0:
                                dung = True
                            else:
                                dung = False
                            DapAn.objects.create(cau_hoi_id=ch, mon_id=ch.mon_id, noi_dung="<p>%s</p>" % dt[row+k],
                                                 dap_an_dung=dung)
                    elif dang_cau_hoi == "Điền từ":
                        for k in range(so_dap_an):
                            DapAn.objects.create(cau_hoi_id=ch, mon_id=ch.mon_id, noi_dung="<p>%s</p>" % dt[row+k],
                                                 dap_an_dung=True)

            return JsonResponse({"status": "Success", "messages": "Thành công"})
        return render(request, 'teacher/manage_question_excel.html', content)
    else:
        return HttpResponseRedirect('/')


def question_data(request, id_mon, all, dung_lam):
    user = request.user
    if user.is_authenticated and user.position == 1:
        data = []
        try:
            if all == 0:
                list_ques = CauHoi.objects.filter(myuser_id=user, mon_id=Mon.objects.get(id=id_mon), don=True)
                list_ques_da = CauHoiDa.objects.filter(myuser_id=user, mon_id=Mon.objects.get(id=id_mon))
            else:
                if dung_lam != '':
                    list_ques = CauHoi.objects.filter(mon_id=Mon.objects.get(id=id_mon), don=True, dung_lam=dung_lam)
                    list_ques_da = CauHoiDa.objects.filter(mon_id=Mon.objects.get(id=id_mon), dung_lam=dung_lam)
                else:
                    list_ques = CauHoi.objects.filter(mon_id=Mon.objects.get(id=id_mon), don=True)
                    list_ques_da = CauHoiDa.objects.filter(mon_id=Mon.objects.get(id=id_mon))
        except:
            return JsonResponse(json.loads(json.dumps({"data": []})))
        else:
            for ques in list(chain(list_ques, list_ques_da)):
                dang_cau_hoi = '<p id="dang_cau_hoi_{}">{}</p>'.format(ques.id, ques.dang_cau_hoi)
                try:
                    so_cau_hoi = '<p id="so_cau_hoi_{}">{}<p>'.format(ques.id, str(ques.so_cau_hoi))
                except:
                    chu_de = '<p id="chu_de_{0}" data-don="don">{1}</p>'.format(ques.id, ques.chu_de)
                    so_cau_hoi = '<p id="so_cau_hoi_{}">1<p>'.format(ques.id)
                else:
                    chu_de = '<p id="chu_de_{0}" data-don="da">{1}</p>'.format(ques.id, ques.chu_de)
                loai_cau_hoi = '<p>{}</p>'.format(ques.dung_lam)
                do_kho = '<p id="do_kho_{}">'.format(ques.id)
                if ques.do_kho == 0:
                    do_kho += 'Dễ</p>'
                elif ques.do_kho == 1:
                    do_kho += 'Trung bình</p>'
                else:
                    do_kho += 'Khó</p>'
                ngay_tao = '<p>{}</p>'.format(str(ques.ngay_tao))
                noi_dung = '''
                <div id="tom_tat_{0}" class="row">{1}</div>
                '''.format(ques.id, ques.noi_dung[:40])
                if all == 0:
                    data.append([chu_de, loai_cau_hoi, dang_cau_hoi, so_cau_hoi, do_kho, ngay_tao, noi_dung])
                else:
                    ten = '<p>{}</p>'.format(ques.myuser_id.fullname)
                    data.append([ques.id, chu_de, dang_cau_hoi, so_cau_hoi, do_kho, ten, ngay_tao, noi_dung])
            json_data = json.loads(json.dumps({"data": data}))
            return JsonResponse(json_data)


def question_data_detail(request, id, bien):
    user = request.user
    if user.is_authenticated and user.position == 1:
        kieu, don = bien.split('_')
        content = ''
        media = ''
        dat = ''
        if kieu == 'edit':
            if don == 'don':
                ques = CauHoi.objects.get(id=id)
                content += '<input hidden name="so_cau_hoi" value="1">'
                if "Trắc nhiệm" in ques.dang_cau_hoi:
                    for i, da in enumerate(DapAn.objects.filter(cau_hoi_id=ques)):
                        if da.dap_an_dung:
                            dung = 'checked'
                        else:
                            dung = ''
                        dat += '''
                        <div class="row">
                            <div class="col-md-1 col-sm-12 col-xs-12 form-group">
                              <input type="checkbox" class="form-control dap_an" style="transform:scale(0.6);" name="dap_an" {0}>
                            </div>
                            <div class="col-md-11 col-sm-12 col-xs-12 form-group">
                              <div id="dap_an_{1}_modal" class="answer-container nd_dap_an editor_da">{2}</div>
                            </div>
                        </div>
                        '''.format(dung, i, da.noi_dung)
                elif "Điền từ" in ques.dang_cau_hoi:
                    for i, da in enumerate(DapAn.objects.filter(cau_hoi_id=ques)):
                        dat += '''
                        <div class="row">
                            <div class="col-md-12 col-sm-12 col-xs-12 form-group">
                              <div id="dap_an_{0}_modal" class="answer-container nd_dap_an editor_da">{1}</div>
                            </div>
                        </div>
                        '''.format(i, da.noi_dung)
            else:
                ques = CauHoiDa.objects.get(id=id)
                content += '<input hidden name="so_cau_hoi" value="{}">'.format(ques.so_cau_hoi)
                if "Trắc nhiệm" in ques.dang_cau_hoi:
                    for index, ch in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ques)):
                        dat += '''
                        <div class="row">
                            <div class="col-md-12 col-sm-12 col-xs-12 form-group">
                              <div id="cau_hoi_{0}_modal" class="answer-container nd_cau_hoi editor_da">{1}</div>
                            </div>
                        </div>
                        '''.format(index+1, ch.cau_hoi_id.noi_dung)
                        for i, da in enumerate(DapAn.objects.filter(cau_hoi_id=ch.cau_hoi_id)):
                            if da.dap_an_dung:
                                dung = 'checked'
                            else:
                                dung = ''
                            dat += '''
                            <div class="row">
                                <div class="col-md-1 col-sm-12 col-xs-12 form-group">
                                  <input type="checkbox" class="form-control dap_an" style="transform:scale(0.6);" name="dap_an" {0}>
                                </div>
                                <div class="col-md-11 col-sm-12 col-xs-12 form-group">
                                  <div id="dap_an_{3}_{1}_modal" class="answer-container nd_dap_an editor_da">{2}</div>
                                </div>
                            </div>
                            '''.format(dung, i, da.noi_dung, index)
                elif "Tự luận" in ques.dang_cau_hoi:
                    for index, ch in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ques)):
                        dat += '''
                        <div class="row">
                            <div class="col-md-12 col-sm-12 col-xs-12 form-group">
                              <div id="cau_hoi_{0}_modal" class="answer-container nd_cau_hoi editor_da">{1}</div>
                            </div>
                        </div>
                        '''.format(index+1, ch.cau_hoi_id.noi_dung)
            if "Văn bản" in ques.dang_cau_hoi:
                media = '''
                <div id="noi_dung_modal" class="ques-container editor_da">{0}</div>
                <br>
                '''.format(ques.noi_dung)
            elif "Hình ảnh" in ques.dang_cau_hoi:
                media = '''
                    <div class="row">
                        <div class="col-md-8 col-sm-12 col-xs-12 form-group">
                            <img id="hinh_anh_modal" style="max-height:600px;max-width:600px; display: block; margin-left: auto;margin-right: auto;" src="/media/{0}" alt="chọn hình ảnh" />
                            <input type='file' style="display: block; margin-left: auto;margin-right: auto;" accept="image/*" />
                        </div>
                        <div class="col-md-4 col-sm-12 col-xs-12 form-group">
                          <div id="noi_dung_modal" class="ques-container editor_da">{1}</div>
                        </div>
                    </div>
                <br>
                '''.format(ques.dinh_kem, ques.noi_dung)
            elif "Âm thanh" in ques.dang_cau_hoi:
                media = '''
                    <div class="row">
                        <div class="col-md-4 col-sm-12 col-xs-12 form-group">
                          <audio id="media" controls width="100%" src="/media/{0}"></audio>
                          <input type="file" style="display: block; margin-left: auto;margin-right: auto;"  accept="audio/*">
                        </div>
                        <div class="col-md-8 col-sm-12 col-xs-12 form-group">
                          <div id="noi_dung_modal" class="ques-container editor_da">{1}</div>
                        </div>
                    </div>
                <br>
                '''.format(ques.dinh_kem, ques.noi_dung)
            elif "Video" in ques.dang_cau_hoi:
                media = '''
                    <div class="row">
                        <div class="col-md-8 col-sm-12 col-xs-12 form-group">
                          <video id="media" controls width="100%" src="/media/{0}"></video>
                          <input type="file" style="display: block; margin-left: auto;margin-right: auto;" accept="video/*">
                        </div>
                        <div class="col-md-4 col-sm-12 col-xs-12 form-group">
                          <div id="noi_dung_modal" class="ques-container editor_da">{1}</div>
                        </div>
                    </div>
                <br>
                '''.format(ques.dinh_kem, ques.noi_dung)
            else:
                media = '''
                    <div class="row">
                        <div class="col-md-4 col-sm-12 col-xs-12 form-group">
                          <a href="/media/{0}" download>{0}</a><br><br>
                          <input type="file" style="display: block; margin-left: auto;margin-right: auto;">
                        </div>
                        <div class="col-md-8 col-sm-12 col-xs-12 form-group">
                          <div id="noi_dung_modal" class="ques-container editor_da">{1}</div>
                        </div>
                    </div>
                <br>
                '''.format(ques.dinh_kem, ques.noi_dung)
            content += '''
            <input hidden name="id" value="{2}">
            <input hidden name="dang_cau_hoi" value="{3}">
            {1}{0}'''.format(dat, media, ques.id, ques.dang_cau_hoi)
        elif kieu == 'read':
            dat = ''
            content += '<input hidden name="don" value="{}">'.format(don)
            if don == 'don':
                ques = CauHoi.objects.get(id=id)
                content += '<input hidden name="so_cau_hoi" value="1">'
                if "Trắc nhiệm" in ques.dang_cau_hoi:
                    for i, da in enumerate(DapAn.objects.filter(cau_hoi_id=ques)):
                        s = chr(ord(str(i)) + 17)
                        if da.dap_an_dung:
                            dung = '(Đúng)'
                        else:
                            dung = ''
                        result = re.search('<p>(.*)</p>', da.noi_dung)
                        dat += '''
                        <p>{0}: {2} {1}</p>
                        '''.format(s, dung, result.group(1))
                elif "Điền từ" in ques.dang_cau_hoi:
                    for i, da in enumerate(DapAn.objects.filter(cau_hoi_id=ques)):
                        result = re.search('<p>(.*)</p>', da.noi_dung)
                        dat += '''
                        <p>({0}): {1}</p>
                        '''.format(i + 1, result.group(1))
            else:
                ques = CauHoiDa.objects.get(id=id)
                content += '<input hidden name="so_cau_hoi" value="{}">'.format(ques.so_cau_hoi)
                if "Trắc nhiệm" in ques.dang_cau_hoi:
                    for index, ch in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ques)):
                        result = re.search('<p>(.*)</p>', ch.cau_hoi_id.noi_dung)
                        dat += '''
                        <p>{0}) {1}</p>
                        '''.format(index+1, result.group(1))
                        for i, da in enumerate(DapAn.objects.filter(cau_hoi_id=ch.cau_hoi_id)):
                            s = chr(ord(str(i)) + 17)
                            if da.dap_an_dung:
                                dung = '(Đúng)'
                            else:
                                dung = ''
                            result = re.search('<p>(.*)</p>', da.noi_dung)
                            dat += '''
                            <p>{0}: {2} {1}</p>
                            '''.format(s, dung, result.group(1))
                elif "Tự luận" in ques.dang_cau_hoi:
                    for index, ch in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ques)):
                        result = re.search('<p>(.*)</p>', ch.cau_hoi_id.noi_dung)
                        dat += '''
                        <p>{0}) {1}</p>
                        '''.format(index+1, result.group(1))
            if "Hình ảnh" in ques.dang_cau_hoi:
                media = '''
                <img id="hinh_anh_modal" style="max-height:600px;max-width:600px; display: block; margin-left: auto;margin-right: auto;" src="/media/{0}" alt="chọn hình ảnh" /><br>
                '''.format(ques.dinh_kem)
            elif "Âm thanh" in ques.dang_cau_hoi:
                media = '''
                <audio id="media" controls width="100%" src="/media/{0}"></audio>
                '''.format(ques.dinh_kem)
            elif "Video" in ques.dang_cau_hoi:
                media = '''
                <video id="media" controls width="100%" src="/media/{0}"></video>
                '''.format(ques.dinh_kem, ques.noi_dung)
            else:
                media = '''
                <a id="media" href="/media/{0}">File: {0}</video>
                '''.format(ques.dinh_kem, ques.noi_dung)
            content += '''
            <input hidden name="id" value="{2}">
            <input hidden name="dang_cau_hoi" value="{4}">{0}
            <ul class="list-unstyled msg_list">
            <li><a>{3}{1}</a></li>
            '''.format(media, dat, ques.id, ques.noi_dung, ques.dang_cau_hoi)
        return HttpResponse(content)


def question_data_detail_review(request, ds_ch):
    user = request.user
    if user.is_authenticated and user.position == 1:
        content = ''
        for i, temp in enumerate(json.loads(ds_ch)):
            id, don = temp.split('_')
            dap_an = ''
            if don == 'da':
                ques = CauHoiDa.objects.get(id=int(id))
                for index, cht in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ques)):
                    result = re.search('<p>(.*)</p>', cht.cau_hoi_id.noi_dung)
                    dap_an += '''<p>{2}.{0}: {1}</p>'''.format(index + 1, result.group(1), i + 1)
                    if "Trắc nhiệm" in ques.dang_cau_hoi:
                        for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=cht.cau_hoi_id)):
                            s = chr(ord(str(k)) + 17)
                            if da.dap_an_dung:
                                dung = '(Đúng)'
                            else:
                                dung = ''
                            result = re.search('<p>(.*)</p>', da.noi_dung)
                            dap_an += '''<p>{0}: {2} {1}</p>'''.format(s, dung, result.group(1))
            else:
                ques = CauHoi.objects.get(id=int(id))
                if "Trắc nhiệm" in ques.dang_cau_hoi:
                    for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=ques)):
                        s = chr(ord(str(k)) + 17)
                        if da.dap_an_dung:
                            dung = '(Đúng)'
                        else:
                            dung = ''
                        result = re.search('<p>(.*)</p>', da.noi_dung)
                        dap_an += '''<p>{0}: {2} {1}</p>'''.format(s, dung, result.group(1))
                elif "Điền từ" in ques.dang_cau_hoi:
                    for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=ques)):
                        result = re.search('<p>(.*)</p>', da.noi_dung)
                        dap_an += '''<p>({0}): {1}</p>'''.format(k + 1, result.group(1))
            media = ''
            if "Hình ảnh" in ques.dang_cau_hoi:
                media = '<img style="max-height:600px;max-width:600px; display: block; margin-left: auto;margin-right: auto;" src="/media/{}" alt="không tồn tại" />'.format(
                    ques.dinh_kem)
            elif "Âm thanh" in ques.dang_cau_hoi:
                media = '<br><audio controls width="100%" src="/media/{}"></audio>'.format(ques.dinh_kem)
            elif "Video" in ques.dang_cau_hoi:
                media = '<video controls width="100%" src="/media/{}"></video>'.format(ques.dinh_kem)
            else:
                media = '''
                <a id="media" href="/media/{0}">File: {0}</video>
                '''.format(ques.dinh_kem, ques.noi_dung)
            content += '''
            <label>Câu hỏi {0}:</label>
            {3}
            <ul class="list-unstyled msg_list">
            <li><a>{1}{2}</a></li>
            '''.format(i + 1, ques.noi_dung, dap_an, media)
        return HttpResponse(content)


def user_login(request):
    user = request.user
    if user.is_authenticated:
        if user.position == 0:
            return redirect("/student")
        elif user.position == 1:
            return redirect("/teacher")
        else:
            return redirect("/adminsc")
    else:
        if request.method == 'POST':
            # post form để User yêu cầu reset mật khẩu, gửi link về mail
            if 'uemail' in request.POST:
                form = UserResetForm(request.POST)
                if form.is_valid():
                    to_email = form.cleaned_data['uemail']
                    current_site = get_current_site(request)
                    user = get_email(to_email)
                    mail_subject = 'Reset password your account.'
                    message = render_to_string('teacher/resetpwd.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.id)).decode(),
                        'token':account_activation_token.make_token(user),
                    })
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    thread = EmailThread(email)
                    thread.start()
                    return render(request, 'teacher/login.html', {'mess': 'Please check email to reset your password!'})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'teacher/login.html', {'error': error})
            elif 'username' and 'password' in request.POST:
                username = request.POST['username']
                password = request.POST['password']
                user = authenticate(username=username, password=password)
                if user:
                    if user.is_active:
                        login(request, user)
                        if user.position == 0:
                            return HttpResponseRedirect('/student')
                        elif user.position == 1:
                            return HttpResponseRedirect('/teacher')
                        else:
                            return redirect('/adminsc/')
                    else:
                        return render(request, 'teacher/login.html', {'error': 'Your account is blocked!'})
                else:
                    return render(request, 'teacher/login.html', {'error': 'Invalid username or password '})
            elif 'firstname' and 'email' and 'password2' in request.POST:
                user_form = UserForm(request.POST)
                if user_form.is_valid():
                    user = user_form.save()
                    return redirect('/')
                else:
                    error = ''
                    for field in user_form:
                        error += field.errors
                    return render(request, 'teacher/login.html',{'error':error})
        return render(request, 'teacher/login.html')


def resetpwd(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = ResetForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data)
                user.save()
                return redirect('/')
            else:
                return redirect('/')
        return render(request, 'teacher/formresetpass.html', {})
    else:
        return HttpResponse('Link is invalid!')


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def user_profile(request):
    user = request.user
    if user.is_authenticated and user.position == 1:
        if request.method == 'POST':
            if 'fullname' in request.POST:
                if check_password(request.POST['password'], user.password):
                    user.fullname = request.POST['fullname']
                    user.email = request.POST['email']
                    if 'nu' in request.POST:
                        user.gioi_tinh = 0
                    else:
                        user.gioi_tinh = 1
                    user.save()
                    messages.success(request, "Cập nhật thành công")
                else:
                    messages.warning(request, 'Mật khẩu không đúng')
            else:
                if check_password(request.POST['pass1'], user.password):
                    user.set_password(request.POST['pass2'])
                    user.save()
                    messages.success(request, "Cập nhật thành công")
                else:
                    messages.warning(request, 'Mật khẩu không đúng')
            return HttpResponseRedirect("/profile")
        content = {'username': mark_safe(json.dumps(user.username)),
                   'list_lop': ChiTietLop.objects.filter(myuser_id=user)}
        return render(request, 'teacher/profile.html', content)
    else:
        return HttpResponseRedirect('/')


def share(request, lop):
    user = request.user
    temp = giaiMa(lop)
    lop, khoa, nien_khoa, gvid = temp.split("_")
    if user.is_authenticated:
        ls_chi_tiet = ChiTietLop.objects.filter(lop_id=Lop.objects.get(ten=lop)).values('myuser_id')
        ls_student = MyUser.objects.filter(id__in=ls_chi_tiet, position=0)
        content = {'username': mark_safe(json.dumps(user.username)), 'ls_student': ls_student, 'lopht': lop,
                   'list_lop': ChiTietLop.objects.filter(myuser_id=user), 'gvht': MyUser.objects.get(id=gvid),
                   'fullname': mark_safe(json.dumps(user.fullname))}
        if user.position == 0:
            return render(request, 'student/share.html', content)
        else:
            return render(request, 'teacher/share.html', content)
    else:
        return HttpResponseRedirect('/')


def call11(request):
    user = request.user
    if user.is_authenticated and user.position == 1:
        return render(request, 'videocall/home.html')
    else:
        return HttpResponseRedirect('/')


def handle_uploaded_file(f):
    name = f.name
    if " " in name:
        name = name.replace(" ", "_")
    path = "{0}/question_upload/{1}".format(settings.STATIC_ROOT, name)
    file = open(path, 'wb+')
    for chunk in f.chunks():
        file.write(chunk)
    file.close()   


def randomCauHoi(my_list, number, de, diem):
    if number <= 0:
        return False
    else:
        list_sel = []
        while len(list_sel) < number:
            temp = random.choice(my_list)
            if temp not in list_sel:
                list_sel.append(temp)
                ChiTietDe.objects.create(cau_hoi_id=temp, de_id=de, diem=diem)


def maHoa(string):
    temp = base64.b64encode(str(string).encode('utf-8', errors='strict'))
    return temp.decode('utf-8', errors='strict')


def giaiMa(string):
    temp = base64.b64decode(str(string).encode('utf-8', errors='strict'))
    return temp.decode('utf-8', errors='strict')


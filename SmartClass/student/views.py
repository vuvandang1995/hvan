from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth import login
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.utils import timezone
import uuid
import random

from django.utils.safestring import mark_safe
import json
from django.contrib.auth.models import User
import threading
from teacher.forms import UserForm, authenticate, UserResetForm, get_email, ResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from teacher.models import *

from django.contrib import messages
import re
import base64


class EmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.email = email

    def run(self):
        self.email.send()


def home(request):
    user = request.user
    if user.is_authenticated and user.position == 0:
        content = {'mon': lop_mon(user), 'username': mark_safe(json.dumps(user.username)), 'noti_noti': mark_safe(json.dumps(user.noti_noti))}
        return render(request, 'student/base.html', content)
    else:
        return HttpResponseRedirect('/')


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def user_profile(request):
    user = request.user
    if user.is_authenticated and user.position == 0:
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
            return HttpResponseRedirect("profile")
        content = {'mon': lop_mon(user), 'lop': ChiTietLop.objects.get(myuser_id=user),
                   'username': mark_safe(json.dumps(user.username)), 'noti_noti': mark_safe(json.dumps(user.noti_noti))}
        return render(request, 'student/profile.html', content)
    else:
        return redirect("/")

    
def score(request):
    user = request.user
    if user.is_authenticated and user.position == 0:
        lopOb = ChiTietLop.objects.get(myuser_id=user)
        content = {'lop': mark_safe(json.dumps(lopOb.lop_id.ten)),
                   'mon': lop_mon(user),
                   'username': mark_safe(json.dumps(user.username)), 'noti_noti': mark_safe(json.dumps(user.noti_noti))}
        return render(request, 'student/score.html', content)
    else:
        return redirect("/")


def mon(request, id):
    user = request.user
    if user.is_authenticated and user.position == 0:
        lopOb = ChiTietLop.objects.get(myuser_id=user)
        monOb = Mon.objects.get(id=id)
        ls_chi_tiet = ChiTietLop.objects.filter(lop_id=lopOb.lop_id).values('myuser_id')
        ls_student = MyUser.objects.filter(id__in=ls_chi_tiet, position=0)
        ls_teacher = MyUser.objects.filter(id__in=ls_chi_tiet, position=1)
        teacher_ht = GiaoVienMon.objects.get(myuser_id__in=ls_teacher, mon_id=monOb)
        content = {'lop': mark_safe(json.dumps(lopOb.lop_id.ten)), 'mon': lop_mon(user), 'mon_ht': monOb,
                   'lop_ht': lopOb.lop_id, 'ls_student': ls_student, 'teacher_ht': teacher_ht,
                   'username': mark_safe(json.dumps(user.username)), 'noti_noti': mark_safe(json.dumps(user.noti_noti))}
        if request.method == 'POST':
            if 'noti_noti' in request.POST:
                user.noti_noti = 0
                user.save()
        return render(request, 'student/subjects.html', content)
    else:
        return redirect("/")


def group_data(request, teacher):
    user = request.user
    if user.is_authenticated and user.position == 0:
        html = ''
        try:
            lopOb = ChiTietLop.objects.get(myuser_id=user)
            ls_nhom = ChiTietNhom.objects.filter(myuser_id=user).values('nhom_id')
            nhom = Nhom.objects.filter(myuser_id=MyUser.objects.get(username=teacher), id__in=ls_nhom)
            html += '''
                <div class="mail_list" id="group_class">
                <p hidden>'''+lopOb.lop_id.ten+'gr_'+teacher+'gr_'+nhom[0].ten_nhom+'''</p>
                <p hidden>'''+nhom[0].ten_nhom+'''</p>
                <div class="right">
                    <h3>'''+nhom[0].ten_nhom+'''</h3>
            '''
            for std in ChiTietNhom.objects.filter(nhom_id=nhom[0]):
                html += '''<p name='''+std.myuser_id.username+'''><i class="fa fa-user"></i> '''+std.myuser_id.fullname+'''</p>'''
            html += '''</div></div>'''
        except:
            pass
        return HttpResponse(html)


def score_data(request):
    user = request.user
    if user.is_authenticated and user.position == 0:
        data = []
        for mon in Mon.objects.all():
            print(mon)
            list_score = DiemSo.objects.filter(myuser_id=user, mon_id=mon)
            print(list_score)
            if len(list_score) == 0:
                continue
            mon_data = ' <h5>{} - {}</h5>'.format(mon.ten, mon.lop)
            diem_thi = '<h4>'
            for diem in list_score:
                if not diem.da_cham_diem:
                    continue
                tong_diem = diem.diem_auto + diem.diem_cham_tay
                if tong_diem < 5.0:
                    loai = "danger"
                elif tong_diem >= 5.0 and tong_diem < 6.5:
                    loai = "warning"
                elif tong_diem >= 6.5 and tong_diem < 8.0:
                    loai = "info"
                else:
                    loai = "success"
                temp = '''
                <span class="label label-{2}" data-id="{0}" data-toggle="modal" data-target="#point" >{1}</span>
                '''.format(diem.id, round(tong_diem,2), loai)
                diem_thi += temp
            diem_thi += '</h4>'
            data.append([mon_data, diem_thi])
        big_data = {"data": data}
        json_data = json.loads(json.dumps(big_data))
        return JsonResponse(json_data)


def score_data_detail(request, id):
    user = request.user
    if user.is_authenticated and user.position == 0:
        diem = DiemSo.objects.get(id=id)
        content = '''
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
        '''.format(user.fullname, '{0} - {1}'.format(diem.mon_id.ten, diem.mon_id.lop), str(diem.ngay_lam),
                   diem.loai_diem, diem.bai_lam, diem.diem_auto + diem.diem_cham_tay)
        return HttpResponse(content)


def user_mon(request):
    user = request.user
    if user.is_authenticated and user.position == 0:
        content = {'mon': lop_mon(user), 'lop': ChiTietLop.objects.get(myuser_id=user)}

        return render(request, 'student/mon.html', content)
    else:
        return redirect("/")


def lop_mon(user):
    lop = ChiTietLop.objects.get(myuser_id=user)
    try:
        ten_lop = int(lop.lop_id.ten[:2])
    except:
        ten_lop = lop.lop_id.ten[0]
    all_mon = Mon.objects.filter(lop=ten_lop)
    giao_vien = ChiTietLop.objects.filter(lop_id=lop.lop_id,
                                          myuser_id__in=MyUser.objects.filter(position=1)).values("myuser_id")
    return GiaoVienMon.objects.filter(myuser_id__in=giao_vien, mon_id__in=all_mon)


def exam(request, data):
    user = request.user
    if user.is_authenticated and user.position == 0:
        de_id, thoi_gian = giaiMa(data).split("_")
        de = De.objects.get(id=de_id)
        try:
            DiemSo.objects.get(de_id=de, myuser_id=user, ngay_lam=timezone.now().date())
        except:
            if request.method == "POST":
                # de = De.objects.get(id=request.POST['de_id'])
                ds_dap_an = json.loads(request.POST['ds_dap_an'])
                diem = 0
                bai_lam = ''
                da_cham_diem = True
                for i, ctd in enumerate(ChiTietDe.objects.filter(de_id=de)):
                    media = ''
                    dap_an = ''
                    if ctd.cau_hoi_id is not None:
                        if "Hình ảnh" in ctd.cau_hoi_id.dang_cau_hoi:
                            media = '<img style="max-height:600px;max-width:600px; display: block; margin-left: auto;margin-right: auto;" src="/static/{}" alt="không tồn tại" /><br>'.format(
                                ctd.cau_hoi_id.dinh_kem)
                        elif "Âm thanh" in ctd.cau_hoi_id.dang_cau_hoi:
                            media = '<br><audio controls width="100%" src="/static/{}"></audio>'.format(
                                ctd.cau_hoi_id.dinh_kem)
                        elif "Video" in ctd.cau_hoi_id.dang_cau_hoi:
                            media = '<video controls width="100%" src="/static/{}"></video>'.format(
                                ctd.cau_hoi_id.dinh_kem)
                        if "Trắc nhiệm" in ctd.cau_hoi_id.dang_cau_hoi:
                            da_dung = []
                            da_chon = []
                            for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=ctd.cau_hoi_id)):
                                check = ''
                                color = ''
                                if ds_dap_an["0_{}_{}".format(ctd.cau_hoi_id.id, da.id)]:
                                    check = 'checked'
                                if da.dap_an_dung:
                                    color = 'class="plus"'
                                s = chr(ord(str(k)) + 17)
                                dap_an += '''
                                <div class="row div_tn">
                                    <input type="checkbox" style="transform:scale(1.3);" {2} disabled>
                                    <p {3} >{0}</p><p>:</p>
                                    {1}
                                </div>'''.format(s, da.noi_dung, check, color)
                                da_chon.append(ds_dap_an["0_{}_{}".format(ctd.cau_hoi_id.id, da.id)])
                                da_dung.append(da.dap_an_dung)
                            plus = '<input type="number" value="0" readonly>'
                            if da_chon == da_dung:
                                diem += ctd.diem
                                plus = '<input type="number" value="{}" readonly>'.format(ctd.diem)
                            bai_lam += '''
                            <div id="cau_{0}">
                                <h4 class="head_ch"><p>Câu hỏi {0} ({4} điểm):</p> {5}</h4>
                                <div class="row">{3}</div>
                                <div class="row div_ch">{1}</div>
                                {2}
                            </div>
                            '''.format(i + 1, ctd.cau_hoi_id.noi_dung, dap_an, media, ctd.diem, plus)
                        elif "Điền từ" in ctd.cau_hoi_id.dang_cau_hoi:
                            ds_da = DapAn.objects.filter(cau_hoi_id=ctd.cau_hoi_id)
                            plus_score = 0
                            for k, da in enumerate(ds_da):
                                temp = re.search('<p>(.*)</p', da.noi_dung)
                                dap_an += '''
                                <div class="row div_dt">
                                    <p>({0}):</p> 
                                    <input type="text" value="{1}" disabled>
                                    <p class="plus">{2}</p>
                                </div>'''.format(k + 1, ds_dap_an["0_{}_{}".format(ctd.cau_hoi_id.id, da.id)],
                                                 temp.group(1))
                                if da.noi_dung.replace(" ", '').lower() == '<p>{}</p>'.format(
                                        ds_dap_an["0_{}_{}".format(ctd.cau_hoi_id.id, da.id)].replace(" ", '').lower()):
                                    diem += ctd.diem / len(ds_da)
                                    plus_score += ctd.diem / len(ds_da)
                            plus = '<input type="number" value="{}" readonly>'.format(plus_score)
                            bai_lam += '''
                                <div id="cau_{0}">
                                    <h4 class="head_ch"><p>Câu hỏi {0} ({4} điểm):</p> {5}</h4>
                                    <div class="row">{2}</div>
                                    <div class="row div_ch">{1}</div>
                                    {3}
                                </div>
                            '''.format(i + 1, ctd.cau_hoi_id.noi_dung, media, dap_an, ctd.diem, plus)
                        elif "Tự luận" in ctd.cau_hoi_id.dang_cau_hoi:
                            da_cham_diem = False
                            bai_lam += '''
                                <div id="cau_{0}">
                                    <h4 class="head_ch"><p>Câu hỏi {0} ({3} điểm):</p><input type="number" min='0' max='{3}' step='0.01' data-start_d="0_{5}" data-value_d="0" data-end_d="0_{5}" readonly class="diem_tu_luan" data-id="0_{5}"></h4>
                                    <div class="row">{2}</div>
                                    <div class="row div_ch">{1}</div>
                                    <div class="row div_tl">
                                        <textarea class="form-control dap_an" readonly>{4}</textarea>
                                    </div>
                                    <div class="row div_dt">
                                        <p><font class="plus">*Nhận xét của giáo viên*</font></p>
                                    </div>
                                    <div class="row div_tl">
                                        <textarea class="form-control nhan_xet" rows="5" style="color:red" readonly data-id="0_{5}" data-start_nx="0_{5}" data-value_nx="0" data-end_nx="0_{5}"></textarea>
                                    </div>
                                </div>
                            '''.format(i + 1, ctd.cau_hoi_id.noi_dung, media, ctd.diem,
                                       ds_dap_an["0_{}_undefined".format(ctd.cau_hoi_id.id)], ctd.cau_hoi_id.id)
                    else:
                        if "Hình ảnh" in ctd.cau_hoi_da_id.dang_cau_hoi:
                            media = '<img style="max-height:600px;max-width:600px; display: block; margin-left: auto;margin-right: auto;" src="/static/{}" alt="không tồn tại" /><br>'.format(
                                ctd.cau_hoi_da_id.dinh_kem)
                        elif "Âm thanh" in ctd.cau_hoi_da_id.dang_cau_hoi:
                            media = '<br><audio controls width="100%" src="/static/{}"></audio>'.format(
                                ctd.cau_hoi_da_id.dinh_kem)
                        elif "Video" in ctd.cau_hoi_da_id.dang_cau_hoi:
                            media = '<video controls width="100%" src="/static/{}"></video>'.format(
                                ctd.cau_hoi_da_id.dinh_kem)
                        if "Trắc nhiệm" in ctd.cau_hoi_da_id.dang_cau_hoi:
                            plus_score = 0
                            for index, ch in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ctd.cau_hoi_da_id)):
                                da_dung = []
                                da_chon = []
                                dap_an += '''
                                <div class="row div_sub">{0}.{1} ({3} điểm): {2}</div>
                                '''.format(i + 1, index + 1, ch.cau_hoi_id.noi_dung,
                                           round(ctd.diem / ctd.cau_hoi_da_id.so_cau_hoi, 2))
                                for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=ch.cau_hoi_id)):
                                    check = ''
                                    color = ''
                                    if ds_dap_an["{}_{}_{}".format(ctd.cau_hoi_da_id.id, ch.cau_hoi_id.id, da.id)]:
                                        check = 'checked'
                                    if da.dap_an_dung:
                                        color = 'class="plus"'
                                    s = chr(ord(str(k)) + 17)
                                    dap_an += '''
                                    <div class="row div_tn">
                                        <input type="checkbox" style="transform:scale(1.3);" {2} disabled>
                                        <p {3} >{0}</p><p>:</p>
                                        {1}
                                    </div>'''.format(s, da.noi_dung, check, color)
                                    da_dung.append(da.dap_an_dung)
                                    da_chon.append(
                                        ds_dap_an["{}_{}_{}".format(ctd.cau_hoi_da_id.id, ch.cau_hoi_id.id, da.id)])
                                if da_chon == da_dung:
                                    diem += ctd.diem / ctd.cau_hoi_da_id.so_cau_hoi
                                    plus_score += ctd.diem / ctd.cau_hoi_da_id.so_cau_hoi
                            plus = '<input type="number" value="{}" readonly>'.format(plus_score)
                            bai_lam += '''
                            <div id="cau_{0}">
                                <h4 class="head_ch"><p>Câu hỏi {0} ({4} điểm):</p> {5}</h4>
                                <div class="row">{3}</div>
                                <div class="row div_ch">{1}</div>
                                {2}
                            </div>
                            '''.format(i + 1, ctd.cau_hoi_da_id.noi_dung, dap_an, media, ctd.diem, plus)
                        elif "Tự luận" in ctd.cau_hoi_da_id.dang_cau_hoi:
                            da_cham_diem = False
                            for index, ch in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ctd.cau_hoi_da_id)):
                                dap_an += '''
                                <div class="row div_sub">{0}.{1} ({2} điểm): {3}</div>
                                <div class="row div_tl">
                                    <textarea class="form-control dap_an" readonly>{4}</textarea>
                                </div>
                                '''.format(i + 1, index + 1, round(ctd.diem / ctd.cau_hoi_da_id.so_cau_hoi, 2),
                                           ch.cau_hoi_id.noi_dung,
                                           ds_dap_an["{}_{}_undefined".format(ctd.cau_hoi_da_id.id, ch.cau_hoi_id.id)])
                            bai_lam += '''
                            <div id="cau_{0}">
                                <h4 class="head_ch"><p>Câu hỏi {0} ({1} điểm):</p><input type="number" min='0' max='{1}' step='0.01' data-start_d="{2}_{3}" data-value_d="0" data-end_d="{2}_{3}" readonly class="diem_tu_luan" data-id="{2}_{3}"></h4>
                                <div class="row">{4}</div>
                                <div class="row div_ch">{5}</div>
                                {6}
                                <div class="row div_dt">
                                    <p><font class="plus">*Nhận xét của giáo viên*</font></p>
                                </div>
                                <div class="row div_tl">
                                    <textarea class="form-control nhan_xet" rows="5" style="color:red" readonly data-id="{2}_{3}" data-start_nx="{2}_{3}" data-value_nx="0" data-end_nx="{2}_{3}"></textarea>
                                </div>
                            </div>
                            '''.format(i + 1, ctd.diem, ctd.cau_hoi_da_id.id, ch.cau_hoi_id.id, media,
                                       ctd.cau_hoi_da_id.noi_dung, dap_an)
                DiemSo.objects.create(de_id=de, myuser_id=user, mon_id=de.mon_id, da_cham_diem=da_cham_diem,
                                      loai_diem="{} - {} phút".format(de.dung_lam, de.thoi_gian),
                                      bai_lam=bai_lam, diem_auto=round(diem, 2))
                time_remain = 0
            else:
                time_exam = timezone.datetime.strptime(thoi_gian, '%H:%M:%S').time()
                now = timezone.now().time()
                time_remain = timezone.timedelta(hours=time_exam.hour, minutes=time_exam.minute, seconds=time_exam.second) + timezone.timedelta(minutes=de.thoi_gian) - timezone.timedelta(hours=7) - timezone.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
                if time_remain < timezone.timedelta(0):
                    time_remain = 0
                else:
                    time_remain = int(time_remain.seconds)
        else:
            time_remain = -1
        content = {'time_remain': mark_safe(json.dumps(maHoa(time_remain))), 'de_id': mark_safe(json.dumps(maHoa(de_id))),
                   'username': mark_safe(json.dumps(user.username)), 'noti_noti': mark_safe(json.dumps(user.noti_noti))}
        return render(request, 'student/exam.html', content)
    else:
        return redirect("/")


def exam_data(request, id):
    user = request.user
    if user.is_authenticated and user.position == 0:
        left_content = ''
        right_content = ''
        de_id = De.objects.get(id=id)
        ctd = ChiTietDe.objects.filter(de_id=de_id)
        nd_de = []
        while len(nd_de) < len(ctd):
            temp = random.choice(ctd)
            if temp not in nd_de:
                nd_de.append(temp)
        for i, ques in enumerate(nd_de):
            dap_an = ''
            left_content += '''
            <div class="mail_list">
                <a href="#cau_{0}" id="stt_{0}">
                  Câu {0} <span class="label label-danger"><i class="fa fa-close"></i></span>
                </a>
            </div>
            '''.format(i + 1)
            media = ''
            if ques.cau_hoi_id is not None:
                if "Hình ảnh" in ques.cau_hoi_id.dang_cau_hoi:
                    media = '<img style="max-height:600px;max-width:600px; display: block; margin-left: auto;margin-right: auto;" src="/static/{}" alt="không tồn tại" /><br>'.format(
                        ques.cau_hoi_id.dinh_kem)
                elif "Âm thanh" in ques.cau_hoi_id.dang_cau_hoi:
                    media = '<br><audio controls width="100%" src="/static/{}"></audio>'.format(ques.cau_hoi_id.dinh_kem)
                elif "Video" in ques.cau_hoi_id.dang_cau_hoi:
                    media = '<video controls width="100%" src="/static/{}"></video>'.format(ques.cau_hoi_id.dinh_kem)
                if "Trắc nhiệm" in ques.cau_hoi_id.dang_cau_hoi:
                    for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=ques.cau_hoi_id).order_by("?")):
                        s = chr(ord(str(k)) + 17)
                        dap_an += '''
                        <div class="row div_tn">
                            <input type="checkbox" data-id="{0}" data-ch_id="0_{1}" data-da_id="{4}" data-kind="tn" style="transform:scale(1.3);" name="dap_an_0_{1}" class="dap_an">
                            <p>{2}:</p> 
                            {3}
                        </div>'''.format(i+1, ques.cau_hoi_id.id, s, da.noi_dung, da.id)
                    right_content += '''
                    <div id="cau_{0}">
                        <label>Câu hỏi {0} ({4} điểm):</label>
                        <div class="row">{3}</div>
                        <div class="row div_ch">{1}</div>
                        {2}
                    </div>
                    '''.format(i + 1, ques.cau_hoi_id.noi_dung, dap_an, media, ques.diem)
                elif "Điền từ" in ques.cau_hoi_id.dang_cau_hoi:
                    nd_cau_hoi = ques.cau_hoi_id.noi_dung
                    for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=ques.cau_hoi_id)):
                        dap_an += '''
                        <div class="row div_dt">
                            <p>({3}):</p> 
                            <input type="text" data-id="{0}" data-ch_id="0_{1}" data-da_id="{2}" data-kind="dt" name="dap_an_0_{1}" class="dap_an"> 
                        </div>'''.format(i + 1, ques.cau_hoi_id.id, da.id, k+1)
                    right_content += '''
                        <div id="cau_{0}">
                            <label>Câu hỏi {0} ({4} điểm):</label>
                            <div class="row">{2}</div>
                            <div class="row div_ch">{1}</div>
                            {3}
                        </div>
                    '''.format(i + 1, nd_cau_hoi, media, dap_an, ques.diem)
                elif "Tự luận" in ques.cau_hoi_id.dang_cau_hoi:
                    right_content += '''
                        <div id="cau_{0}">
                            <label>Câu hỏi {0} ({3} điểm):</label>
                            <div class="row">{2}</div>
                            <div class="row div_ch">{1}</div>
                            <div class="row div_tl">
                                <textarea class="form-control dap_an" cols="100" rows="10" data-id="{0}" data-ch_id="0_{4}" data-kind="tl" name="dap_an_0_{4}" ></textarea>
                            </div>
                        </div>
                    '''.format(i + 1, ques.cau_hoi_id.noi_dung, media, ques.diem, ques.cau_hoi_id.id)
            else:
                if "Hình ảnh" in ques.cau_hoi_da_id.dang_cau_hoi:
                    media = '<img style="max-height:600px;max-width:600px; display: block; margin-left: auto;margin-right: auto;" src="/static/{}" alt="không tồn tại" /><br>'.format(
                        ques.cau_hoi_da_id.dinh_kem)
                elif "Âm thanh" in ques.cau_hoi_da_id.dang_cau_hoi:
                    media = '<br><audio controls width="100%" src="/static/{}"></audio>'.format(ques.cau_hoi_da_id.dinh_kem)
                elif "Video" in ques.cau_hoi_da_id.dang_cau_hoi:
                    media = '<video controls width="100%" src="/static/{}"></video>'.format(ques.cau_hoi_da_id.dinh_kem)
                if "Trắc nhiệm" in ques.cau_hoi_da_id.dang_cau_hoi:
                    for index, ch in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ques.cau_hoi_da_id)):
                        dap_an += '''
                        <div class="row div_sub">{0}.{1} ({3} điểm): {2}</div>
                        '''.format(i+1, index+1, ch.cau_hoi_id.noi_dung,
                                   round(ques.diem / ques.cau_hoi_da_id.so_cau_hoi, 2))
                        for k, da in enumerate(DapAn.objects.filter(cau_hoi_id=ch.cau_hoi_id).order_by("?")):
                            s = chr(ord(str(k)) + 17)
                            dap_an += '''
                            <div class="row div_tn">
                                <input type="checkbox" data-id="{0}" data-ch_id="{1}_{5}" data-da_id="{4}" data-kind="tn" style="transform:scale(1.3);" name="dap_an_{1}_{5}" class="dap_an">
                                <p>{2}:</p> 
                                {3}
                            </div>'''.format(i+1, ques.cau_hoi_da_id.id, s, da.noi_dung, da.id, ch.cau_hoi_id.id)
                    right_content += '''
                    <div id="cau_{0}">
                        <label>Câu hỏi {0} ({4} điểm):</label>
                        <div class="row">{3}</div>
                        <div class="row div_ch">{1}</div>
                        {2}
                    </div>
                    '''.format(i + 1, ques.cau_hoi_da_id.noi_dung, dap_an, media, ques.diem)
                elif "Tự luận" in ques.cau_hoi_da_id.dang_cau_hoi:
                    for index, ch in enumerate(ChiTietCauHoiDa.objects.filter(cau_hoi_da_id=ques.cau_hoi_da_id)):
                        dap_an += '''
                        <div class="row div_sub">{0}.{1} ({5} điểm): {2}</div>
                        <div class="row div_tl">
                            <textarea class="form-control dap_an" cols="100" rows="10" data-id="{0}" data-ch_id="{3}_{4}" data-kind="tl" name="dap_an_{3}_{4}" ></textarea>
                        </div>
                        '''.format(i+1, index+1, ch.cau_hoi_id.noi_dung, ques.cau_hoi_da_id.id, ch.cau_hoi_id.id,
                                   round(ques.diem / ques.cau_hoi_da_id.so_cau_hoi, 2))
                    right_content += '''
                    <div id="cau_{0}">
                        <label>Câu hỏi {0} ({4} điểm):</label>
                        <div class="row">{3}</div>
                        <div class="row div_ch">{1}</div>
                        {2}
                    </div>
                    '''.format(i + 1, ques.cau_hoi_da_id.noi_dung, dap_an, media, ques.diem)
        lop = ChiTietLop.objects.filter(myuser_id=user)[0]

        content = '''
        <div class="col-sm-1">{0}</div>
        <div class="col-sm-8 baithi" id="bai_lam">
            <input type="hidden" value="{2}" name="de_id">
            <div class="inbox-body">
                <div class="mywrap">{1}</div>
            </div>
        </div>
        <div class="col-sm-3">
            <h3><i class="fa fa-clock-o"></i> <p style="display:inline;" id="tg_lam">{8}:00</p></h3>
            <h5>Thời gian làm bài</h5>
            <table class="mytable" >
                <tr><td>Họ và tên</td><td><b>{3}</b></td></tr>
                <tr><td>Lớp</td><td>{4}</td></tr>
                <tr><td>Khoa</td><td>{5}</td></tr>
                <tr><td>Khóa</td><td>{6} - {7}</td></tr>
            </table>
            <hr>
            <div class="row">
                <div class="col-sm-4"></div>
                <div class="col-sm-4">
                    <button class="btn btn-primary btn-lg" id="submit" onclick="nopBai();">Nộp bài <i class="fa fa-send"></i> </button>
                </div>
                <div class="col-sm-4"></div>
            </div>
            <hr>
            <font color="red">*Chú ý: Điểm lẻ của môn thi tự luận được làm tròn đến 2 chữ số thập phân thay vì lấy đến 
            0,25 điểm như trước; thay đổi hình thức xử lý thí sinh vi phạm quy chế thi,… là những thay đổi nổi bật 
            nhất trong Quy chế thi THPT quốc gia và xét công nhận tốt nghiệp THPT năm 2018 mà Bộ GD&ĐT vừa công bố 
            chính thức.
            </font>
        </div>
        '''.format(left_content, right_content, id, user.fullname, lop.lop_id.ten, lop.lop_id.khoa_id.ten_khoa,
                   lop.lop_id.nien_khoa_id.ten_nien_khoa, lop.lop_id.nien_khoa_id.nam_hoc, de_id.thoi_gian)
        return HttpResponse(content)


def maHoa(string):
    temp = base64.b64encode(str(string).encode('utf-8', errors='strict'))
    return temp.decode('utf-8', errors='strict')


def giaiMa(string):
    temp = base64.b64decode(str(string).encode('utf-8', errors='strict'))
    return temp.decode('utf-8', errors='strict')

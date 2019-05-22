from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from passlib.hash import pbkdf2_sha256, md5_crypt
from forum.models import t_user, t_tipe_kategori, t_kategori, t_user_grup, t_grup, t_user_subscribe, t_topik, t_user_log, t_notifikasi
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from collections import Counter


def get_topik_trending():
    class ComponentTopik():
        topic = None
        id_hash = ""
        tags = []

    trending = []
    for topic in sorted(t_topik.objects.filter(id_grup=None), key=lambda t: t.jumlah_komentar_topik, reverse=True):
        c_topik = ComponentTopik()
        c_topik.topic = topic
        hash_id_topik = md5_crypt.encrypt(str(topic.id_topik))
        c_topik.id_hash = hash_id_topik[:0] + hash_id_topik[3:]
        c_topik.tags = str(topic.tags).split(',')
        trending.append(c_topik)
    return trending


def get_topik_latest():
    class ComponentTopik():
        topic = None
        id_hash = ""
        tags = []

    latest = []
    all_topik = t_topik.objects.filter(id_grup=None)
    all_topik = list(reversed(all_topik))
    for topic in all_topik:
        c_topik = ComponentTopik()
        c_topik.topic = topic
        hash_id_topik = md5_crypt.encrypt(str(topic.id_topik))
        c_topik.id_hash = hash_id_topik[:0] + hash_id_topik[3:]
        c_topik.tags = str(topic.tags).split(',')
        latest.append(c_topik)
    return latest

def topic_recommended(request):
    try:
        email_login = request.session['email_login']
    except:
        return redirect('/forum/user/sign_in')
    #######################################
    # user
    try:
        user_login = t_user.objects.get(pk=email_login)
    except:
        user_login = None

    # KATEGORI
    class ComponentCategory():
        tipe_kategori = None
        kategori = []

    c_category = []
    for tipe_kategori in t_tipe_kategori.objects.all():
        componentCategory = ComponentCategory()
        componentCategory.tipe_kategori = tipe_kategori
        componentCategory.kategori = t_kategori.objects.filter(id_tipe_kategori=tipe_kategori)
        c_category.append(componentCategory)

    # JOINED GRUP
    c_joined_grup = []
    c_my_grup = []
    c_subscription = []
    if (email_login):
        for user_grup in t_user_grup.objects.filter(email=t_user.objects.get(pk=email_login), confirm=True):
            c_joined_grup.append(user_grup.id_grup)

        # MY GROUPS
        c_my_grup = t_grup.objects.filter(moderator=t_user.objects.get(pk=email_login))

        # SUBCRIPTION
        for user_subscribe in t_user_subscribe.objects.filter(
                email_subscriber=t_user.objects.get(pk=email_login)):
            c_subscription.append(user_subscribe.email_subscribed)
            #######################################
    ##Notifikasi
    notif_not_read = []
    notif = []
    if (user_login):
        notif_not_read = t_notifikasi.objects.filter(read=False, email_receiver=t_user.objects.get(pk=email_login))
        all_notif = t_notifikasi.objects.filter(email_receiver=t_user.objects.get(pk=email_login))
        if (notif_not_read):
            notif = notif_not_read
        else:
            if (len(all_notif) > 10):
                for i in range(0, 10):
                    notif.append(all_notif[i])
            else:
                notif = all_notif
        notif = list(reversed(notif))
    content = {
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,
        'c_topic': get_topik_recomended(email_login),
        'notif': notif,
        'notif_not_read': notif_not_read,
    }
    return render(request, 'topic_recommended.html', content)
def get_topik_recomended(email_login):
    class ComponentTopik():
        topic = None
        id_hash = ""
        tags = []
    recommended = []
    all_topik = []
    all_user_log = t_user_log.objects.filter(email=t_user.objects.get(pk=email_login))
    all_tag = []
    all_tag_non_duplicate = []

    if (all_user_log):
        all_tag = []
        class ComponentTag():
            tag = ""
            n = 0
        c_tag = []
        for user_log in all_user_log:
            topic = user_log.id_topik
            all_tag += (str(topic.tags).lower()).split(',')
        all_tag_non_duplicate = list(set(all_tag))
        for tag in all_tag_non_duplicate:
            componentTag = ComponentTag()
            componentTag.tag = tag
            componentTag.n = all_tag.count(tag)
            c_tag.append(componentTag)
        c_tag =  sorted(c_tag, key=lambda t: t.n, reverse=True)
        for c_t in c_tag:
            for topic in t_topik.objects.filter(tags__icontains = c_t.tag, id_grup = None):
                if not topic in all_topik:
                    all_topik.append(topic)

        c_all_topik = []
        user = t_user.objects.get(pk=email_login)
        if (user.jurusan == "Sistem Informasi (S1-SI)"):
            c_all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=2)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=13)) | Q(
                    id_kategori=t_kategori.objects.get(pk=12)))
        elif (user.jurusan == "Teknik Informatika (S1-TI)"):
            c_all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=7)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=12)) | Q(
                    id_kategori=t_kategori.objects.get(pk=13)))
        elif (user.jurusan == "Teknik Elektro (S1-TE)"):
            c_all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=8)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=14)))
        elif (user.jurusan == "Teknik Informatika (D4-TI)"):
            c_all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=7)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=12)) | Q(
                    id_kategori=t_kategori.objects.get(pk=13)))
        elif (user.jurusan == "Teknik Informatika (D3-TI)"):
            c_all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=7)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=12)) | Q(
                    id_kategori=t_kategori.objects.get(pk=13)))
        elif (user.jurusan == "Teknik Komputer (D3-TK)"):
            c_all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=9)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=12)) | Q(
                    id_kategori=t_kategori.objects.get(pk=17)))
        elif (user.jurusan == "Manajemen Rekayasa (S1-MR)"):
            c_all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=10)) | Q(id_kategori=t_kategori.objects.get(pk=5)))
        elif (user.jurusan == "Teknik Bioproses (S1-BP)"):
            c_all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=6)) | Q(id_kategori=t_kategori.objects.get(pk=11)))
        for topic in c_all_topik:
            if not topic in all_topik:
                all_topik.append(topic)
        print(Counter(all_tag))
    else:
        user = t_user.objects.get(pk=email_login)
        if (user.jurusan == "Sistem Informasi (S1-SI)"):
            all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=2)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=13)) | Q(
                    id_kategori=t_kategori.objects.get(pk=12)))
        elif (user.jurusan == "Teknik Informatika (S1-TI)"):
            all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=7)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=12)) | Q(
                    id_kategori=t_kategori.objects.get(pk=13)))
        elif (user.jurusan == "Teknik Elektro (S1-TE)"):
            all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=8)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=14)))
        elif (user.jurusan == "Teknik Informatika (D4-TI)"):
            all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=7)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=12)) | Q(
                    id_kategori=t_kategori.objects.get(pk=13)))
        elif (user.jurusan == "Teknik Informatika (D3-TI)"):
            all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=7)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=12)) | Q(
                    id_kategori=t_kategori.objects.get(pk=13)))
        elif (user.jurusan == "Teknik Komputer (D3-TK)"):
            all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=9)) | Q(id_kategori=t_kategori.objects.get(pk=1)) | Q(
                    id_kategori=t_kategori.objects.get(pk=12)) | Q(
                    id_kategori=t_kategori.objects.get(pk=17)))
        elif (user.jurusan == "Manajemen Rekayasa (S1-MR)"):
            all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=10)) | Q(id_kategori=t_kategori.objects.get(pk=5)))
        elif (user.jurusan == "Teknik Bioproses (S1-BP)"):
            all_topik = t_topik.objects.filter(
                Q(id_kategori=t_kategori.objects.get(pk=6)) | Q(id_kategori=t_kategori.objects.get(pk=11)))
        all_topik = sorted(all_topik, key=lambda t: t.jumlah_komentar_topik, reverse=True)

    ###
    for topic in all_topik:
        c_topik = ComponentTopik()
        c_topik.topic = topic
        hash_id_topik = md5_crypt.encrypt(str(topic.id_topik))
        c_topik.id_hash = hash_id_topik[:0] + hash_id_topik[3:]
        c_topik.tags = str(topic.tags).split(',')
        recommended.append(c_topik)
    return recommended


def index(request):
    try:
        email_login = request.session['email_login']
    except:
        email_login = None
    # user
    try:
        user_login = t_user.objects.get(pk=email_login)
    except:
        user_login = None

    # KATEGORI
    class ComponentCategory():
        tipe_kategori = None
        kategori = []

    c_category = []
    for tipe_kategori in t_tipe_kategori.objects.all():
        componentCategory = ComponentCategory()
        componentCategory.tipe_kategori = tipe_kategori
        componentCategory.kategori = t_kategori.objects.filter(id_tipe_kategori=tipe_kategori)
        c_category.append(componentCategory)

    # JOINED GRUP
    c_joined_grup = []
    c_my_grup = []
    c_subscription = []
    if (email_login):
        for user_grup in t_user_grup.objects.filter(email=t_user.objects.get(pk=email_login), confirm=True):
            c_joined_grup.append(user_grup.id_grup)

        # MY GROUPS
        c_my_grup = t_grup.objects.filter(moderator=t_user.objects.get(pk=email_login))

        # SUBCRIPTION
        for user_subscribe in t_user_subscribe.objects.filter(email_subscriber=t_user.objects.get(pk=email_login)):
            c_subscription.append(user_subscribe.email_subscribed)
    trending_topic = get_topik_trending()
    latest_topic = get_topik_latest()
    recommended_topic = []
    if (user_login):
        recommended_topic = get_topik_recomended(email_login)
    else:
        pass

    ##Notifikasi
    notif_not_read = []
    notif = []
    if (user_login):
        notif_not_read = t_notifikasi.objects.filter(read = False, email_receiver = t_user.objects.get(pk= email_login))
        all_notif = t_notifikasi.objects.filter(email_receiver = t_user.objects.get(pk= email_login))
        if(notif_not_read):
            notif = notif_not_read
        else:
            if(len(all_notif) > 10):
                for i in range(0,10):
                    notif.append(all_notif[i])
            else:
                notif = all_notif
        notif = list(reversed(notif))
    content = {
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,
        'trending_topic': trending_topic,
        'latest_topic': latest_topic,
        'recommended_topic': recommended_topic,
        'notif': notif,
        'notif_not_read': notif_not_read,
    }
    return render(request, 'dashboard.html', content)

def update_notif(request):
    if(request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            email_login = None
        for notif in t_notifikasi.objects.filter(email_receiver = t_user.objects.get(pk = email_login)):
            notif.read = True
            notif.save()
        return HttpResponse("")
def sign_in(request):
    if (request.method == 'POST'):
        all_user = t_user.objects.all()
        email = request.POST['email']
        password = request.POST['password']
        if(email == "admin@admin" and password == "admin123"):
            request.session['admin'] = "admin_forum"
            return redirect("/forum/admin_page")
        m = 'null'
        for users in all_user:
            if ((pbkdf2_sha256.verify(password, users.password)) and (users.email == email)):
                if (users.verified == False):
                    m = 'not verified'
                    break
                else:
                    m = 'verified'
                    break
        if (m == 'null'):
            error_message_sign_in = 'Invalid account'
        elif (m == 'not verified'):
            error_message_sign_in = 'Account not verified, check your email'
        else:
            request.session['email_login'] = email
            request.session.get_expire_at_browser_close()
            return redirect('/forum')
    else:
        try:
            email_login = request.session['email_login']

        except:
            email_login = None

        try:
            admin = request.session['admin']
        except:
            admin = None
        if (email_login):
            return redirect('/forum')
        if(admin):
            return redirect("/forum/admin_page")
        error_message_sign_in = ''
    content = {
        'error_message': error_message_sign_in,
    }
    return render(request, 'sign_in.html', content)


def forgot_password(request):
    if (request.method == 'POST'):
        email = request.POST['email']
        hash_email = md5_crypt.encrypt(email)
        url_email = hash_email[:0] + hash_email[3:]
        all_user = t_user.objects.all()
        m = 'null'
        user = None
        for users in all_user:
            if (users.email == email):
                m = 'not null'
                user = users
                break
        if (m == 'not null'):
            subject = '[Reset your password ]'
            text_content = ''
            html_content = '<h4>Hello ' + user.full_name + ',</h4><br>' \
                                                           '<p>Click the link below to reset your password</p><br>' \
                                                           '<a href="http://localhost:8000/forum/user/change_password/' + url_email + '" style="background-color: #F2711C; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px;" >RESET PASSWORD</a><br><br>' \
                                                                                                                                      '<p><strong>Note : If it does not you who make this request, please ignore this email</strong></p>' \
                                                                                                                                      '<hr>' \
                                                                                                                                      '<p><strong>Thank You</strong></p>' \
                                                                                                                                      '<p><strong>Forum Mahasiswa</strong></p>'
            msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return HttpResponse('not null')
        else:
            return HttpResponse('null')
    else:
        return render(request, '404.html')


def sign_out(request):
    try:
        del request.session['email_login']
    except:
        pass
    try:
        del request.session['admin']
    except:
        pass
    return redirect('/forum')


def search_topic(request):
    try:
        email_login = request.session['email_login']
    except:
        email_login = None
    # user
    try:
        user_login = t_user.objects.get(pk=email_login)
    except:
        user_login = None

    # KATEGORI
    class ComponentCategory():
        tipe_kategori = None
        kategori = []

    c_category = []
    for tipe_kategori in t_tipe_kategori.objects.all():
        componentCategory = ComponentCategory()
        componentCategory.tipe_kategori = tipe_kategori
        componentCategory.kategori = t_kategori.objects.filter(id_tipe_kategori=tipe_kategori)
        c_category.append(componentCategory)

    # JOINED GRUP
    c_joined_grup = []
    c_my_grup = []
    c_subscription = []
    if (email_login):
        for user_grup in t_user_grup.objects.filter(email=t_user.objects.get(pk=email_login), confirm=True):
            c_joined_grup.append(user_grup.id_grup)

        # MY GROUPS
        c_my_grup = t_grup.objects.filter(moderator=t_user.objects.get(pk=email_login))

        # SUBCRIPTION
        for user_subscribe in t_user_subscribe.objects.filter(email_subscriber=t_user.objects.get(pk=email_login)):
            c_subscription.append(user_subscribe.email_subscribed)

    q = request.GET['q']
    all_topic = t_topik.objects.filter((Q(judul_topik__icontains=q) | Q(isi_topik__icontains=q)), id_grup=None)

    class ComponentTopic():
        topic = None
        id_hash = ""
        tags = []

    c_topic = []
    for topic in all_topic:
        ct = ComponentTopic()
        ct.topic = topic
        hash_id_topik = md5_crypt.encrypt(str(topic.id_topik))
        ct.id_hash = hash_id_topik[:0] + hash_id_topik[3:]
        ct.tags = str(topic.tags).split(',')
        c_topic.append(ct)

    ##Notifikasi
    notif_not_read = []
    notif = []
    if (user_login):
        notif_not_read = t_notifikasi.objects.filter(read=False, email_receiver=t_user.objects.get(pk=email_login))
        all_notif = t_notifikasi.objects.filter(email_receiver=t_user.objects.get(pk=email_login))
        if (notif_not_read):
            notif = notif_not_read
        else:
            if (len(all_notif) > 10):
                for i in range(0, 10):
                    notif.append(all_notif[i])
            else:
                notif = all_notif
        notif = list(reversed(notif))
    content = {
        'c_topic': c_topic,
        'q': q,
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,
        'notif': notif,
        'notif_not_read': notif_not_read,
    }
    return render(request, 'search_topic.html', content)


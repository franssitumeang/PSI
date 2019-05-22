from django.shortcuts import redirect, render
from forum.models import t_topik, t_tipe_kategori, t_grup, t_user_grup, t_kategori, t_user, t_komentar, \
    t_user_subscribe, t_notifikasi, t_tipe_notifikasi
import json
from django.core import serializers
from django.http import HttpResponse
from passlib.hash import md5_crypt
from operator import itemgetter


def view(request):
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
    all_user = t_user.objects.filter(verified=True)
    id_user = []

    class ContentUser:
        user = None
        is_subscribe = False
        self = ""

    c_user = []
    for u in all_user:
        id_user.append(u.email)
        content_user = ContentUser()
        content_user.user = u
        if (u.email == email_login):
            content_user.self = "self"
        for user_subscribe in t_user_subscribe.objects.all():
            if (
                            user_subscribe.email_subscriber.email == email_login and user_subscribe.email_subscribed.email == u.email):
                content_user.is_subscribe = True
                break
        c_user.append(content_user)

    all_grup = t_grup.objects.all()
    id_grup = []

    class ContentGrup:
        grup = None
        join = "not_join"
        moderator = False

    c_grup = []
    for grup in all_grup:
        id_grup.append(grup.id_grup)
        content_grup = ContentGrup()
        content_grup.grup = grup
        if (grup.moderator.email == email_login):
            content_grup.moderator = True
        else:
            for user_grup in t_user_grup.objects.all():
                if (user_grup.email.email == email_login and user_grup.id_grup.id_grup == grup.id_grup):
                    if (user_grup.confirm):
                        content_grup.join = "is_join"
                    else:
                        content_grup.join = "wait"
                    break
        c_grup.append(content_grup)
    content = {
        'content_user': c_user,
        'content_group': c_grup,
        'email_user': id_user,
        'id_grup': id_grup,
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,
        'notif': notif,
        'notif_not_read': notif_not_read,
    }
    return render(request, 'users_groups.html', content)


def subscribe(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            return redirect('/forum/sign_in')
        email_subscriber = email_login
        email_subscribed = request.POST['email_subscribed']
        user_subscribe = t_user_subscribe(email_subscriber=t_user.objects.get(pk=email_subscriber),
                                          email_subscribed=t_user.objects.get(pk=email_subscribed))
        user_subscribe.save()
        sender = t_user.objects.get(pk=email_login)
        receiver = t_user.objects.get(pk=email_subscribed)
        notifikasi = t_notifikasi(email_sender=sender, email_receiver=receiver,
                                  id_tipe_notifikasi=t_tipe_notifikasi.objects.get(pk=1), read=False)
        notifikasi.isi_notifikasi = "<img class='ui avatar image' src='/static/images/avatar_user/"+sender.avatar_user+"'><a href='/forum/user/view/" + sender.email + "'>" + sender.full_name + "</a> Subscribe You"
        notifikasi.save()
        return HttpResponse("")
    else:
        return render(request, '404.html')


def unsubscribe(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            return redirect('/forum/sign_in')
        email_subscriber = email_login
        email_subscribed = request.POST['email_subscribed']
        user_subscribe = t_user_subscribe.objects.filter(email_subscriber=t_user.objects.get(pk=email_subscriber),
                                                         email_subscribed=t_user.objects.get(pk=email_subscribed))
        user_subscribe[0].delete()
        sender = t_user.objects.get(pk=email_login)
        receiver = t_user.objects.get(pk=email_subscribed)
        notifikasi = t_notifikasi(email_sender=sender, email_receiver=receiver,
                                  id_tipe_notifikasi=t_tipe_notifikasi.objects.get(pk=2), read=False)
        notifikasi.isi_notifikasi = "<img class='ui avatar image' src='/static/images/avatar_user/"+sender.avatar_user+"'><a href='/forum/user/view/" + sender.email + "'>" + sender.full_name + "</a> Unsubscribe You"
        notifikasi.save()
        return HttpResponse("")
    else:
        return render(request, '404.html')


def search_user(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            return redirect('/forum/user/sign_in')
        q = request.POST['q']
        all_user = t_user.objects.filter(full_name__icontains=q)
        users = []
        for user in all_user:
            if (user.verified == True):
                users.append(user)
        html = ""
        if (users):
            for u in users:
                html += ("<div class='four wide column'>" +
                         "<div class='ui grid ui stacked segment'>" +
                         "<div class='five wide column'>" +
                         "<img class='ui avatar image' src='/static/images/avatar_user/" + u.avatar_user + "'" +
                         "style='border-radius: 2px !important; width:50px !important; height:50px !important;'>" +
                         "</div>" +
                         "<div class='eleven wide column'>" +
                         "<a href='/forum/user/view/" + u.email + "' style='font-family: Exo, sans-serif;'>" + u.full_name + "<br></a>" +
                         "<span class='post'>" + u.jurusan + "<br>" + str(u.jumlah_topik_user) + " post</span><br>")
                if (email_login == u.email):
                    html += "<a class='ui grey label' id='' href='#'>Edit Profile</a>"
                else:
                    is_subscribe = False
                    for user_subscribe in t_user_subscribe.objects.filter(email_subscriber=email_login):
                        if (user_subscribe.email_subscribed.email == u.email):
                            is_subscribe = True
                            break
                    if (is_subscribe):
                        html += (
                            "<button class='ui red label' id='a_unsubs_" + str((u.email).replace("@", "")).replace(".",
                                                                                                                   "") + "'>Unsubscribe</button>" +
                            "<button class='ui teal label' id='a_subs_" + str((u.email).replace("@", "")).replace(".",
                                                                                                                  "") + "'style='display:none;'>Subscribe</button>")
                    else:
                        html += (
                            "<button class='ui red label' id='b_unsubs_" + str((u.email).replace("@", "")).replace(".",
                                                                                                                   "") + "'style='display:none;'>Unsubscribe</button>" +
                            "<button class='ui teal label' id='b_subs_" + str((u.email).replace("@", "")).replace(".",
                                                                                                                  "") + "'>Subscribe</button>")
                html += "</div></div></div>"
        else:
            html += "<h3 style='color:#e67300;'><br> No users matched your search.</h3><br><br>"
        return HttpResponse(html)
    else:
        return render(request, '404.html')


def create_grup(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            return redirect('/forum/user/sign_in')
        nama_grup = request.POST['name_group']
        deskripsi_grup = request.POST['desc']
        avatar_grup = request.POST['img']
        grup = t_grup(moderator=t_user.objects.get(pk=email_login), nama_grup=nama_grup, deskripsi_grup=deskripsi_grup,
                      jumlah_topik_grup=0, jumlah_anggota_grup=0, avatar_grup=avatar_grup)
        grup.save()
        return redirect('/forum/users/groups')
    else:
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
            notif_not_read = t_notifikasi.objects.filter(read=False,
                                                         email_receiver=t_user.objects.get(pk=email_login))
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
            'notif': notif,
            'notif_not_read': notif_not_read,
        }
        return render(request, 'create_grup.html', content)


def join_group(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            return redirect('/forum/user/sign_in')
        id_grup = request.POST['id_grup']
        user_grup = t_user_grup(email=t_user.objects.get(pk=email_login), id_grup=t_grup.objects.get(pk=id_grup),
                                confirm=False)
        user_grup.save()
        grup = t_grup.objects.get(pk=id_grup)
        sender = t_user.objects.get(pk=email_login)
        receiver = t_user.objects.get(pk=grup.moderator.email)
        notifikasi = t_notifikasi(email_sender=sender, email_receiver=receiver,
                                  id_tipe_notifikasi=t_tipe_notifikasi.objects.get(pk=3), read=False)
        notifikasi.isi_notifikasi = "<img class='ui avatar image' src='/static/images/avatar_user/"+sender.avatar_user+"'><a href='/forum/user/view/" + sender.email + "'>" + sender.full_name + "</a> Wants to Join to Your Group " + "<img class='ui avatar image' src='/static/images/avatar_group/"+grup.avatar_grup+"'><a href='/forum/group/edit/" + id_grup + "'>" + grup.nama_grup + "</a>"
        notifikasi.save()
        return HttpResponse("")
    else:
        return render(request, '404.html')


def leave_group(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            return redirect('/forum/user/sign_in')
        id_grup = request.POST['id_grup']
        user_grup = t_user_grup.objects.filter(email=t_user.objects.get(pk=email_login),
                                               id_grup=t_grup.objects.get(pk=id_grup))
        user_grup[0].delete()
        grup = t_grup.objects.get(pk=id_grup)
        grup.jumlah_anggota_grup -= 1
        grup.save()

        grup = t_grup.objects.get(pk=id_grup)
        sender = t_user.objects.get(pk=email_login)
        receiver = t_user.objects.get(pk=grup.moderator.email)
        notifikasi = t_notifikasi(email_sender=sender, email_receiver=receiver,
                                  id_tipe_notifikasi=t_tipe_notifikasi.objects.get(pk=7), read=False)
        notifikasi.isi_notifikasi = "<img class='ui avatar image' src='/static/images/avatar_user/"+sender.avatar_user+"'><a href='/forum/user/view/" + sender.email + "'>" + sender.full_name + "</a> Leave from Your Group " + "<img class='ui avatar image' src='/static/images/avatar_group/"+grup.avatar_grup+"'><a href='/forum/group/edit/" + id_grup + "'>" + grup.nama_grup + "</a>"
        notifikasi.save()

        return HttpResponse("")
    else:
        return render(request, '404.html')


def search_group(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            return redirect('/forum/user/sign_in')
        q = request.POST['q']
        all_grup = t_grup.objects.filter(nama_grup__icontains=q)
        html = ""
        if (all_grup):
            for grup in all_grup:
                html += ("<div class='four wide column'>" +
                         "<div class='ui grid ui stacked segment'>" +
                         "<div class='five wide column'>" +
                         "<img class='ui avatar image' src='/static/images/avatar_group/" + grup.avatar_grup + "'" +
                         "style='border-radius: 2px !important; width:50px !important; height:50px !important;'>" +
                         "</div>" +
                         "<div class='eleven wide column'>" +
                         "<a href='' style='font-family: Exo, sans-serif;'>" + grup.nama_grup + "<br></a>" +
                         "<span class='post'>" + str(grup.jumlah_anggota_grup) + " members</span><br>")
                if (grup.moderator.email == email_login):
                    html += "<a class='ui grey label' id='' href='#'>Edit Group</a>"
                else:
                    join = "not_join"
                    for user_grup in t_user_grup.objects.all():
                        if (user_grup.email.email == email_login and user_grup.id_grup.id_grup == grup.id_grup):
                            if (user_grup.confirm):
                                join = "is_join"
                            else:
                                join = "wait"
                            break
                    if (join == "is_join"):
                        html += (
                            "<button class='ui red label' id='a_leave_" + str(grup.id_grup) + "'>Leave Group</button>" +
                            "<button class='ui teal label' id='a_join_" + str(
                                grup.id_grup) + "'style='display:none;'>Join Group</button>" +
                            "<label class='ui orange label' id='a_waiting_" + str(
                                grup.id_grup) + "' style='display: none;'>Waiting...</label>")
                    elif (join == "not_join"):
                        html += (
                            "<button class='ui teal label' id='b_join_" + str(grup.id_grup) + "'>Join Group</button>" +
                            "<label class='ui orange label' id='b_waiting_" + str(
                                grup.id_grup) + "' style='display: none;'>Waiting...</label>")
                    else:
                        html += "<label class='ui orange label'>Waiting...</label>"
                html += "</div></div></div>"
        else:
            html += "<h3 style='color:#e67300;'><br> No groups matched your search.</h3><br><br>"
        return HttpResponse(html)
    else:
        return render(request, '404.html')


def view_user(request, email):
    try:
        email_login = request.session['email_login']
    except:
        return redirect('/forum/user/sign_in')
    try:
        user = t_user.objects.get(pk=email)
    except:
        return render(request, '404.html')
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
    user.jumlah_subscriber = len(t_user_subscribe.objects.filter(email_subscribed=user))
    user.save()

    class ComponentUser():
        user = None
        topik = []
        grup = []
        subscribe = "not"

    class Topic():
        topik = None
        id_hash = ""

    c_user = ComponentUser()
    c_user.user = user
    if (email_login == email):
        c_user.subscribe = "self"
    else:
        user_subscribe = t_user_subscribe.objects.filter(email_subscriber=t_user.objects.get(pk=email_login),
                                                         email_subscribed=user)
        if (user_subscribe):
            c_user.subscribe = "is"
    for grup in t_grup.objects.filter(moderator=user):
        c_user.grup.append(grup)
    user_grup = t_user_grup.objects.filter(email=user, confirm=True)
    for ug in user_grup:
        c_user.grup.append(ug.id_grup)

    all_topic_user = t_topik.objects.filter(email=user, id_grup=None)
    all_topic_user = sorted(all_topic_user, key=lambda t: t.jumlah_komentar_topik, reverse=True)
    for topic in all_topic_user:
        t = Topic()
        t.topik = topic
        hash_id_topik = md5_crypt.encrypt(str(topic.id_topik))
        t.id_hash = hash_id_topik[:0] + hash_id_topik[3:]
        c_user.topik.append(t)

    content = {
        'c_user': c_user,
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,
        'notif': notif,
        'notif_not_read': notif_not_read,
    }
    return render(request, 'view_user.html', content)


def view_group(request, id):
    try:
        email_login = request.session['email_login']
    except:
        return redirect('/forum/user/sign_in')
    try:
        grup = t_grup.objects.get(pk=id)
    except:
        return render(request, '404.html')
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

    class ComponentGroup():
        grup = None
        is_moderator = False
        is_join = "not"
        user = []
        topic = []

    c_grup = ComponentGroup()
    c_grup.grup = grup
    if (grup.moderator.email == email_login):
        c_grup.is_moderator = True
    user = t_user_grup.objects.filter(email=t_user.objects.get(pk=email_login), id_grup=grup)
    if (user):
        if (user[0].confirm):
            c_grup.is_join = "is"
        else:
            c_grup.is_join = "wait"

    for u in t_user_grup.objects.filter(id_grup=grup, confirm=True):
        c_grup.user.append(u.email)
    for t in t_topik.objects.filter(id_grup=grup):
        c_grup.topic.append(t)

    content = {
        'c_grup': c_grup,
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,
        'notif': notif,
        'notif_not_read': notif_not_read,
    }
    return render(request, 'view_group.html', content)


def user_edit(request):
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
    club = t_kategori.objects.filter(id_tipe_kategori=t_tipe_kategori.objects.get(pk=5))
    all_subscibers = []
    id_grups = []
    id_topics = []
    my_groups = t_grup.objects.filter(moderator=t_user.objects.get(pk=email_login))
    my_topics = t_topik.objects.filter(email=t_user.objects.get(pk=email_login))

    class ComponentTopik():
        topic = None
        id_hash = ""

    c_topic = []
    for user in t_user_subscribe.objects.filter(email_subscribed=t_user.objects.get(pk=email_login)):
        all_subscibers.append(t_user.objects.get(pk=user.email_subscriber.email))
    for grup in my_groups:
        id_grups.append(grup.id_grup)
    for topic in my_topics:
        ct = ComponentTopik()
        ct.topic = topic
        hash_id_topik = md5_crypt.encrypt(str(topic.id_topik))
        ct.id_hash = hash_id_topik[:0] + hash_id_topik[3:]
        c_topic.append(ct)
        id_topics.append(topic.id_topik)
    email_hash = md5_crypt.encrypt(str(email_login))
    email_hash = email_hash[:0] + email_hash[3:]
    content = {
        'user': t_user.objects.get(pk=email_login),
        'club': club,
        'all_subscibers': all_subscibers,
        'my_groups': my_groups,
        'id_grups': id_grups,
        'c_topic': c_topic,
        'id_topics': id_topics,
        'email_hash': email_hash,
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,
        'notif': notif,
        'notif_not_read': notif_not_read,
    }
    return render(request, 'edit_profile.html', content)


def update_avatar_user(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            pass
        user = t_user.objects.get(pk=email_login)
        img = request.POST['img']
        user.avatar_user = img
        user.save()
        return HttpResponse("")


def update_name_user(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            pass
        user = t_user.objects.get(pk=email_login)
        name = request.POST['name']
        user.full_name = name
        user.save()
        return HttpResponse("")


def update_club_user(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            pass
        user = t_user.objects.get(pk=email_login)
        club = request.POST['club']
        user.klub = club
        user.save()
        return HttpResponse("")


def delete_grup(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            pass
        id_grup = request.POST['id_grup']
        grup = t_grup.objects.get(pk=id_grup)
        grup.delete()
        return HttpResponse("")


def delete_topic(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            pass
        id_topic = request.POST['id_topic']
        topic = t_topik.objects.get(pk=id_topic)
        if (topic.id_grup):
            grup = t_grup.objects.get(pk=topic.id_grup.id_grup)
            grup.jumlah_topik_grup -= 1
            grup.save()
        topic.delete()
        return HttpResponse("")


def group_edit(request, id):
    try:
        email_login = request.session['email_login']
    except:
        return redirect('/forum/user/sign_in')

    try:
        grup = t_grup.objects.get(pk=id)
    except:
        return render(request, '404.html')
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
        notif_not_read = t_notifikasi.objects.filter(read=False,
                                                     email_receiver=t_user.objects.get(pk=email_login))
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
    if not (email_login == grup.moderator.email):
        return render(request, '404.html')
    user_request = []
    email_request = []
    members = []
    email_members = []
    id_topics = []
    for user in t_user_grup.objects.filter(id_grup=grup, confirm=False):
        user_request.append(user.email)
        email_request.append(user.email.email)

    for user in t_user_grup.objects.filter(id_grup=grup, confirm=True):
        members.append(user.email)
        email_members.append(user.email.email)

    class ComponentTopik():
        topic = None
        id_hash = ""

    c_topic = []
    for topic in t_topik.objects.filter(id_grup=grup):
        ct = ComponentTopik()
        ct.topic = topic
        hash_id_topik = md5_crypt.encrypt(str(topic.id_topik))
        ct.id_hash = hash_id_topik[:0] + hash_id_topik[3:]
        c_topic.append(ct)
        id_topics.append(topic.id_topik)

    content = {
        'grup': grup,
        'user_request': user_request,
        'email_request': email_request,
        'members': members,
        'email_members': email_members,
        'c_topic': c_topic,
        'id_topics': id_topics,
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,

        'notif': notif,
        'notif_not_read': notif_not_read,
    }

    return render(request, 'edit_group.html', content)


def update_avatar_group(request):
    if (request.method == 'POST'):
        img = request.POST['img']
        id_grup = request.POST['id_grup']
        grup = t_grup.objects.get(pk=id_grup)
        grup.avatar_grup = img
        grup.save()
        return HttpResponse("")


def update_nama_group(request):
    if (request.method == 'POST'):
        nama = request.POST['nama']
        id_grup = request.POST['id_grup']
        grup = t_grup.objects.get(pk=id_grup)
        grup.nama_grup = nama
        grup.save()
        return HttpResponse("")


def update_desc_group(request):
    if (request.method == 'POST'):
        desc = request.POST['desc']
        id_grup = request.POST['id_grup']
        grup = t_grup.objects.get(pk=id_grup)
        grup.deskripsi_grup = desc
        grup.save()
        return HttpResponse("")


def accept_user(request):
    if (request.method == 'POST'):
        id_grup = request.POST['id_grup']
        email = request.POST['email']
        user_grup = t_user_grup.objects.filter(email=t_user.objects.get(pk=email),
                                               id_grup=t_grup.objects.get(pk=id_grup))
        u_g = t_user_grup.objects.get(pk=user_grup[0].pk)
        u_g.confirm = True
        u_g.save()
        grup = t_grup.objects.get(pk=id_grup)
        grup.jumlah_anggota_grup += 1
        grup.save()

        grup = t_grup.objects.get(pk=id_grup)
        receiver = t_user.objects.get(pk=email)
        sender = t_user.objects.get(pk=grup.moderator.email)
        notifikasi = t_notifikasi(email_sender=sender, email_receiver=receiver,
                                  id_tipe_notifikasi=t_tipe_notifikasi.objects.get(pk=4), read=False)
        notifikasi.isi_notifikasi = "<img class='ui avatar image' src='/static/images/avatar_user/"+sender.avatar_user+"'><a href='/forum/user/view/" + sender.email + "'>" + sender.full_name + "</a> Accept Your Request to Join Group " + "<img class='ui avatar image' src='/static/images/avatar_group/"+grup.avatar_grup+"'><a href='/forum/group/view/" + id_grup + "'>" + grup.nama_grup + "</a>"
        notifikasi.save()
        return HttpResponse("")


def reject_user(request):
    if (request.method == 'POST'):
        id_grup = request.POST['id_grup']
        email = request.POST['email']
        user_grup = t_user_grup.objects.filter(email=t_user.objects.get(pk=email),
                                               id_grup=t_grup.objects.get(pk=id_grup))
        u_g = t_user_grup.objects.get(pk=user_grup[0].pk)
        u_g.confirm = True
        u_g.delete()

        grup = t_grup.objects.get(pk=id_grup)
        receiver = t_user.objects.get(pk=email)
        sender = t_user.objects.get(pk=grup.moderator.email)
        notifikasi = t_notifikasi(email_sender=sender, email_receiver=receiver,
                                  id_tipe_notifikasi=t_tipe_notifikasi.objects.get(pk=6), read=False)
        notifikasi.isi_notifikasi = "<img class='ui avatar image' src='/static/images/avatar_user/"+sender.avatar_user+"'><a href='/forum/user/view/" + sender.email + "'>" + sender.full_name + "</a> Reject Your Request to Join Group " + "<img class='ui avatar image' src='/static/images/avatar_group/"+grup.avatar_grup+"'><a href='/forum/group/view/" + id_grup + "'>" + grup.nama_grup + "</a>"
        notifikasi.save()

        return HttpResponse("")


def remove_user(request):
    if (request.method == 'POST'):
        id_grup = request.POST['id_grup']
        email = request.POST['email']
        user_grup = t_user_grup.objects.filter(email=t_user.objects.get(pk=email),
                                               id_grup=t_grup.objects.get(pk=id_grup))
        u_g = t_user_grup.objects.get(pk=user_grup[0].pk)
        u_g.confirm = True
        u_g.delete()
        grup = t_grup.objects.get(pk=id_grup)
        grup.jumlah_anggota_grup -= 1
        grup.save()

        grup = t_grup.objects.get(pk=id_grup)
        receiver = t_user.objects.get(pk=email)
        sender = t_user.objects.get(pk=grup.moderator.email)
        notifikasi = t_notifikasi(email_sender=sender, email_receiver=receiver,
                                  id_tipe_notifikasi=t_tipe_notifikasi.objects.get(pk=5), read=False)
        notifikasi.isi_notifikasi = "<img class='ui avatar image' src='/static/images/avatar_user/"+sender.avatar_user+"'><a href='/forum/user/view/" + sender.email + "'>" + sender.full_name + "</a> Removed You from Group " + "<img class='ui avatar image' src='/static/images/avatar_group/"+grup.avatar_group+"'><a href='/forum/group/view/" + id_grup + "'>" + grup.nama_grup + "</a>"
        notifikasi.save()

        return HttpResponse("")

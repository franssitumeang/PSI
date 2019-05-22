from django.shortcuts import redirect, render
from forum.models import t_topik, t_tipe_kategori, t_grup, t_user_grup, t_kategori, t_user, t_komentar, \
    t_user_subscribe, t_user_log, t_notifikasi, t_tipe_notifikasi
from passlib.hash import md5_crypt


def create_topic(request):
    if (request.method == 'POST'):
        try:
            email_login = request.session['email_login']
        except:
            email_login = None
        if (email_login == None):
            return redirect("/forum/user/sign_in")
        email = t_user.objects.get(pk = email_login)
        email.jumlah_topik_user+=1
        email.save()
        id_grup = None
        id_kategori = None
        if(request.POST['data-grup']):
            id_grup = t_grup.objects.get(pk = int(request.POST['data-grup']))
            id_grup.jumlah_topik_grup+=1
            id_grup.save()
        if(request.POST['data-kategori']):
            id_kategori = t_kategori.objects.get(pk = int(request.POST['data-kategori']))
        judul_topik = request.POST['title']
        isi_topik = request.POST['content']
        tags = request.POST['data-tag']
        topik = t_topik(email = email, id_grup = id_grup, id_kategori = id_kategori, judul_topik = judul_topik, isi_topik = isi_topik, tags = tags, jumlah_komentar_topik = 0)
        topik.save()
        new_topik = t_topik.objects.latest('id_topik')
        id_topik = new_topik.id_topik
        hash_id_topik = md5_crypt.encrypt(str(id_topik))
        url_id = hash_id_topik[:0] + hash_id_topik[3:]
        if(id_kategori):
            for user_subscribe in t_user_subscribe.objects.filter(email_subscribed=t_user.objects.get(pk=email_login)):
                sender = user_subscribe.email_subscribed
                receiver = user_subscribe.email_subscriber
                notifikasi = t_notifikasi(email_sender=sender, email_receiver=receiver,
                                          id_tipe_notifikasi=t_tipe_notifikasi.objects.get(pk=8), read=False)
                notifikasi.isi_notifikasi = "<img class='ui avatar image' src='/static/images/avatar_user/" + sender.avatar_user + "'><a href='/forum/user/view/" + sender.email + "'>" + sender.full_name + "</a> Post New Topic <a href='/forum/topic/view/" + str(
                    url_id) + "'>View Topic</a>"
                notifikasi.save()
        return redirect('/forum/topic/view/'+str(url_id))
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

        my_group = t_grup.objects.filter(moderator = t_user.objects.get(pk=email_login))
        user_grup = t_user_grup.objects.filter(email = t_user.objects.get(pk=email_login), confirm = True)
        joined_grup = []
        for grup in user_grup:
            joined_grup.append(t_grup.objects.get(pk=grup.id_grup.id_grup))
        all_topik = t_topik.objects.all()
        all_tag = []
        for topik in all_topik:
            tag = str(topik.tags).lower()
            get_unique_tags(tag.split(','),all_tag)

        #test object custom
        class Kategori():
            tipe_kategori = None
            all_kategori = []
        all_kategori = []
        all_tipe_kategori = t_tipe_kategori.objects.all()
        for tipe_kategori in all_tipe_kategori:
            k = Kategori()
            k.tipe_kategori = tipe_kategori
            k.all_kategori = t_kategori.objects.filter(id_tipe_kategori = tipe_kategori.id_tipe_kategori)
            all_kategori.append(k)

        if(email_login):
            content = {
                'all_kategori': all_kategori,
                'my_grup': my_group,
                'joined_grup': joined_grup,
                'all_tag': all_tag,
                'email_login': user_login,
                'c_category': c_category,
                'c_joined_grup': c_joined_grup,
                'c_my_grup': c_my_grup,
                'c_subscription': c_subscription,
                'notif': notif,
                'notif_not_read': notif_not_read,
            }
            return render(request, 'create_topic.html', content)
        else:
            return redirect('/forum/user/sign_in')

def get_unique_tags(tags, list_tag):
    for tag in tags:
        if(tag not in list_tag):
            list_tag.append(tag)

def view_topic(request, id_hash):
    all_topik = t_topik.objects.all()
    topik = None
    try:
        email_login = request.session['email_login']
    except:
        return redirect('/forum/user/sign_in')
    try:
        for t in all_topik:
            if(md5_crypt.verify(str(t.id_topik), '$1$'+id_hash)):
                topik = t
                break
        user = t_user.objects.get(pk=topik.email_id)
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

    user_log = t_user_log(email=t_user.objects.get(pk=email_login), id_topik=topik)
    user_log.save()

    kategori = None
    grup = None
    if(topik.id_kategori != None):
        kategori = t_kategori.objects.get(pk=topik.id_kategori.id_kategori)
    else:
        grup = t_grup.objects.get(pk=topik.id_grup.id_grup)
    class Komentar():
        user = None
        comment = None
    all_komentar = []
    komentars = t_komentar.objects.filter(id_topik = topik.id_topik)
    for k in komentars:
        komentar = Komentar()
        komentar.comment = k
        komentar.user = t_user.objects.get(pk=k.email.email)
        all_komentar.append(komentar)

    all_related_topic = []
    tmp_all_related_topic = []
    class ComponentRelatedTopic():
        judul_topic = ""
        id_hash = ""
    for tag in (str(topik.tags).lower()).split(','):
        for topic in t_topik.objects.filter(id_grup=None):
            topic_tag = (str(topic.tags).lower()).split(',')
            if tag in topic_tag:
                if not topic in tmp_all_related_topic and topic != topik:
                    tmp_all_related_topic.append(topic)
                    crt = ComponentRelatedTopic()
                    crt.judul_topic = topic.judul_topik
                    hash_id_topik = md5_crypt.encrypt(str(topic.id_topik))
                    crt.id_hash = hash_id_topik[:0] + hash_id_topik[3:]
                    all_related_topic.append(crt)

    content = {
        'topik': topik,
        'user': user,
        'kategori': kategori,
        'grup': grup,
        'tags': str(topik.tags).split(','),
        'user_login':t_user.objects.get(pk = email_login),
        'all_komentar': all_komentar,
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,
        'all_related_topic': all_related_topic,
        'notif': notif,
        'notif_not_read': notif_not_read,
    }
    return render(request, 'view_topik.html', content)

def topic_category(request, id):
    try:
        email_login = request.session['email_login']
    except:
        return redirect('/forum/user/sign_in')
    try:
        kategori = t_kategori.objects.get(pk = id)
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
    all_topic = t_topik.objects.filter(id_kategori = kategori)
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
    content = {
        'kategori':kategori,
        'c_topic' : c_topic,
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,
        'notif': notif,
        'notif_not_read': notif_not_read,

    }
    return render(request, 'topic_category.html', content)

def topic_group(request, id):
    try:
        email_login = request.session['email_login']
    except:
        return redirect('/forum/user/sign_in')
    try:
        grup = t_grup.objects.get(pk = id)
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
    is_grup = False
    if(grup.moderator == t_user.objects.get(pk = email_login)):
        is_grup = True
    if(t_user_grup.objects.filter(email = t_user.objects.get(pk = email_login), id_grup = grup, confirm = True)):
        is_grup = True
    if not (is_grup):
        return render(request, '404.html')
    class ComponentTopic():
        topic = None
        id_hash = ""
        tags = []
    c_topic = []
    for topic in t_topik.objects.filter(id_grup = grup):
        ct = ComponentTopic()
        ct.topic = topic
        hash_id_topik = md5_crypt.encrypt(str(topic.id_topik))
        ct.id_hash = hash_id_topik[:0] + hash_id_topik[3:]
        ct.tags = str(topic.tags).split(',')
        c_topic.append(ct)
    content = {
        'grup':grup,
        'c_topic': c_topic,
        'email_login': user_login,
        'c_category': c_category,
        'c_joined_grup': c_joined_grup,
        'c_my_grup': c_my_grup,
        'c_subscription': c_subscription,
        'notif': notif,
        'notif_not_read': notif_not_read,
    }
    return render(request, 'topic_grup.html', content)



import json
import urllib
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import redirect, render

from forum.models import t_user, t_tipe_kategori, t_kategori, t_user_grup, t_grup, t_user_subscribe, t_notifikasi
from passlib.hash import pbkdf2_sha256, md5_crypt
from django.core import serializers
import json
def create_user(request):
    all_user = t_user.objects.all()
    auser_email = []
    for user in all_user:
        auser_email.append(user.email)
    user_email = json.dumps(auser_email)
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        faculty = request.POST['faculty']
        major = request.POST['major']
        if(name == '' or len(name) > 20 or email == '' or email.find('@') == -1 or password == '' or len(password) < 6 or faculty == '' or major == ''):
            content = {
                'is_valid' : "False",
                'error' : 'true',
                'user_email' : user_email
            }
            return render(request, 'register_user.html', content)
        else:
            hash_password = pbkdf2_sha256.encrypt(password, rounds=1200, salt_size=32)
            hash_email = md5_crypt.encrypt(email)
            url_email = hash_email[:0]+hash_email[3:]
            #CAPTCHA
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': '6LdWFR4UAAAAANxEvnVsMHEhMIlXs1OH2tSHAoDL',
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            if result['success']:
                user = t_user(email = email, full_name = name, password = hash_password, verified = False, jumlah_subscriber=0, jumlah_topik_user=0, avatar_user='user_default.png', fakultas=faculty, jurusan=major)
                try:
                    user.save()
                except Exception as e:
                    content = {
                        'is_valid': "False",
                        'error': 'true',
                        'user_email' : user_email
                    }
                    return render(request, 'register_user.html', content)
                subject = '[Please verify your email address]'
                text_content = ''
                html_content = '<h4>Hello '+name+',</h4>' \
                               '<p>We are almost done creating your <strong>FORUM MAHASISWA account</strong>. You can this account to log in into <strong>FORUM MAHASISWA</strong>.</p>' \
                               '<p>Full Name : '+name+'</p>' \
                               '<p>Faculty : ' + faculty + '</p>' \
                                '<p>Major : ' + major + '</p>' \
                                '<p>Log in email : '+email+'</p><br>' \
                               '<p>Click the link below to verify this email address</p>' \
                               '<a href="http://localhost:8000/forum/user/verify/'+url_email+'" style="background-color: #008CBA; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px;" >VERIFY ACCOUNT</a><br><br>'\
                                '<hr>' \
                                '<p><strong>Thank You</strong></p>' \
                                '<p><strong>Forum Mahasiswa</strong></p>'
                msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                content = {
                    'is_valid': "True",
                    'user_email' : user_email
                }
                return render(request, 'register_user.html', content)
            else:
                content = {
                    'is_valid': "False",
                    'error': 'true',
                    'user_email' : user_email
                }
                return render(request, 'register_user.html', content)
    else:
        try:
            email_login = request.session['email_login']
        except:
            email_login = None
        if(email_login):
            return redirect('/forum')
        content = {
            'is_valid': "False",
            'user_email' : user_email,
        }
        return render(request, 'register_user.html', content)

def verify_user(request, email_hash):
    all_user = t_user.objects.all()
    try:
        for users in all_user:
            if(md5_crypt.verify(users.email,'$1$'+email_hash)):
                users.verified = True
                users.save()
                break
    except Exception as e:
        return render(request, '404.html')
    return redirect('/forum/user/sign_in')

def change_password(request, email_hash):
    if(request.method == 'POST'):
        all_user = t_user.objects.all()
        password = request.POST['password']
        try:
            for users in all_user:
                if (md5_crypt.verify(users.email, '$1$' + email_hash)):
                    users.password = hash_password = pbkdf2_sha256.encrypt(password, rounds=1200, salt_size=32)
                    users.save()
                    break
        except Exception as e:
            return render(request, '404.html')
        return redirect('/forum/user/sign_in')
    else:
        try:
            email_login = request.session['email_login']
        except:
            email_login = None
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
        all_user = t_user.objects.all()
        is_email = False
        try:
            for users in all_user:
                if (md5_crypt.verify(users.email, '$1$'+email_hash)):
                    is_email = True
                    break
        except Exception as e:
            is_email = False
        if (is_email):
            content = {
                'email_hash' : email_hash,
                'email_login': user_login,
                'c_category': c_category,
                'c_joined_grup': c_joined_grup,
                'c_my_grup': c_my_grup,
                'c_subscription': c_subscription,
                'notif': notif,
                'notif_not_read': notif_not_read,
            }
            return render(request, 'change_password.html', content)
        else:
            return render(request, '404.html')
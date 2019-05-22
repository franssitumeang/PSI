from collections import Counter

from django.http import HttpResponse
from django.shortcuts import render, redirect
from forum.models import t_tipe_kategori,t_kategori,t_tipe_notifikasi,t_user, t_topik

def admin_page(request):
    try:
        email_login = request.session['admin']
    except:
        return redirect("/forum/user/sign_in")
    user = []
    user_n = []
    tags = []
    tag_n = []
    all_user = t_user.objects.all()
    all_user = sorted(all_user, key=lambda t: t.jumlah_topik_user, reverse=True)
    for i in range(0,5):
        user.append(all_user[i].full_name)
        user_n.append(all_user[i].jumlah_topik_user)
    user_n.append(0)
    for i in range(4, len(all_user)-1):
        user_n[5] += all_user[i].jumlah_topik_user
    class ComponentTag():
        tag = ""
        n = 0
    all_tag = []
    all_tag_non_duplicate = []
    c_tag = []
    for topic in t_topik.objects.all():
        for tag in (str(topic.tags).lower()).split(','):
            all_tag.append(tag)
    all_tag_non_duplicate = list(set(all_tag))
    for tag in all_tag_non_duplicate:
        componentTag = ComponentTag()
        componentTag.tag = tag
        componentTag.n = all_tag.count(tag)
        c_tag.append(componentTag)
    c_tag = sorted(c_tag, key=lambda t: t.n, reverse=True)
    for i in range(0,10):
        tags.append(c_tag[i].tag)
        tag_n.append(c_tag[i].n)
    tag_n.append(0)
    for i in range(9, len(c_tag) - 1):
        tag_n[10] += c_tag[i].n

    content = {
        'all_tipe_kategori': t_tipe_kategori.objects.all(),
        'kategori':t_kategori.objects.all(),
        'tipe_notifikasi':t_tipe_notifikasi.objects.all(),
        'user':user,
        'user_n': user_n,
        'tag': tags,
        'tag_n': tag_n,

    }
    return render(request, 'admin_page.html', content)

def create_tipe_kategori(request):
    if(request.method == 'POST'):
        nama_kategori = request.POST['nama_kategori']
        deskripsi_tipe_kategori = request.POST['deskripsi_tipe_kategori']
        tipe_kategori = t_tipe_kategori(nama_kategori = nama_kategori, deskripsi_tipe_kategori = deskripsi_tipe_kategori)
        tipe_kategori.save()
        last_tipe_kategori = t_tipe_kategori.objects.latest('id_tipe_kategori')
        id = last_tipe_kategori.id_tipe_kategori
        return HttpResponse(id)
    else:
        return render(request, '404.html')

def create_kategori(request):
    if(request.method == 'POST'):
        id_tipe_kategori = request.POST['id_tipe_kategori']
        judul_kategori = request.POST['judul_kategori']
        deskripsi_kategori = request.POST['deskripsi_kategori']

        kategori = t_kategori(id_tipe_kategori = t_tipe_kategori.objects.get(pk = id_tipe_kategori), judul_kategori = judul_kategori, deskripsi_kategori = deskripsi_kategori)
        kategori.save()
        return HttpResponse("")
    else:
        return render(request, '404.html')

def create_tipe_notifikasi(request):
    if(request.method == 'POST'):
        nama_tipe_notifikasi = request.POST['nama_tipe_notifikasi']
        notifikasi = t_tipe_notifikasi(nama_tipe_notifikasi = nama_tipe_notifikasi)
        notifikasi.save()
        return HttpResponse("")
    else:
        return render(request, '404.html')

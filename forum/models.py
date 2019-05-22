from django.db import models

class t_user(models.Model):
    email = models.CharField(max_length=100, primary_key=True)
    full_name = models.CharField(max_length=200, null=False)
    password = models.CharField(max_length=200, null=False)
    verified = models.BooleanField(default=False, null=False)
    jumlah_subscriber = models.IntegerField(default=0, null=False)
    jumlah_topik_user = models.IntegerField(default=0, null=False)
    avatar_user = models.CharField(max_length=50, null=False, default='user_default.png')
    fakultas = models.CharField(max_length=100, null=False)
    jurusan = models.CharField(max_length=100, null=False)
    klub = models.CharField(max_length=255, null=True)
    date_created_user = models.DateTimeField(auto_now_add=True)

class t_tipe_kategori(models.Model):
    id_tipe_kategori = models.IntegerField(null=False, primary_key=True)
    nama_kategori = models.CharField(null=False, max_length=255)
    deskripsi_tipe_kategori = models.TextField(null=False)
    date_created_tipe_kategori = models.DateTimeField(auto_now_add=True, null=False)

class t_kategori(models.Model):
    id_kategori = models.IntegerField(null=False, primary_key=True)
    id_tipe_kategori = models.ForeignKey(t_tipe_kategori, on_delete=models.CASCADE)
    judul_kategori = models.CharField(max_length=255, null=False)
    deskripsi_kategori = models.TextField(null=False)
    date_created_kategori = models.DateTimeField(auto_now_add=True, null=False)

class t_tipe_notifikasi(models.Model):
    id_tipe_notifikasi = models.IntegerField(primary_key=True, null=False)
    nama_tipe_notifikasi = models.CharField(max_length=255, null=False)
    date_created_tipe_notifikasi = models.DateTimeField(auto_now_add=True, null=False)

class t_grup(models.Model):
    id_grup = models.IntegerField(primary_key=True, null=False)
    moderator = models.ForeignKey(t_user, on_delete=models.CASCADE)
    nama_grup = models.CharField(max_length=255, null=False)
    deskripsi_grup = models.TextField(null=False)
    jumlah_topik_grup = models.IntegerField(null=False)
    jumlah_anggota_grup = models.IntegerField(null=False)
    avatar_grup = models.CharField(max_length=255)
    date_created_grup = models.DateTimeField(auto_now_add=True, null=False)

class t_user_grup(models.Model):
    email = models.ForeignKey(t_user, on_delete=models.CASCADE)
    id_grup = models.ForeignKey(t_grup, on_delete=models.CASCADE)
    confirm = models.BooleanField(default=False)

class t_user_subscribe(models.Model):
    email_subscriber = models.ForeignKey(t_user, on_delete=models.CASCADE, related_name='subscriber')
    email_subscribed = models.ForeignKey(t_user, on_delete=models.CASCADE, related_name='subscribed')

class t_topik(models.Model):
    id_topik = models.IntegerField(primary_key=True, null=False)
    email = models.ForeignKey(t_user, on_delete=models.CASCADE, null=True)
    id_grup = models.ForeignKey(t_grup, on_delete=models.CASCADE, null=True)
    id_kategori = models.ForeignKey(t_kategori, on_delete=models.CASCADE, null=True)
    judul_topik = models.CharField(max_length=255, null=False)
    isi_topik = models.TextField(null=True)
    jumlah_komentar_topik = models.IntegerField(null=False)
    tags = models.TextField(null=True)
    date_created_topik = models.DateTimeField(auto_now_add=True, null=False)

class t_komentar(models.Model):
    id_komentar = models.IntegerField(primary_key=True, null=False)
    email = models.ForeignKey(t_user, on_delete=models.CASCADE, null=True)
    id_topik = models.ForeignKey(t_topik, on_delete=models.CASCADE, null=True)
    isi_komentar = models.TextField(null=False)
    date_created_komentar = models.DateTimeField(auto_now_add=True, null=False)

class t_user_log(models.Model):
    email = models.ForeignKey(t_user, on_delete=models.CASCADE)
    id_topik = models.ForeignKey(t_topik, on_delete=models.CASCADE)

class t_notifikasi(models.Model):
    id_notifikasi = models.IntegerField(primary_key=True, null=False)
    email_sender = models.ForeignKey(t_user, on_delete=models.CASCADE, null=True, related_name='sender')
    email_receiver = models.ForeignKey(t_user, on_delete=models.CASCADE, null=True, related_name='receiver')
    id_tipe_notifikasi = models.ForeignKey(t_tipe_notifikasi, on_delete=models.CASCADE, null=True)
    isi_notifikasi = models.TextField(null=False)
    read = models.BooleanField(default=False)
    date_created_notifikasi = models.DateTimeField(auto_now_add=True, null=False)
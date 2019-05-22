from django.conf.urls import url
from .controllers import index_controller, register_user_controller, topic_controller, admin_controller, \
    users_groups_controller
from django.conf.urls import (handler404)

handler404 = 'index_controller.page_not_found'


urlpatterns = [
    url(r'^$', index_controller.index),
    url(r'^/user/register$', register_user_controller.create_user),
    url(r'^/user/verify/(?P<email_hash>.*)$', register_user_controller.verify_user),
    url(r'^/user/sign_in$', index_controller.sign_in),
    url(r'^/user/forgot_password$', index_controller.forgot_password),
    url(r'^/user/change_password/(?P<email_hash>.*)$', register_user_controller.change_password),
    url(r'^/topic/create', topic_controller.create_topic),
    url(r'^/admin_page', admin_controller.admin_page),
    url(r'^/admin/create_tipe_kategori', admin_controller.create_tipe_kategori),
    url(r'^/admin/create_kategori', admin_controller.create_kategori),
    url(r'^/admin/create_tipe_notifikasi', admin_controller.create_tipe_notifikasi),
    url(r'^/topic/view/(?P<id_hash>.*)$', topic_controller.view_topic),
    url(r'^/users/groups$', users_groups_controller.view),
    url(r'^/subscribe$', users_groups_controller.subscribe),
    url(r'^/unsubscribe$', users_groups_controller.unsubscribe),
    url(r'^/search_user$', users_groups_controller.search_user),
    url(r'^/group/create_new$', users_groups_controller.create_grup),
    url(r'^/join$', users_groups_controller.join_group),
    url(r'^/leave$', users_groups_controller.leave_group),
    url(r'^/search_group$', users_groups_controller.search_group),
    url(r'^/user/view/(?P<email>.*)$', users_groups_controller.view_user),
    url(r'^/group/view/(?P<id>.*)$', users_groups_controller.view_group),
    url(r'^/user/edit/profile$', users_groups_controller.user_edit),
    url(r'^/sign_out$', index_controller.sign_out),
    url(r'^/update_avatar_user$', users_groups_controller.update_avatar_user),
    url(r'^/update_name_user$', users_groups_controller.update_name_user),
    url(r'^/update_club_user$', users_groups_controller.update_club_user),
    url(r'^/delete_grup$', users_groups_controller.delete_grup),
    url(r'^/delete_topic$', users_groups_controller.delete_topic),
    url(r'^/group/edit/(?P<id>.*)$', users_groups_controller.group_edit),
    url(r'^/update_avatar_group$', users_groups_controller.update_avatar_group),
    url(r'^/update_nama_group$', users_groups_controller.update_nama_group),
    url(r'^/update_desc_group$', users_groups_controller.update_desc_group),
    url(r'^/accept_user$', users_groups_controller.accept_user),
    url(r'^/reject_user$', users_groups_controller.reject_user),
    url(r'^/remove_user$', users_groups_controller.remove_user),
    url(r'^/topic/category/(?P<id>.*)$', topic_controller.topic_category),
    url(r'^/topic/group/(?P<id>.*)$', topic_controller.topic_group),
    url(r'^/topic/search$', index_controller.search_topic),
    url(r'^/topic/recommended$', index_controller.topic_recommended),
    url(r'^/update_notif$', index_controller.update_notif),
]

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("all_posts", views.all_posts, name="all_posts"),
    path("post/<int:post_id>", views.post, name="post"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("follow/<str:username>", views.follow_toggle, name="follow"),
    path("following", views.following_posts, name="following"),
]

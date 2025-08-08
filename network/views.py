from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


from .models import User


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def new_post(request):
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            from .models import Post

            post = Post(user=request.user, content=content)
            post.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/new_post.html",
                {"message": "Post content cannot be empty."},
            )
    else:
        return render(request, "network/index.html")


def all_posts(request):
    from .models import Post

    posts = Post.objects.all().order_by("-created_at")

    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "network/all_posts.html",
        {"posts": posts, "page_obj": page_obj},
    )


def profile(request, username):
    from .models import Post, User, Follow

    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse("User does not exist.")

    posts = Post.objects.filter(user=profile_user).order_by("-created_at")

    # Pagigantion
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user, following=profile_user
        ).exists()

    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    context = {
        "profile_user": profile_user,
        "posts": posts,
        "is_following": is_following,
        "followers_count": followers_count,
        "following_count": following_count,
        "page_obj": page_obj,
    }

    return render(request, "network/profile.html", context)


def follow_toggle(request, username):
    from .models import User, Follow

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse("User does not exist.")

    if request.user == target_user:
        return HttpResponse("You cannot follow yourself.")

    follow_relation = Follow.objects.filter(
        follower=request.user, following=target_user
    ).first()

    if follow_relation:
        follow_relation.delete()
    else:
        Follow.objects.create(follower=request.user, following=target_user)

    return HttpResponseRedirect(reverse("profile", args=[username]))


def following_posts(request):
    from .models import Post, User

    following = request.user.following.all()
    users = User.objects.filter(followers__in=following)
    posts = Post.objects.filter(user__in=users).order_by("-created_at")

    # Pagigantion
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request, "network/following_posts.html", {"posts": posts, "page_obj": page_obj}
    )


@csrf_exempt
@login_required
def post(request, post_id):
    from .models import Post

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(post.serialize())

    elif request.method == "PUT":
        if request.user == post.user:
            data = json.loads(request.body)
            post.content = data["content"]
            post.save()
            return HttpResponse(status=204)
        else:
            return JsonResponse({"error": "Permission denied."}, status=404)

    # Post must be via GET or PUT
    else:
        return JsonResponse({"error": "GET or PUT request required."}, status=400)

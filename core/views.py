from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    Profile, Post, Like, Comment, Follow, Message, Notification,
    Story, StoryView, StoryHighlight, Video, VideoLike, VideoComment,
    Playlist, Group, GroupMembership, GroupPost, GroupPostLike, GroupPostComment
)
from .forms import (
    UserUpdateForm, ProfileUpdateForm, PostForm, MessageForm,
    StoryForm, VideoForm, VideoCommentForm, PlaylistForm, GroupForm, GroupPostForm
)


# ========== AUTHENTICATION VIEWS ==========

def register_view(request):
    """User registration with validation"""
    if request.user.is_authenticated:
        return redirect('feed')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        terms = request.POST.get('terms')
        
        context = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        }
        
        errors = []
        
        # Validate username
        if not username:
            errors.append('Username is required')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        elif len(username) > 150:
            errors.append('Username must be less than 150 characters')
        elif not username.replace('_', '').replace('-', '').isalnum():
            errors.append('Username can only contain letters, numbers, underscores, and hyphens')
        elif User.objects.filter(username__iexact=username).exists():
            errors.append('Username already exists')
        
        # Validate email
        if not email:
            errors.append('Email is required')
        else:
            try:
                validate_email(email)
                if User.objects.filter(email__iexact=email).exists():
                    errors.append('Email is already registered')
            except ValidationError:
                errors.append('Invalid email address')
        
        # Validate password
        if not password1:
            errors.append('Password is required')
        elif len(password1) < 8:
            errors.append('Password must be at least 8 characters long')
        elif password1.isdigit():
            errors.append('Password cannot be entirely numeric')
        
        if password1 != password2:
            errors.append('Passwords do not match')
        
        if not terms:
            errors.append('You must accept the Terms of Service')
        
        # Show errors or create user
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'core/register.html', context)
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, f'Welcome to UniVerse, {username}!')
            return redirect('feed')
            
        except IntegrityError:
            messages.error(request, 'Username or email already exists')
            return render(request, 'core/register.html', context)
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'core/register.html', context)
    
    return render(request, 'core/register.html')


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('feed')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Please fill in all fields')
            return render(request, 'core/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('feed')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'core/login.html')


def logout_view(request):
    """User logout"""
    logout(request)
    return redirect('login')


# ========== FEED & PROFILE VIEWS ==========

@login_required
def feed(request):
    """Main feed with posts and stories"""
    user = request.user
    following_users = user.following.values_list('following', flat=True)
    
    posts = Post.objects.filter(
        Q(author=user) | Q(author__in=following_users)
    ).select_related('author__profile').annotate(
        like_count=Count('likes'),
        comment_count=Count('comments')
    ).order_by('-created_at')
    
    user_liked_posts = Like.objects.filter(user=user).values_list('post_id', flat=True)
    
    story_users = User.objects.filter(
        Q(id__in=following_users) | Q(id=user.id),
        stories__expires_at__gt=timezone.now()
    ).distinct().prefetch_related('stories')
    
    for story_user in story_users:
        story_user.latest_story = story_user.stories.filter(
            expires_at__gt=timezone.now()
        ).first()
    
    suggested_users = User.objects.exclude(
        Q(id=user.id) | Q(id__in=following_users)
    ).select_related('profile').annotate(
        follower_count=Count('followers')
    ).order_by('-follower_count')[:5]
    
    context = {
        'posts': posts,
        'user_liked_posts': list(user_liked_posts),
        'story_users': story_users,
        'suggested_users': suggested_users,
    }
    return render(request, 'core/feed.html', context)


def profile(request, username):
    """User profile page"""
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.all().order_by('-created_at')
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    is_following = False
    user_liked_posts = []
    
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=profile_user
        ).exists()
        user_liked_posts = Like.objects.filter(
            user=request.user
        ).values_list('post_id', flat=True)
    
    context = {
        'profile_user': profile_user,
        'profile': profile_user.profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
        'user_liked_posts': list(user_liked_posts),
    }
    return render(request, 'core/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'core/edit_profile.html', context)


# ========== POST VIEWS ==========

@login_required
def create_post(request):
    """Create a new post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('feed')
    else:
        form = PostForm()
    
    return render(request, 'core/create_post.html', {'form': form})


@login_required
def delete_post(request, post_id):
    """Delete a post"""
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        post.delete()
        messages.success(request, 'Post deleted')
    return redirect('feed')


@login_required
def like_post(request, post_id):
    """Like/unlike a post"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                actor=request.user,
                notification_type='like',
                post=post
            )
    
    return JsonResponse({
        'liked': liked,
        'like_count': post.likes.count()
    })


@login_required
def add_comment(request, post_id):
    """Add comment to post"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    post = get_object_or_404(Post, id=post_id)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
    except:
        content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Comment cannot be empty'}, status=400)
    
    comment = Comment.objects.create(
        author=request.user,
        post=post,
        content=content
    )
    
    if post.author != request.user:
        Notification.objects.create(
            user=post.author,
            actor=request.user,
            notification_type='comment',
            post=post
        )
    
    profile_pic_url = request.user.profile.profile_picture.url if request.user.profile.profile_picture else None
    
    return JsonResponse({
        'success': True,
        'comment': {
            'author_username': request.user.username,
            'author_avatar': profile_pic_url,
            'content': content,
        },
        'comment_count': post.comments.count()
    })


# ========== FOLLOW VIEWS ==========

@login_required
def follow_user(request, username):
    """Follow a user"""
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        Notification.objects.create(
            user=user_to_follow,
            actor=request.user,
            notification_type='follow'
        )
        messages.success(request, f'You are now following {username}')
    return redirect('profile', username=username)


@login_required
def unfollow_user(request, username):
    """Unfollow a user"""
    user_to_unfollow = get_object_or_404(User, username=username)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    messages.success(request, f'You unfollowed {username}')
    return redirect('profile', username=username)


# ========== MESSAGE VIEWS ==========

@login_required
def messages_list(request):
    """List all conversations"""
    user = request.user
    sent_users = Message.objects.filter(sender=user).values_list('recipient_id', flat=True).distinct()
    received_users = Message.objects.filter(recipient=user).values_list('sender_id', flat=True).distinct()
    conversation_user_ids = set(list(sent_users) + list(received_users))
    
    conversations = []
    for user_id in conversation_user_ids:
        try:
            other_user = User.objects.get(id=user_id)
            if not other_user.username:
                continue
            
            last_message = Message.objects.filter(
                Q(sender=user, recipient=other_user) | 
                Q(sender=other_user, recipient=user)
            ).order_by('-created_at').first()
            
            if last_message:
                conversations.append({
                    'other_user': other_user,
                    'last_message': last_message
                })
        except User.DoesNotExist:
            continue
    
    conversations.sort(key=lambda x: x['last_message'].created_at, reverse=True)
    
    return render(request, 'core/messages_list.html', {'conversations': conversations})


@login_required
def message_detail(request, username):
    """View conversation with a user"""
    other_user = get_object_or_404(User, username=username)
    
    messages_list = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) | 
        Q(sender=other_user, recipient=request.user)
    ).select_related('sender', 'recipient').order_by('created_at')
    
    Message.objects.filter(
        sender=other_user, 
        recipient=request.user, 
        is_read=False
    ).update(is_read=True)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                content=content
            )
            Notification.objects.create(
                user=other_user,
                actor=request.user,
                notification_type='message'
            )
            return redirect('message_detail', username=username)
    
    context = {
        'other_user': other_user,
        'messages': messages_list,
    }
    return render(request, 'core/message_detail.html', context)


# ========== NOTIFICATION VIEWS ==========

@login_required
def notifications(request):
    """View notifications"""
    user_notifications = request.user.notifications.all().order_by('-created_at')
    
    for notif in user_notifications:
        if notif.notification_type == 'like':
            notif.message = f'{notif.actor.username} liked your post'
        elif notif.notification_type == 'comment':
            notif.message = f'{notif.actor.username} commented on your post'
        elif notif.notification_type == 'follow':
            notif.message = f'{notif.actor.username} started following you'
        elif notif.notification_type == 'message':
            notif.message = f'{notif.actor.username} sent you a message'
        
        if notif.notification_type == 'follow':
            notif.link = f'/profile/{notif.actor.username}/'
        elif notif.notification_type == 'message':
            notif.link = f'/messages/{notif.actor.username}/'
        else:
            notif.link = '/'
    
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'core/notifications.html', {'notifications': user_notifications})


# ========== SEARCH VIEWS ==========

@login_required
def search_users(request):
    """Search for users"""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
    
    return render(request, 'core/search.html', {'query': query, 'results': results})


# ========== STORY VIEWS ==========

@login_required
def stories_feed(request):
    """View active stories"""
    following_users = request.user.following.values_list('following', flat=True)
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    
    story_users = User.objects.filter(
        Q(id__in=following_users) | Q(id=request.user.id),
        stories__created_at__gte=twenty_four_hours_ago
    ).distinct().prefetch_related('stories')
    
    for user in story_users:
        user.latest_story = user.stories.filter(created_at__gte=twenty_four_hours_ago).first()
        user.story_count = user.stories.filter(created_at__gte=twenty_four_hours_ago).count()
    
    return render(request, 'core/stories_feed.html', {'story_users': story_users})


@login_required
def create_story(request):
    """Create a new story"""
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            if not story.background_color or story.background_color == '#000000':
                story.background_color = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            story.save()
            messages.success(request, 'Story created!')
            return redirect('stories_feed')
    else:
        form = StoryForm()
    
    return render(request, 'core/create_story.html', {'form': form})


@login_required
def view_story(request, story_id):
    """View a story"""
    story = get_object_or_404(Story, id=story_id)
    
    if story.is_expired():
        return redirect('stories_feed')
    
    if request.user != story.author:
        StoryView.objects.get_or_create(story=story, viewer=request.user)
    
    user_stories = Story.objects.filter(
        author=story.author,
        expires_at__gt=timezone.now()
    ).order_by('created_at')
    
    context = {
        'story': story,
        'user_stories': user_stories,
        'views_count': story.views.count(),
    }
    return render(request, 'core/view_story.html', context)


@login_required
def delete_story(request, story_id):
    """Delete a story"""
    story = get_object_or_404(Story, id=story_id)
    if story.author == request.user:
        story.delete()
        messages.success(request, 'Story deleted')
    return redirect('stories_feed')


# ========== VIDEO VIEWS ==========

@login_required
def videos_feed(request):
    """Video feed"""
    videos = Video.objects.filter(is_public=True).select_related('author__profile').order_by('-created_at')
    week_ago = timezone.now() - timedelta(days=7)
    trending = Video.objects.filter(
        is_public=True,
        created_at__gte=week_ago
    ).order_by('-views')[:10]
    
    return render(request, 'core/videos_feed.html', {'videos': videos, 'trending': trending})


@login_required
def upload_video(request):
    """Upload video"""
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.author = request.user
            video.save()
            messages.success(request, 'Video uploaded!')
            return redirect('video_detail', video_id=video.id)
    else:
        form = VideoForm()
    
    return render(request, 'core/upload_video.html', {'form': form})


@login_required
def video_detail(request, video_id):
    """View video"""
    video = get_object_or_404(Video, id=video_id)
    
    if request.user != video.author:
        video.increment_views()
    
    comments = video.video_comments.filter(parent=None).select_related('author__profile')
    related = Video.objects.filter(category=video.category, is_public=True).exclude(id=video.id)[:5]
    user_liked = VideoLike.objects.filter(user=request.user, video=video).exists()
    tags_list = [tag.strip() for tag in video.tags.split(',')] if video.tags else []
    
    context = {
        'video': video,
        'comments': comments,
        'related': related,
        'user_liked': user_liked,
        'comment_form': VideoCommentForm(),
        'tags_list': tags_list,
    }
    return render(request, 'core/video_detail.html', context)


@login_required
def delete_video(request, video_id):
    """Delete video"""
    video = get_object_or_404(Video, id=video_id)
    if video.author == request.user:
        video.delete()
        messages.success(request, 'Video deleted')
    return redirect('videos_feed')


# ========== PLAYLIST VIEWS ==========

@login_required
def my_playlists(request):
    """View playlists"""
    my_playlists_list = Playlist.objects.filter(user=request.user)
    public_playlists = Playlist.objects.filter(is_public=True).exclude(user=request.user)[:10]
    
    return render(request, 'core/my_playlists.html', {
        'playlists': my_playlists_list,
        'public_playlists': public_playlists,
    })


@login_required
def create_playlist(request):
    """Create playlist"""
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            messages.success(request, 'Playlist created!')
            return redirect('playlist_detail', playlist_id=playlist.id)
    else:
        form = PlaylistForm()
    
    return render(request, 'core/create_playlist.html', {'form': form})


@login_required
def playlist_detail(request, playlist_id):
    """View playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    
    if not playlist.is_public and playlist.user != request.user:
        return HttpResponseForbidden()
    
    return render(request, 'core/playlist_detail.html', {'playlist': playlist})


@login_required
def delete_playlist(request, playlist_id):
    """Delete playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if playlist.user == request.user:
        playlist.delete()
        messages.success(request, 'Playlist deleted')
    return redirect('my_playlists')


# ========== GROUP VIEWS ==========

@login_required
def groups_list(request):
    """List groups"""
    public_groups = Group.objects.filter(privacy='public').annotate(
        member_count=Count('members')
    ).order_by('-created_at')
    my_groups = request.user.joined_groups.all()
    
    return render(request, 'core/groups_list.html', {
        'groups': public_groups,
        'my_groups': my_groups,
    })


@login_required
def create_group(request):
    """Create group"""
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            GroupMembership.objects.create(
                user=request.user,
                group=group,
                role='admin',
                status='approved'
            )
            messages.success(request, 'Group created!')
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupForm()
    
    return render(request, 'core/create_group.html', {'form': form})


@login_required
def group_detail(request, group_id):
    """View group"""
    group = get_object_or_404(Group, id=group_id)
    is_member = GroupMembership.objects.filter(
        user=request.user,
        group=group,
        status='approved'
    ).exists()
    
    if group.privacy == 'private' and not is_member:
        return HttpResponseForbidden("You must be a member to view this group")
    
    posts = group.group_posts.all().select_related('author__profile')
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    
    context = {
        'group': group,
        'posts': posts,
        'is_member': is_member,
        'membership': membership,
        'is_admin': membership.role == 'admin' if membership else False,
        'is_moderator': membership.role in ['admin', 'moderator'] if membership else False,
    }
    return render(request, 'core/group_detail.html', context)


@login_required
def join_group(request, group_id):
    """Join group"""
    group = get_object_or_404(Group, id=group_id)
    status = 'approved' if group.privacy == 'public' else 'pending'
    
    GroupMembership.objects.get_or_create(
        user=request.user,
        group=group,
        defaults={'status': status, 'role': 'member'}
    )
    messages.success(request, f'Joined {group.name}')
    return redirect('group_detail', group_id=group_id)


@login_required
def leave_group(request, group_id):
    """Leave group"""
    group = get_object_or_404(Group, id=group_id)
    
    if group.admin != request.user:
        GroupMembership.objects.filter(user=request.user, group=group).delete()
        messages.success(request, f'Left {group.name}')
    
    return redirect('groups_list')


@login_required
def delete_group(request, group_id):
    """Delete group"""
    group = get_object_or_404(Group, id=group_id)
    
    if group.admin == request.user:
        group.delete()
        messages.success(request, 'Group deleted')
    
    return redirect('groups_list')
    
    
    


# ========== MISSING STORY VIEWS ==========

@login_required
def user_stories(request, username):
    """View all active stories from a specific user"""
    user = get_object_or_404(User, username=username)
    stories = Story.objects.filter(
        author=user,
        expires_at__gt=timezone.now()
    ).order_by('created_at')
    
    context = {
        'story_user': user,
        'stories': stories,
    }
    return render(request, 'core/user_stories.html', context)


@login_required
def create_highlight(request):
    """Create a story highlight"""
    if request.method == 'POST':
        title = request.POST.get('title')
        story_ids = request.POST.getlist('stories')
        
        highlight = StoryHighlight.objects.create(
            user=request.user,
            title=title
        )
        highlight.stories.set(story_ids)
        messages.success(request, 'Highlight created!')
        return redirect('profile', username=request.user.username)
    
    old_stories = Story.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'core/create_highlight.html', {'old_stories': old_stories})


@login_required
def view_highlight(request, highlight_id):
    """View a story highlight"""
    highlight = get_object_or_404(StoryHighlight, id=highlight_id)
    
    context = {
        'highlight': highlight,
        'stories': highlight.stories.all(),
    }
    return render(request, 'core/view_highlight.html', context)


@login_required
def delete_highlight(request, highlight_id):
    """Delete a highlight"""
    highlight = get_object_or_404(StoryHighlight, id=highlight_id)
    if highlight.user == request.user:
        highlight.delete()
        messages.success(request, 'Highlight deleted')
    return redirect('profile', username=request.user.username)


# ========== MISSING VIDEO VIEWS ==========

@login_required
def edit_video(request, video_id):
    """Edit video details"""
    video = get_object_or_404(Video, id=video_id)
    
    if video.author != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video updated!')
            return redirect('video_detail', video_id=video.id)
    else:
        form = VideoForm(instance=video)
    
    context = {'form': form, 'video': video}
    return render(request, 'core/edit_video.html', context)


@login_required
def videos_by_category(request, category):
    """Filter videos by category"""
    videos = Video.objects.filter(
        category=category, 
        is_public=True
    ).order_by('-created_at')
    
    context = {
        'videos': videos,
        'category': category,
    }
    return render(request, 'core/videos_by_category.html', context)


@login_required
def search_videos(request):
    """Search for videos"""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = Video.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(tags__icontains=query),
            is_public=True
        ).order_by('-created_at')
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'core/search_videos.html', context)


@login_required
def like_video(request, video_id):
    """Like/unlike a video"""
    video = get_object_or_404(Video, id=video_id)
    like, created = VideoLike.objects.get_or_create(user=request.user, video=video)
    
    if not created:
        like.delete()
    else:
        if video.author != request.user:
            Notification.objects.create(
                user=video.author,
                actor=request.user,
                notification_type='like'
            )
    
    messages.success(request, 'Video liked!' if created else 'Like removed')
    return redirect('video_detail', video_id=video_id)


@login_required
def add_video_comment(request, video_id):
    """Add a comment to a video"""
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST' and video.allow_comments:
        form = VideoCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.video = video
            
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id
            
            comment.save()
            
            if video.author != request.user:
                Notification.objects.create(
                    user=video.author,
                    actor=request.user,
                    notification_type='comment'
                )
            
            messages.success(request, 'Comment added!')
    
    return redirect('video_detail', video_id=video_id)


# ========== MISSING PLAYLIST VIEWS ==========

@login_required
def edit_playlist(request, playlist_id):
    """Edit playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    
    if playlist.user != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = PlaylistForm(request.POST, instance=playlist)
        if form.is_valid():
            form.save()
            messages.success(request, 'Playlist updated!')
            return redirect('playlist_detail', playlist_id=playlist.id)
    else:
        form = PlaylistForm(instance=playlist)
    
    context = {'form': form, 'playlist': playlist}
    return render(request, 'core/edit_playlist.html', context)


@login_required
def add_to_playlist(request, playlist_id, video_id):
    """Add video to playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    video = get_object_or_404(Video, id=video_id)
    
    if playlist.user == request.user:
        if video not in playlist.videos.all():
            playlist.videos.add(video)
            messages.success(request, f'Added to {playlist.title}')
        else:
            messages.info(request, 'Video already in playlist')
    
    return redirect('video_detail', video_id=video_id)


@login_required
def remove_from_playlist(request, playlist_id, video_id):
    """Remove video from playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    video = get_object_or_404(Video, id=video_id)
    
    if playlist.user == request.user:
        playlist.videos.remove(video)
        messages.success(request, f'Removed from {playlist.title}')
    
    return redirect('playlist_detail', playlist_id=playlist_id)


# ========== MISSING GROUP VIEWS ==========

@login_required
def edit_group(request, group_id):
    """Edit group details"""
    group = get_object_or_404(Group, id=group_id)
    
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    if not membership or membership.role != 'admin':
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated!')
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupForm(instance=group)
    
    context = {'form': form, 'group': group}
    return render(request, 'core/edit_group.html', context)


@login_required
def create_group_post(request, group_id):
    """Create a post in a group"""
    group = get_object_or_404(Group, id=group_id)
    
    is_member = GroupMembership.objects.filter(
        user=request.user,
        group=group,
        status='approved'
    ).exists()
    
    if not is_member:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = GroupPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.group = group
            post.save()
            messages.success(request, 'Post created!')
            return redirect('group_detail', group_id=group_id)
    else:
        form = GroupPostForm()
    
    context = {'form': form, 'group': group}
    return render(request, 'core/create_group_post.html', context)


@login_required
def delete_group_post(request, post_id):
    """Delete a group post"""
    post = get_object_or_404(GroupPost, id=post_id)
    group_id = post.group.id
    
    membership = GroupMembership.objects.filter(user=request.user, group=post.group).first()
    
    if post.author == request.user or (membership and membership.role in ['admin', 'moderator']):
        post.delete()
        messages.success(request, 'Post deleted')
    
    return redirect('group_detail', group_id=group_id)


@login_required
def like_group_post(request, post_id):
    """Like/unlike a group post"""
    post = get_object_or_404(GroupPost, id=post_id)
    like, created = GroupPostLike.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
    
    return redirect('group_detail', group_id=post.group.id)


@login_required
def add_group_comment(request, post_id):
    """Add comment to group post"""
    post = get_object_or_404(GroupPost, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            GroupPostComment.objects.create(
                author=request.user,
                post=post,
                content=content
            )
            messages.success(request, 'Comment added!')
    
    return redirect('group_detail', group_id=post.group.id)


@login_required
def group_members(request, group_id):
    """View group members"""
    group = get_object_or_404(Group, id=group_id)
    
    is_member = GroupMembership.objects.filter(
        user=request.user,
        group=group,
        status='approved'
    ).exists()
    
    if group.privacy != 'public' and not is_member:
        return HttpResponseForbidden()
    
    members = group.groupmembership_set.filter(status='approved').select_related('user__profile')
    user_membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    
    context = {
        'group': group,
        'members': members,
        'is_admin': user_membership.role == 'admin' if user_membership else False,
        'is_moderator': user_membership.role in ['admin', 'moderator'] if user_membership else False,
    }
    return render(request, 'core/group_members.html', context)


@login_required
def remove_group_member(request, group_id, user_id):
    """Remove a member from group (admin/moderator only)"""
    group = get_object_or_404(Group, id=group_id)
    user_to_remove = get_object_or_404(User, id=user_id)
    
    requester_membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    
    if not requester_membership or requester_membership.role not in ['admin', 'moderator']:
        return HttpResponseForbidden()
    
    if user_to_remove != group.admin:
        GroupMembership.objects.filter(user=user_to_remove, group=group).delete()
        messages.success(request, f'Removed {user_to_remove.username} from group')
    
    return redirect('group_members', group_id=group_id)


@login_required
def make_moderator(request, group_id, user_id):
    """Make a member a moderator (admin only)"""
    group = get_object_or_404(Group, id=group_id)
    user = get_object_or_404(User, id=user_id)
    
    if request.user != group.admin:
        return HttpResponseForbidden()
    
    membership = GroupMembership.objects.filter(user=user, group=group).first()
    if membership:
        membership.role = 'moderator'
        membership.save()
        group.moderators.add(user)
        messages.success(request, f'{user.username} is now a moderator')
    
    return redirect('group_members', group_id=group_id)
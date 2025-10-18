from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import (
    Profile, Post, Like, Comment, Follow, Message, Notification,
    Story, StoryView, StoryHighlight, Video, VideoLike, VideoComment,
    Playlist, Group, GroupMembership, GroupPost, GroupPostLike, GroupPostComment
)
from .forms import (
    UserCreationForm, UserUpdateForm, ProfileUpdateForm, PostForm, CommentForm, MessageForm,
    StoryForm, VideoForm, VideoCommentForm, PlaylistForm, GroupForm, GroupPostForm
)
import json


@login_required
def feed(request):
    user = request.user
    following_users = user.following.values_list('following', flat=True)
    
    # Get posts
    posts = Post.objects.filter(
        Q(author=user) | Q(author__in=following_users)
    ).select_related('author', 'author__profile').annotate(
        like_count=Count('likes'),
        comment_count=Count('comments')
    ).order_by('-created_at')
    
    # Get liked posts
    user_liked_posts = Like.objects.filter(user=user).values_list('post_id', flat=True)
    
    # Get active stories
    story_users = User.objects.filter(
        Q(id__in=following_users) | Q(id=user.id),
        stories__expires_at__gt=timezone.now()
    ).distinct().prefetch_related('stories')
    
    # Attach latest story to each user
    for story_user in story_users:
        story_user.latest_story = story_user.stories.filter(
            expires_at__gt=timezone.now()
        ).first()
    
    # Get suggested users (users not followed by current user)
    suggested_users = User.objects.exclude(
        Q(id=user.id) | Q(id__in=following_users)
    ).select_related('profile').annotate(
        follower_count=Count('followers')
    ).order_by('-follower_count')[:5]

    # If no suggestions, just show any active users
    if not suggested_users.exists():
        suggested_users = User.objects.exclude(
            id=user.id
        ).select_related('profile').order_by('-date_joined')[:5]
        
    context = {
        'posts': posts,
        'user_liked_posts': list(user_liked_posts),
        'story_users': story_users,
        'suggested_users': suggested_users,
    }
    return render(request, 'core/feed.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('feed')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('feed')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid credentials'})
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    posts = user.posts.all().order_by('-created_at')
    followers_count = user.followers.count()
    following_count = user.following.count()
    is_following = False
    
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    user_liked_posts = []
    if request.user.is_authenticated:
        user_liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)

    
    context = {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
        'user_liked_posts': list(user_liked_posts),
    }
    return render(request, 'core/profile.html', context)

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'core/edit_profile.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'core/create_post.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        post.delete()
    return redirect('feed')

@login_required
def like_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        # Create notification
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
    
    # Create notification
    if post.author != request.user:
        Notification.objects.create(
            user=post.author,
            actor=request.user,
            notification_type='comment',
            post=post
        )
    
    # Get profile picture URL
    profile_pic_url = None
    if request.user.profile.profile_picture:
        profile_pic_url = request.user.profile.profile_picture.url
    
    return JsonResponse({
        'success': True,
        'comment': {
            'author_username': request.user.username,
            'author_avatar': profile_pic_url,
            'content': content,
        },
        'comment_count': post.comments.count()
    })


@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        
        # Create notification
        Notification.objects.create(
            user=user_to_follow,
            actor=request.user,
            notification_type='follow'
        )
    
    return redirect('profile', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect('profile', username=username)

@login_required
def messages_list(request):
    user = request.user
    
    # Get all unique users the current user has messaged with
    sent_users = Message.objects.filter(sender=user).values_list('recipient_id', flat=True).distinct()
    received_users = Message.objects.filter(recipient=user).values_list('sender_id', flat=True).distinct()
    
    # Combine and get unique user IDs
    conversation_user_ids = set(list(sent_users) + list(received_users))
    
    # Build conversations with last message
    conversations = []
    
    for user_id in conversation_user_ids:
        try:
            other_user = User.objects.get(id=user_id)
            
            # Skip if the user doesn't have a username (safety check)
            if not other_user.username:
                continue
            
            # Get last message between current user and this other user
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
            # Skip if user doesn't exist
            continue
    
    # Sort by most recent message first
    conversations.sort(key=lambda x: x['last_message'].created_at, reverse=True)
    
    context = {
        'conversations': conversations
    }
    
    return render(request, 'core/messages_list.html', context)

@login_required
def message_detail(request, username):
    """View conversation with a specific user"""
    other_user = get_object_or_404(User, username=username)
    
    # Get all messages between the two users
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) | 
        Q(sender=other_user, recipient=request.user)
    ).select_related('sender', 'recipient').order_by('created_at')
    
    # Mark messages as read
    Message.objects.filter(
        sender=other_user, 
        recipient=request.user, 
        is_read=False
    ).update(is_read=True)
    
    # Get all conversations for sidebar
    sent_messages = Message.objects.filter(sender=request.user).values('recipient').distinct()
    received_messages = Message.objects.filter(recipient=request.user).values('sender').distinct()
    
    # Get unique user IDs
    user_ids = set()
    for msg in sent_messages:
        user_ids.add(msg['recipient'])
    for msg in received_messages:
        user_ids.add(msg['sender'])
    
    # Build conversations list
    conversations = []
    for user_id in user_ids:
        conv_user = User.objects.get(id=user_id)
        last_message = Message.objects.filter(
            Q(sender=request.user, recipient=conv_user) | 
            Q(sender=conv_user, recipient=request.user)
        ).order_by('-created_at').first()
        
        if last_message:
            conversations.append({
                'other_user': conv_user,
                'last_message': last_message,
                'is_active': conv_user.id == other_user.id
            })
    
    # Sort by most recent
    conversations.sort(key=lambda x: x['last_message'].created_at, reverse=True)
    
    # Handle message sending
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                content=content
            )
            # Create notification
            Notification.objects.create(
                user=other_user,
                actor=request.user,
                notification_type='message'
            )
            return redirect('message_detail', username=username)
    
    context = {
        'other_user': other_user,
        'messages': messages,
        'conversations': conversations,
    }
    return render(request, 'core/message_detail.html', context)

@login_required
def send_message(request, username):
    recipient = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            
            # Create notification
            Notification.objects.create(
                user=recipient,
                actor=request.user,
                notification_type='message'
            )
    
    return redirect('message_detail', username=username)

def get_notification_message(notification):
    """Generate notification message"""
    messages = {
        'like': f'<strong>{notification.actor.username}</strong> liked your post',
        'comment': f'<strong>{notification.actor.username}</strong> commented on your post',
        'follow': f'<strong>{notification.actor.username}</strong> started following you',
        'message': f'<strong>{notification.actor.username}</strong> sent you a message',
    }
    return messages.get(notification.notification_type, 'New notification')

@login_required
def notifications(request):
    # Change variable name from 'notifications' to 'user_notifications'
    user_notifications = request.user.notifications.all().order_by('-created_at')
    
    # Generate messages for notifications
    notifications_list = []
    for notif in user_notifications:
        # Generate message
        if notif.notification_type == 'like':
            notif.message = f'<strong>{notif.actor.username}</strong> liked your post'
        elif notif.notification_type == 'comment':
            notif.message = f'<strong>{notif.actor.username}</strong> commented on your post'
        elif notif.notification_type == 'follow':
            notif.message = f'<strong>{notif.actor.username}</strong> started following you'
        elif notif.notification_type == 'message':
            notif.message = f'<strong>{notif.actor.username}</strong> sent you a message'
        else:
            notif.message = 'New notification'
        
        # Generate link
        if notif.notification_type == 'follow':
            notif.link = f'/profile/{notif.actor.username}/'
        elif notif.notification_type == 'message':
            notif.link = f'/messages/{notif.actor.username}/'
        elif notif.post:
            notif.link = f'/'  # or detail page if you have one
        else:
            notif.link = '/'
        
        notifications_list.append(notif)
    
    # Mark as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications_list,
    }
    return render(request, 'core/notifications.html', context)
    
@login_required
def search_users(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).exclude(id=request.user.id)
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'core/search.html', context)

# Replace the entire stories_feed function with:
@login_required
def stories_feed(request):
    following_users = request.user.following.values_list('following', flat=True)
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    
    # Get users with active stories
    story_users = User.objects.filter(
        Q(id__in=following_users) | Q(id=request.user.id),
        stories__created_at__gte=twenty_four_hours_ago
    ).distinct().prefetch_related('stories')
    
    # Attach latest story to each user
    for user in story_users:
        user.latest_story = user.stories.filter(created_at__gte=twenty_four_hours_ago).first()
        user.story_count = user.stories.filter(created_at__gte=twenty_four_hours_ago).count()
    
    context = {
        'story_users': story_users,
    }
    return render(request, 'core/stories_feed.html', context)


@login_required
def create_story(request):
    """Create a new story"""
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug
        print("FILES:", request.FILES)  # Debug
        
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            
            # Set default background color if not provided
            if not story.background_color or story.background_color == '#000000':
                story.background_color = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            
            # expires_at will be set automatically in save() method
            story.save()
            print("Story created successfully!")  # Debug
            return redirect('stories_feed')
        else:
            print("Form errors:", form.errors)  # Debug
            # Return with errors
            context = {
                'form': form,
                'errors': form.errors
            }
            return render(request, 'core/create_story.html', context)
    else:
        form = StoryForm()
    
    context = {'form': form}
    return render(request, 'core/create_story.html', context)

@login_required
def view_story(request, story_id):
    """View a specific story and mark as viewed"""
    story = get_object_or_404(Story, id=story_id)
    
    if story.is_expired():
        return redirect('stories_feed')
    
    # Record view if not the author
    if request.user != story.author:
        StoryView.objects.get_or_create(story=story, viewer=request.user)
    
    # Get all stories from this user
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
def delete_story(request, story_id):
    """Delete a story"""
    story = get_object_or_404(Story, id=story_id)
    if story.author == request.user:
        story.delete()
    return redirect('stories_feed')


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
        return redirect('profile', username=request.user.username)
    
    # Get user's expired stories that can be added to highlights
    old_stories = Story.objects.filter(author=request.user).order_by('-created_at')
    
    context = {'old_stories': old_stories}
    return render(request, 'core/create_highlight.html', context)


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
    return redirect('profile', username=request.user.username)


# ========== VIDEO VIEWS ==========

@login_required
def videos_feed(request):
    """Display video feed"""
    videos = Video.objects.filter(is_public=True).select_related('author__profile').order_by('-created_at')
    
    # Get trending videos (most views in last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    trending = Video.objects.filter(
        is_public=True,
        created_at__gte=week_ago
    ).order_by('-views')[:10]
    
    context = {
        'videos': videos,
        'trending': trending,
    }
    return render(request, 'core/videos_feed.html', context)


@login_required
def upload_video(request):
    """Upload a new video"""
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.author = request.user
            video.save()
            return redirect('video_detail', video_id=video.id)
    else:
        form = VideoForm()
    
    context = {'form': form}
    return render(request, 'core/upload_video.html', context)


@login_required
def video_detail(request, video_id):
    """View video details and increment views"""
    video = get_object_or_404(Video, id=video_id)
    
    # Increment views
    if request.user != video.author:
        video.increment_views()
    
    # Get comments
    comments = video.video_comments.filter(parent=None).select_related('author__profile')
    
    # Get related videos
    related = Video.objects.filter(
        category=video.category,
        is_public=True
    ).exclude(id=video.id)[:5]
    
    # Check if user liked
    user_liked = VideoLike.objects.filter(user=request.user, video=video).exists()
    
    # Process tags
    tags_list = [tag.strip() for tag in video.tags.split(',')] if video.tags else []
    
    context = {
        'video': video,
        'comments': comments,
        'related': related,
        'user_liked': user_liked,
        'comment_form': VideoCommentForm(),
        'tags_list': tags_list,  # Add this
    }
    return render(request, 'core/video_detail.html', context)

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
            return redirect('video_detail', video_id=video.id)
    else:
        form = VideoForm(instance=video)
    
    context = {'form': form, 'video': video}
    return render(request, 'core/edit_video.html', context)


@login_required
def delete_video(request, video_id):
    """Delete a video"""
    video = get_object_or_404(Video, id=video_id)
    if video.author == request.user:
        video.delete()
    return redirect('videos_feed')


@login_required
def like_video(request, video_id):
    """Like/unlike a video"""
    video = get_object_or_404(Video, id=video_id)
    like, created = VideoLike.objects.get_or_create(user=request.user, video=video)
    
    if not created:
        like.delete()
    else:
        # Create notification
        if video.author != request.user:
            Notification.objects.create(
                user=video.author,
                actor=request.user,
                notification_type='like'
            )
    
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
            
            # Check for parent comment (replies)
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id
            
            comment.save()
            
            # Create notification
            if video.author != request.user:
                Notification.objects.create(
                    user=video.author,
                    actor=request.user,
                    notification_type='comment'
                )
    
    return redirect('video_detail', video_id=video_id)


@login_required
def videos_by_category(request, category):
    """Filter videos by category"""
    videos = Video.objects.filter(category=category, is_public=True).order_by('-created_at')
    
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


# ========== PLAYLIST VIEWS ==========

@login_required
def my_playlists(request):
    """View user's playlists"""
    # Get user's own playlists
    my_playlists = Playlist.objects.filter(user=request.user)
    
    # Get public playlists from others
    public_playlists = Playlist.objects.filter(
        is_public=True
    ).exclude(user=request.user).select_related('user')[:10]
    
    context = {
        'playlists': my_playlists,
        'public_playlists': public_playlists,
    }
    return render(request, 'core/my_playlists.html', context)

@login_required
def create_playlist(request):
    """Create a new playlist"""
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            return redirect('playlist_detail', playlist_id=playlist.id)
        else:
            print("Form errors:", form.errors)  # Debug
    else:
        form = PlaylistForm()
    
    context = {'form': form}
    return render(request, 'core/create_playlist.html', context)

@login_required
def add_to_playlist(request, playlist_id, video_id):
    """Add video to playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    video = get_object_or_404(Video, id=video_id)
    
    if playlist.user == request.user:
        if video not in playlist.videos.all():
            playlist.videos.add(video)
            # You can add a success message here if you have messages framework
        
    # Redirect back to the video page
    return redirect('video_detail', video_id=video_id)


@login_required
def remove_from_playlist(request, playlist_id, video_id):
    """Remove video from playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    video = get_object_or_404(Video, id=video_id)
    
    if playlist.user == request.user:
        playlist.videos.remove(video)
    
    return redirect('playlist_detail', playlist_id=playlist_id)
    
    
@login_required
def playlist_detail(request, playlist_id):
    """View playlist details"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    
    # Check permissions
    if not playlist.is_public and playlist.user != request.user:
        return HttpResponseForbidden()
    
    context = {'playlist': playlist}
    return render(request, 'core/playlist_detail.html', context)


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
            return redirect('playlist_detail', playlist_id=playlist.id)
    else:
        form = PlaylistForm(instance=playlist)
    
    context = {'form': form, 'playlist': playlist}
    return render(request, 'core/edit_playlist.html', context)


@login_required
def delete_playlist(request, playlist_id):
    """Delete playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if playlist.user == request.user:
        playlist.delete()
    return redirect('my_playlists')


@login_required
def add_to_playlist(request, playlist_id, video_id):
    """Add video to playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    video = get_object_or_404(Video, id=video_id)
    
    if playlist.user == request.user:
        playlist.videos.add(video)
    
    return redirect('playlist_detail', playlist_id=playlist_id)


@login_required
def remove_from_playlist(request, playlist_id, video_id):
    """Remove video from playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    video = get_object_or_404(Video, id=video_id)
    
    if playlist.user == request.user:
        playlist.videos.remove(video)
    
    return redirect('playlist_detail', playlist_id=playlist_id)


# ========== GROUP VIEWS ==========

@login_required
def groups_list(request):
    """List all groups"""
    # Public groups
    public_groups = Group.objects.filter(privacy='public').annotate(
        member_count=Count('members')
    ).order_by('-created_at')
    
    # User's groups
    my_groups = request.user.joined_groups.all()
    
    context = {
        'groups': public_groups,
        'my_groups': my_groups,
    }
    return render(request, 'core/groups_list.html', context)


@login_required
def create_group(request):
    """Create a new group"""
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            
            # Add creator as member
            GroupMembership.objects.create(
                user=request.user,
                group=group,
                role='admin',
                status='approved'
            )
            
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupForm()
    
    context = {'form': form}
    return render(request, 'core/create_group.html', context)


@login_required
def group_detail(request, group_id):
    """View group details and posts"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check permissions
    is_member = GroupMembership.objects.filter(
        user=request.user,
        group=group,
        status='approved'
    ).exists()
    
    if group.privacy == 'private' and not is_member:
        return HttpResponseForbidden("You must be a member to view this group.")
    
    # Get posts
    posts = group.group_posts.all().select_related('author__profile')
    
    # Get membership
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
def edit_group(request, group_id):
    """Edit group details"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check permissions
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    if not membership or membership.role != 'admin':
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupForm(instance=group)
    
    context = {'form': form, 'group': group}
    return render(request, 'core/edit_group.html', context)


@login_required
def delete_group(request, group_id):
    """Delete a group"""
    group = get_object_or_404(Group, id=group_id)
    
    if group.admin == request.user:
        group.delete()
    
    return redirect('groups_list')


@login_required
def join_group(request, group_id):
    """Join a group"""
    group = get_object_or_404(Group, id=group_id)
    
    # Determine status based on privacy
    status = 'approved' if group.privacy == 'public' else 'pending'
    
    GroupMembership.objects.get_or_create(
        user=request.user,
        group=group,
        defaults={'status': status, 'role': 'member'}
    )
    
    # Notify admin if private
    if group.privacy == 'private':
        Notification.objects.create(
            user=group.admin,
            actor=request.user,
            notification_type='follow'  # Reusing notification type
        )
    
    return redirect('group_detail', group_id=group_id)


@login_required
def leave_group(request, group_id):
    """Leave a group"""
    group = get_object_or_404(Group, id=group_id)
    
    # Can't leave if you're the admin
    if group.admin != request.user:
        GroupMembership.objects.filter(user=request.user, group=group).delete()
    
    return redirect('groups_list')


@login_required
def create_group_post(request, group_id):
    """Create a post in a group"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check membership
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
    
    # Check permissions (author or group moderator/admin)
    membership = GroupMembership.objects.filter(user=request.user, group=post.group).first()
    
    if post.author == request.user or (membership and membership.role in ['admin', 'moderator']):
        post.delete()
    
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
    
    return redirect('group_detail', group_id=post.group.id)


@login_required
def group_members(request, group_id):
    """View group members"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user can view members
    is_member = GroupMembership.objects.filter(
        user=request.user,
        group=group,
        status='approved'
    ).exists()
    
    if group.privacy != 'public' and not is_member:
        return HttpResponseForbidden()
    
    members = group.groupmembership_set.filter(status='approved').select_related('user__profile')
    
    # Get user's membership to check permissions
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
    
    # Check permissions
    requester_membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    
    if not requester_membership or requester_membership.role not in ['admin', 'moderator']:
        return HttpResponseForbidden()
    
    # Can't remove admin
    if user_to_remove != group.admin:
        GroupMembership.objects.filter(user=user_to_remove, group=group).delete()
    
    return redirect('group_members', group_id=group_id)


@login_required
def make_moderator(request, group_id, user_id):
    """Make a member a moderator (admin only)"""
    group = get_object_or_404(Group, id=group_id)
    user = get_object_or_404(User, id=user_id)
    
    # Check permissions
    if request.user != group.admin:
        return HttpResponseForbidden()
    
    membership = GroupMembership.objects.filter(user=user, group=group).first()
    if membership:
        membership.role = 'moderator'
        membership.save()
        group.moderators.add(user)
    
    return redirect('group_members', group_id=group_id)

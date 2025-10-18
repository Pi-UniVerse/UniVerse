from django.urls import path
from . import views

# Try to import AI views, but don't fail if not available
try:
    from . import views_ai
    AI_VIEWS_AVAILABLE = True
except ImportError:
    AI_VIEWS_AVAILABLE = False

urlpatterns = [
    # ========== AUTHENTICATION ==========
    path('', views.feed, name='feed'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ========== PROFILE ==========
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    
    # ========== POSTS ==========
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    
    # ========== FOLLOW ==========
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    
    # ========== MESSAGES ==========
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/<str:username>/', views.message_detail, name='message_detail'),
    
    # ========== NOTIFICATIONS ==========
    path('notifications/', views.notifications, name='notifications'),
    
    # ========== SEARCH ==========
    path('search/', views.search_users, name='search_users'),
    
    # ========== STORIES ==========
    path('stories/', views.stories_feed, name='stories_feed'),
    path('story/create/', views.create_story, name='create_story'),
    path('story/<int:story_id>/', views.view_story, name='view_story'),
    path('story/<int:story_id>/delete/', views.delete_story, name='delete_story'),
    path('stories/<str:username>/', views.user_stories, name='user_stories'),
    
    # ========== STORY HIGHLIGHTS ==========
    path('highlights/create/', views.create_highlight, name='create_highlight'),
    path('highlight/<int:highlight_id>/', views.view_highlight, name='view_highlight'),
    path('highlight/<int:highlight_id>/delete/', views.delete_highlight, name='delete_highlight'),
    
    # ========== VIDEOS ==========
    path('videos/', views.videos_feed, name='videos_feed'),
    path('video/upload/', views.upload_video, name='upload_video'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('video/<int:video_id>/edit/', views.edit_video, name='edit_video'),
    path('video/<int:video_id>/delete/', views.delete_video, name='delete_video'),
    path('video/<int:video_id>/like/', views.like_video, name='like_video'),
    path('video/<int:video_id>/comment/', views.add_video_comment, name='add_video_comment'),
    path('videos/category/<str:category>/', views.videos_by_category, name='videos_by_category'),
    path('videos/search/', views.search_videos, name='search_videos'),
    
    # ========== PLAYLISTS ==========
    path('playlists/', views.my_playlists, name='my_playlists'),
    path('playlist/create/', views.create_playlist, name='create_playlist'),
    path('playlist/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('playlist/<int:playlist_id>/edit/', views.edit_playlist, name='edit_playlist'),
    path('playlist/<int:playlist_id>/delete/', views.delete_playlist, name='delete_playlist'),
    path('playlist/<int:playlist_id>/add/<int:video_id>/', views.add_to_playlist, name='add_to_playlist'),
    path('playlist/<int:playlist_id>/remove/<int:video_id>/', views.remove_from_playlist, name='remove_from_playlist'),
    
    # ========== GROUPS ==========
    path('groups/', views.groups_list, name='groups_list'),
    path('group/create/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/edit/', views.edit_group, name='edit_group'),
    path('group/<int:group_id>/delete/', views.delete_group, name='delete_group'),
    path('group/<int:group_id>/join/', views.join_group, name='join_group'),
    path('group/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('group/<int:group_id>/post/', views.create_group_post, name='create_group_post'),
    path('group/post/<int:post_id>/delete/', views.delete_group_post, name='delete_group_post'),
    path('group/post/<int:post_id>/like/', views.like_group_post, name='like_group_post'),
    path('group/post/<int:post_id>/comment/', views.add_group_comment, name='add_group_comment'),
    path('group/<int:group_id>/members/', views.group_members, name='group_members'),
    path('group/<int:group_id>/member/<int:user_id>/remove/', views.remove_group_member, name='remove_group_member'),
    path('group/<int:group_id>/member/<int:user_id>/make-moderator/', views.make_moderator, name='make_moderator'),
]

# Add AI URLs if available
if AI_VIEWS_AVAILABLE:
    urlpatterns += [
        path('ai/translate/', views_ai.translate_post, name='translate_post'),
        path('ai/suggestions/', views_ai.ai_suggestions, name='ai_suggestions'),
        path('ai/translate/', views_ai.translate_post, name='translate_post'),
        path('ai/suggestions/', views_ai.ai_suggestions, name='ai_suggestions'),
        path('ai/analyze-image/', views_ai.analyze_image, name='analyze_image'),  # Add this
    ]

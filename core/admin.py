from django.contrib import admin
from .models import (
    Profile, Follow, Post, Like, Comment, Message, Notification,
    Story, StoryView, StoryHighlight, Video, VideoLike, VideoComment, 
    Playlist, Group, GroupMembership, GroupPost, GroupPostLike, GroupPostComment
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at')
    search_fields = ('user__username', 'location')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at', 'like_count', 'comment_count')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__id')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    search_fields = ('author__username', 'content')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username')
    list_filter = ('is_read', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'actor', 'notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'actor__username')
    list_filter = ('notification_type', 'is_read', 'created_at')

# ==================== NEW ADMIN CLASSES ====================

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at', 'expires_at', 'is_expired')
    search_fields = ('author__username', 'caption')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'expires_at')

@admin.register(StoryView)
class StoryViewAdmin(admin.ModelAdmin):
    list_display = ('story', 'viewer', 'viewed_at')
    search_fields = ('story__author__username', 'viewer__username')
    list_filter = ('viewed_at',)

@admin.register(StoryHighlight)
class StoryHighlightAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')
    search_fields = ('user__username', 'title')
    filter_horizontal = ('stories',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'views', 'is_public', 'created_at')
    search_fields = ('title', 'author__username', 'tags')
    list_filter = ('category', 'is_public', 'created_at')
    readonly_fields = ('views', 'created_at', 'updated_at')

@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')
    search_fields = ('user__username', 'video__title')

@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'video', 'created_at')
    search_fields = ('author__username', 'content', 'video__title')
    list_filter = ('created_at',)

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_public', 'created_at')
    search_fields = ('title', 'user__username')
    list_filter = ('is_public', 'created_at')
    filter_horizontal = ('videos',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'privacy', 'member_count', 'created_at')
    search_fields = ('name', 'admin__username', 'description')
    list_filter = ('privacy', 'created_at')
    filter_horizontal = ('moderators',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'status', 'joined_at')
    search_fields = ('user__username', 'group__name')
    list_filter = ('role', 'status', 'joined_at')

@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    list_display = ('author', 'group', 'is_pinned', 'created_at')
    search_fields = ('author__username', 'group__name', 'content')
    list_filter = ('is_pinned', 'created_at')

@admin.register(GroupPostLike)
class GroupPostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username',)

@admin.register(GroupPostComment)
class GroupPostCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    search_fields = ('author__username', 'content')
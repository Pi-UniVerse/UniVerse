from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from .models import (
    Profile, Post, Comment, Message, 
    Story, Video, VideoComment, Group, GroupPost, Playlist  # Add VideoComment here
)

class UserCreationForm(DjangoUserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture', 'cover_image', 'location', 'website', 'birth_date')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content', 'image')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': "What's on your mind?"}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Add a comment...'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your message...'}),
        }

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ('image', 'video', 'caption', 'duration', 'background_color')
        widgets = {
            'caption': forms.Textarea(attrs={'placeholder': 'Add a caption...', 'maxlength': '200', 'rows': 3}),
            'duration': forms.NumberInput(attrs={'min': '3', 'max': '15', 'value': '5'}),
            'background_color': forms.HiddenInput(),  # Changed to HiddenInput
        }
    
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        caption = cleaned_data.get('caption')
        
        # Text-only stories need caption
        if not image and not video:
            if not caption or not caption.strip():
                raise forms.ValidationError("Please upload an image/video or add text for your story.")
        
        # Don't allow both image and video
        if image and video:
            raise forms.ValidationError("Please upload only one: either image or video.")
        
        return cleaned_data

# Video Forms
class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'description', 'video_file', 'thumbnail', 'category', 'tags', 'is_public', 'allow_comments')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter video title...'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your video...'}),
            'tags': forms.TextInput(attrs={'placeholder': 'gaming, tutorial, vlog (comma-separated)'}),
        }

class VideoCommentForm(forms.ModelForm):
    class Meta:
        model = VideoComment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a comment...'}),
        }

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ('title', 'description', 'is_public')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Playlist name...'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your playlist...'}),
        }

# Group Forms
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'description', 'cover_image', 'privacy', 'rules', 'category')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter group name...'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What is this group about?'}),
            'rules': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Group rules (optional)...'}),
            'category': forms.TextInput(attrs={'placeholder': 'e.g., Technology, Gaming, Music...'}),
        }

class GroupPostForm(forms.ModelForm):
    class Meta:
        model = GroupPost
        fields = ('content', 'image')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share something with the group...'}),
        }
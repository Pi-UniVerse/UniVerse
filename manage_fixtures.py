"""
Script to create sample data fixtures for the social media app.
Run this after migrations: python manage_fixtures.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Post, Follow, Like, Comment, Message, Notification

def create_sample_data():
    """Create sample users, posts, and interactions"""
    
    # Clear existing data
    User.objects.all().delete()
    
    # Create sample users
    users_data = [
        {'username': 'alice', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Johnson'},
        {'username': 'bob', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Smith'},
        {'username': 'charlie', 'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Brown'},
        {'username': 'diana', 'email': 'diana@example.com', 'first_name': 'Diana', 'last_name': 'Prince'},
        {'username': 'eve', 'email': 'eve@example.com', 'first_name': 'Eve', 'last_name': 'Wilson'},
    ]
    
    users = []
    for user_data in users_data:
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password='testpass123'
        )
        users.append(user)
        
        # Update profile
        profile = user.profile
        profile.bio = f"Hi, I'm {user_data['first_name']}! Welcome to my profile."
        profile.location = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'][users.index(user)]
        profile.website = f"https://{user_data['username']}.example.com"
        profile.save()
    
    # Create follow relationships
    Follow.objects.create(follower=users[0], following=users[1])  # Alice follows Bob
    Follow.objects.create(follower=users[0], following=users[2])  # Alice follows Charlie
    Follow.objects.create(follower=users[1], following=users[0])  # Bob follows Alice
    Follow.objects.create(follower=users[2], following=users[0])  # Charlie follows Alice
    Follow.objects.create(follower=users[3], following=users[0])  # Diana follows Alice
    Follow.objects.create(follower=users[4], following=users[1])  # Eve follows Bob
    
    # Create sample posts
    posts_data = [
        {'author': users[0], 'content': 'Just finished an amazing project! Feeling accomplished 🎉'},
        {'author': users[0], 'content': 'Beautiful sunset today! Nature is amazing.'},
        {'author': users[1], 'content': 'Coffee and code - the perfect combination ☕'},
        {'author': users[1], 'content': 'Anyone else love working on side projects?'},
        {'author': users[2], 'content': 'Learning Django has been so much fun!'},
        {'author': users[3], 'content': 'Just launched my new website! Check it out.'},
        {'author': users[4], 'content': 'Web development is my passion 💻'},
    ]
    
    posts = []
    for post_data in posts_data:
        post = Post.objects.create(
            author=post_data['author'],
            content=post_data['content']
        )
        posts.append(post)
    
    # Create likes
    Like.objects.create(user=users[1], post=posts[0])  # Bob likes Alice's post
    Like.objects.create(user=users[2], post=posts[0])  # Charlie likes Alice's post
    Like.objects.create(user=users[0], post=posts[2])  # Alice likes Bob's post
    Like.objects.create(user=users[3], post=posts[1])  # Diana likes Alice's post
    Like.objects.create(user=users[0], post=posts[4])  # Alice likes Charlie's post
    
    # Create comments
    Comment.objects.create(
        author=users[1],
        post=posts[0],
        content='Congratulations! That looks amazing!'
    )
    Comment.objects.create(
        author=users[2],
        post=posts[0],
        content='Great work, Alice!'
    )
    Comment.objects.create(
        author=users[0],
        post=posts[2],
        content='Coffee is life! ☕'
    )
    Comment.objects.create(
        author=users[3],
        post=posts[1],
        content='Beautiful! Where was this taken?'
    )
    
    # Create messages
    Message.objects.create(
        sender=users[0],
        recipient=users[1],
        content='Hey Bob! How are you doing?'
    )
    Message.objects.create(
        sender=users[1],
        recipient=users[0],
        content='Hi Alice! I\'m doing great, thanks for asking!'
    )
    Message.objects.create(
        sender=users[0],
        recipient=users[1],
        content='Want to collaborate on a project?'
    )
    
    print("✓ Sample data created successfully!")
    print(f"✓ Created {len(users)} users")
    print(f"✓ Created {len(posts)} posts")
    print(f"✓ Created {Like.objects.count()} likes")
    print(f"✓ Created {Comment.objects.count()} comments")
    print(f"✓ Created {Message.objects.count()} messages")

if __name__ == '__main__':
    create_sample_data()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class BasicTests(TestCase):
    """Simple tests to verify the app works"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Test that user can be created"""
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')
        print("✅ User creation test passed!")
    
    def test_user_has_profile(self):
        """Test that user automatically gets a profile"""
        self.assertTrue(hasattr(self.user, 'profile'))
        print("✅ User profile test passed!")
    
    def test_login_page_loads(self):
        """Test that login page is accessible"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        print("✅ Login page test passed!")
    
    def test_user_can_login(self):
        """Test that user can log in"""
        logged_in = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(logged_in)
        print("✅ User login test passed!")
    
    def test_feed_requires_login(self):
        """Test that feed redirects if not logged in"""
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        print("✅ Feed authentication test passed!")

class PostTests(TestCase):
    """Test post functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_create_post(self):
        """Test creating a post"""
        from core.models import Post
        
        post = Post.objects.create(
            author=self.user,
            content='This is a test post!'
        )
        
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.content, 'This is a test post!')
        print("✅ Post creation test passed!")
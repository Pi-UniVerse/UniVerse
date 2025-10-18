[![Tests](https://github.com/Pi-UniVerse/UniVerse/actions/workflows/test.yml/badge.svg)](https://github.com/Pi-UniVerse/UniVerse/actions/workflows/test.yml)

# 🌐 UniVerse - AI-Powered Social Media Platform

<div align="center">

![UniVerse Logo](https://via.placeholder.com/200x200/6366f1/ffffff?text=UniVerse)

**Connect Beyond Boundaries** 🚀

[![GitHub](https://img.shields.io/badge/GitHub-Pi--UniVerse-blue?logo=github)](https://github.com/Pi-UniVerse/UniVerse)
[![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![HTML](https://img.shields.io/badge/HTML-81.1%25-orange?logo=html5)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-features) • [Installation](#-installation) • [Roadmap](#-roadmap) • [Contributing](#-contributing)

</div>

---

## 📖 About

**UniVerse** est un réseau social multimédia innovant, intégrant texte, images et audio, propulsé par l'IA pour une accessibilité universelle et une expérience personnalisée.

> A next-generation social media platform that breaks down communication barriers through AI-powered accessibility features, making connections truly universal.

---

## ✨ Features

### 🎯 **Core Social Features**

<table>
<tr>
<td width="50%">

#### 📝 **Content Creation**

- Rich text posts with images
- Video uploads & sharing
- 24-hour Stories
- Audio attachments
- Emoji reactions

</td>
<td width="50%">

#### 👥 **Community**

- User profiles & bios
- Follow system
- Groups & communities
- Direct messaging
- Real-time notifications

</td>
</tr>
</table>

### 🤖 **AI-Powered Features** (Roadmap)

<table>
<tr>
<td>

### 🎨 Création Assistée par IA

- 📸 Description automatique d'images
- 🎙️ Transcription audio
- 🔊 Synthèse vocale
- ✍️ Génération de légendes

</td>
<td>

### 🌍 Accessibilité Universelle

- 🌐 Traductions en temps réel
- 📝 Sous-titres intelligents
- 🔊 Lecture vocale
- ♿ Support écran lecteur

</td>
</tr>
<tr>
<td>

### 🛡️ Modération Intelligente

- 🚫 Détection de contenus haineux
- 🔍 Détection de fake news
- 🤖 Filtrage automatique
- ⚠️ Signalement proactif

</td>
<td>

### 🎯 Personnalisation Avancée

- 📊 Fil d'actualité intelligent
- 🔎 Recherche multimodale
- 💡 Recommandations hybrides
- 🎨 Expérience adaptée

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+
MySQL 8.0+
pip & virtualenv
```

### Installation

```bash
# Clone the repository
git clone https://github.com/Pi-UniVerse/UniVerse.git
cd UniVerse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Configure database
mysql -u root -p
CREATE DATABASE universe_db CHARACTER SET utf8mb4;
CREATE USER 'universe_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON universe_db.* TO 'universe_user'@'localhost';
EXIT;

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` 🎉

---

## 🏗️ Technology Stack

<div align="center">

### Backend

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)

### Frontend

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

### AI/ML (Planned)

![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)

</div>

---

## 📊 Project Statistics

```
Language Distribution:
████████████████████████████████ HTML   81.1%
██████                           Python 17.1%
█                                CSS     1.8%
```

- **Total Lines of Code**: 15,000+
- **Database Models**: 20+
- **Views & Templates**: 50+
- **Active Features**: 15+

---

## 🗂️ Project Structure

```
UniVerse/
├── 📁 core/                    # Main application
│   ├── models.py              # Database models
│   ├── views.py               # View logic
│   ├── forms.py               # Django forms
│   ├── urls.py                # URL routing
│   └── ai_services.py         # AI integration (future)
├── 📁 templates/              # HTML templates
│   ├── base.html              # Base template
│   └── core/
│       ├── feed.html          # Main feed
│       ├── profile.html       # User profiles
│       ├── video_detail.html  # Video player
│       └── messages_list.html # Messaging
├── 📁 static/                 # Static files
├── 📁 media/                  # User uploads
├── 📁 social_media/           # Project settings
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Models

### Core Models

- **User** - Authentication & profile
- **Post** - Text/image posts
- **Comment** - Nested comments
- **Like** - Post engagement
- **Follow** - User relationships

### Media Models

- **Video** - Video content
- **Playlist** - Video collections
- **Story** - Temporary content (24h)

### Communication

- **Message** - Direct messaging
- **Notification** - User alerts
- **Group** - Communities

### AI Models (Roadmap)

- **AIMetadata** - AI-generated data
- **ContentModeration** - Moderation results
- **UserPreferences** - AI settings
- **TranslationCache** - Translation storage

---

## 🎨 Design System

### Color Palette

```css
Primary:   #6366f1  /* Indigo */
Secondary: #ec4899  /* Pink */
Success:   #10b981  /* Green */
Danger:    #ef4444  /* Red */
```

### Typography

- **Font Family**: Inter, system-ui
- **Weights**: 300 - 900

---

## 🔮 Roadmap

### ✅ Phase 1: Foundation (Completed)

- [x] User authentication & profiles
- [x] Posts, comments, likes
- [x] Direct messaging
- [x] Video sharing & playlists
- [x] Stories (24h)
- [x] Groups & communities
- [x] Real-time notifications

### 🚧 Phase 2: AI Integration (Q1 2025)

- [ ] Image description AI
- [ ] Real-time translation (50+ languages)
- [ ] Content moderation
- [ ] Audio transcription
- [ ] Text-to-speech synthesis

### 📅 Phase 3: Advanced Features (Q2 2025)

- [ ] Smart feed algorithm
- [ ] Multimodal search (text, image, audio)
- [ ] Voice messages
- [ ] Live streaming
- [ ] Advanced analytics dashboard

### 🌟 Phase 4: Scale (Q3 2025)

- [ ] Mobile app (React Native)
- [ ] Public API
- [ ] Microservices architecture
- [ ] Multi-region deployment
- [ ] Enterprise features

---

## 💻 API Endpoints

### Posts

```
GET  /                      # Feed
POST /post/create/          # Create post
POST /post/<id>/like/       # Like post
POST /post/<id>/comment/    # Comment
GET  /post/<id>/delete/     # Delete post
```

### Users

```
GET  /profile/<username>/   # View profile
POST /follow/<username>/    # Follow user
GET  /profile/edit/         # Edit profile
```

### Videos

```
GET  /videos/               # Video feed
GET  /video/<id>/           # Video detail
POST /video/upload/         # Upload video
```

### Messages

```
GET  /messages/             # Conversations
GET  /messages/<username>/  # Chat
POST /messages/<username>/  # Send message
```

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use environment variables
- [ ] Set up PostgreSQL/MySQL
- [ ] Configure static files (S3/CDN)
- [ ] Enable HTTPS
- [ ] Set up monitoring (Sentry)
- [ ] Configure email backend
- [ ] Set up Redis caching
- [ ] Configure Celery for tasks

### Recommended Platforms

- **Backend**: Heroku, DigitalOcean, AWS, Google Cloud
- **Database**: AWS RDS, Google Cloud SQL
- **Storage**: AWS S3, Google Cloud Storage
- **CDN**: CloudFlare, AWS CloudFront

---

## 💰 Cost Estimates (with AI)

### AI Services (Monthly)

| Service             | Cost         |
| ------------------- | ------------ |
| OpenAI API          | $50-200      |
| Google Cloud Vision | $30-100      |
| Google Translate    | $20-80       |
| Google Speech APIs  | $40-150      |
| **Total AI**        | **$140-530** |

### Infrastructure

| Service                  | Cost        |
| ------------------------ | ----------- |
| Server                   | $20-100     |
| Database                 | $15-50      |
| Storage & CDN            | $15-80      |
| **Total Infrastructure** | **$50-230** |

**Total Monthly**: $190-760

---

## 👥 Contributing

We welcome contributions! 🎉

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit** your changes
   ```bash
   git commit -m '✨ Add AmazingFeature'
   ```
4. **Push** to the branch
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open** a Pull Request

### Commit Convention

Use emojis for clarity:

- ✨ `:sparkles:` - New feature
- 🐛 `:bug:` - Bug fix
- 📝 `:memo:` - Documentation
- 🎨 `:art:` - UI/UX
- ♻️ `:recycle:` - Refactor
- 🚀 `:rocket:` - Performance
- 🔒 `:lock:` - Security

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Django Framework Team
- OpenAI & Google Cloud
- Open Source Community
- All Contributors ❤️

---

## 📞 Contact

<div align="center">

### Get in Touch

[![Email](https://img.shields.io/badge/Email-support@universe.com-red?style=for-the-badge&logo=gmail)](mailto:support@universe.com)
[![GitHub](https://img.shields.io/badge/GitHub-Pi--UniVerse-black?style=for-the-badge&logo=github)](https://github.com/Pi-UniVerse)
[![Twitter](https://img.shields.io/badge/Twitter-@UniVerseSocial-blue?style=for-the-badge&logo=twitter)](https://twitter.com/UniverseSocial)

**Report bugs**: [GitHub Issues](https://github.com/Pi-UniVerse/UniVerse/issues)

</div>

---

## 📈 Stats

![GitHub Stars](https://img.shields.io/github/stars/Pi-UniVerse/UniVerse?style=social)
![GitHub Forks](https://img.shields.io/github/forks/Pi-UniVerse/UniVerse?style=social)
![GitHub Issues](https://img.shields.io/github/issues/Pi-UniVerse/UniVerse)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/Pi-UniVerse/UniVerse)

---

<div align="center">

### 🌟 Star us on GitHub!

**Built with ❤️ by the Pi-UniVerse Team**

_Connecting the universe, one post at a time._ 🌐✨

[⬆ Back to Top](#-universe---ai-powered-social-media-platform)

</div>

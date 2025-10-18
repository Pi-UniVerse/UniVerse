-- Create the database
CREATE DATABASE IF NOT EXISTS django_social_media CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a dedicated user for Django
CREATE USER IF NOT EXISTS 'django_user'@'localhost' IDENTIFIED BY 'django_secure_pass_2024';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON django_social_media.* TO 'django_user'@'localhost';

-- Apply the privilege changes
FLUSH PRIVILEGES;

-- Verify the user was created
SELECT user, host FROM mysql.user WHERE user='django_user';

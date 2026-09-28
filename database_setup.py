import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', os.getenv('MYSQL_HOST', 'localhost'))
DB_USER = os.getenv('DB_USER', os.getenv('MYSQL_USER', 'root'))
DB_PASSWORD = os.getenv('DB_PASSWORD', os.getenv('MYSQL_PASSWORD', 'Radhey2005@'))
DB_NAME = os.getenv('DB_NAME', os.getenv('MYSQL_DB', 'mental_wellness_db'))
DB_PORT = int(os.getenv('DB_PORT', os.getenv('MYSQL_PORT', 3306)))

print(f"Connecting to MySQL server at {DB_HOST}:{DB_PORT} as user '{DB_USER}'...")

connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT,
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        print(f"Creating database '{DB_NAME}' if not exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{DB_NAME}`")

        # 1. Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `users` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `username` VARCHAR(50) NOT NULL UNIQUE,
            `email` VARCHAR(100) NOT NULL UNIQUE,
            `password` VARCHAR(255) NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 2. Support groups & Groups
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `groups` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(100) NOT NULL,
            `description` TEXT,
            `banner_color` VARCHAR(50) DEFAULT NULL,
            `icon` VARCHAR(50) DEFAULT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `support_groups` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(100) NOT NULL,
            `description` TEXT,
            `banner_color` VARCHAR(50) DEFAULT NULL,
            `icon` VARCHAR(50) DEFAULT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 3. Group members
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `group_members` (
            `user_id` INT NOT NULL,
            `group_id` INT NOT NULL,
            `joined_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (`user_id`, `group_id`),
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`group_id`) REFERENCES `groups`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 4. Mood entries
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `mood_entries` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `mood` VARCHAR(50) NOT NULL,
            `intensity` INT NOT NULL DEFAULT 5,
            `notes` TEXT,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 5. Journal entries
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `journal_entries` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `title` VARCHAR(100) NOT NULL DEFAULT 'Untitled',
            `content` TEXT NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 6. Notifications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `notifications` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `type` VARCHAR(50) DEFAULT 'info',
            `message` TEXT NOT NULL,
            `is_read` TINYINT(1) DEFAULT 0,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 7. Community Posts
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `posts` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `content` TEXT NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 8. Post Likes & Comments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `post_likes` (
            `user_id` INT NOT NULL,
            `post_id` INT NOT NULL,
            `liked_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (`user_id`, `post_id`),
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`post_id`) REFERENCES `posts`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `post_comments` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `post_id` INT NOT NULL,
            `content` TEXT NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`post_id`) REFERENCES `posts`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 9. Music Tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `music_songs` (
            `id` VARCHAR(255) PRIMARY KEY,
            `title` VARCHAR(255) NOT NULL,
            `artist` VARCHAR(255) NOT NULL,
            `thumbnail` VARCHAR(512) DEFAULT NULL,
            `duration` VARCHAR(20) DEFAULT NULL,
            `description` TEXT,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `music_playlists` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `name` VARCHAR(255) NOT NULL,
            `description` TEXT,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `music_playlist_songs` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `playlist_id` INT NOT NULL,
            `song_id` VARCHAR(255) NOT NULL,
            `added_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY `unique_playlist_song` (`playlist_id`, `song_id`),
            FOREIGN KEY (`playlist_id`) REFERENCES `music_playlists`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`song_id`) REFERENCES `music_songs`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `music_favorites` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `song_id` VARCHAR(255) NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY `unique_favorite` (`user_id`, `song_id`),
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`song_id`) REFERENCES `music_songs`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `music_history` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `song_id` VARCHAR(255) NOT NULL,
            `played_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`song_id`) REFERENCES `music_songs`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # 10. Therapeutic Games Tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `game_sessions` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `game_type` VARCHAR(50) NOT NULL,
            `duration` INT NOT NULL COMMENT 'Duration in seconds',
            `score` INT DEFAULT NULL,
            `session_data` JSON DEFAULT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `game_activity` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `activity_type` VARCHAR(50) NOT NULL,
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `game_achievements` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `game_type` VARCHAR(50) NOT NULL,
            `achievement_name` VARCHAR(100) NOT NULL,
            `achieved_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY `unique_user_achievement` (`user_id`, `game_type`, `achievement_name`),
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS `saved_games` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `game_type` VARCHAR(50) NOT NULL,
            `game_state` JSON NOT NULL,
            `last_played` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY `unique_user_game` (`user_id`, `game_type`),
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Seed initial groups if empty
        cursor.execute("SELECT COUNT(*) AS count FROM `groups`")
        if cursor.fetchone()['count'] == 0:
            cursor.execute("""
            INSERT INTO `groups` (`name`, `description`, `banner_color`, `icon`) VALUES
            ('Mindfulness & Meditation', 'Share mindful moments, breathwork techniques, and daily peace.', '#6c5ce7', 'spa'),
            ('Stress & Anxiety Relief', 'A supportive space for navigating everyday worries and calming strategies.', '#0984e3', 'feather-alt'),
            ('Positive Vibes & Gratitude', 'Celebrate small wins, share positive thoughts, and uplift each other.', '#00b894', 'sun');
            """)

        # Seed initial support groups if empty
        cursor.execute("SELECT COUNT(*) AS count FROM `support_groups`")
        if cursor.fetchone()['count'] == 0:
            cursor.execute("""
            INSERT INTO `support_groups` (`name`, `description`, `banner_color`, `icon`) VALUES
            ('Daily Coping Circle', 'Daily check-ins for coping tools and mutual support.', '#e17055', 'heart'),
            ('Sleep & Rest Well', 'Tips, habits, and community discussions for restful recovery.', '#a29bfe', 'moon'),
            ('Creative Healing', 'Art, writing, journaling, and musical expression for mental wellness.', '#fd79a8', 'palette');
            """)

        connection.commit()
        print("All 19 database tables and initial seed data configured successfully!")
finally:
    connection.close()
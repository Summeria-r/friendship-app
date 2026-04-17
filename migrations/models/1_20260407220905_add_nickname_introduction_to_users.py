from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `likes` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `like_type` VARCHAR(20) NOT NULL COMMENT '点赞类型：post=帖子, comment=评论' DEFAULT 'post',
    `comment_id` INT,
    `post_id` INT,
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_likes_user_id_31fec2` (`user_id`, `post_id`),
    UNIQUE KEY `uid_likes_user_id_a71e14` (`user_id`, `comment_id`),
    CONSTRAINT `fk_likes_comments_55c4dbc9` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_likes_posts_f849e61d` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_likes_users_a61ca3f4` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='点赞模型';
        ALTER TABLE `users` ADD `nickname` VARCHAR(50) COMMENT '昵称';
        ALTER TABLE `users` ADD `introduction` LONGTEXT COMMENT '个人介绍';
        DROP TABLE IF EXISTS `like`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` DROP COLUMN `nickname`;
        ALTER TABLE `users` DROP COLUMN `introduction`;
        DROP TABLE IF EXISTS `likes`;"""

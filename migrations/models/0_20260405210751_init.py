from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `interests` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(20) NOT NULL UNIQUE COMMENT '兴趣名称（枚举值）'
) CHARACTER SET utf8mb4 COMMENT='兴趣模型';
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password` VARCHAR(100) NOT NULL COMMENT '密码哈希值',
    `gender` VARCHAR(10) COMMENT '性别',
    `birthday` DATE COMMENT '生日',
    `bio` LONGTEXT COMMENT '个性签名',
    `department` VARCHAR(100) COMMENT '学院',
    `major` VARCHAR(100) COMMENT '专业',
    `phone` VARCHAR(20) COMMENT '联系电话',
    `level` INT NOT NULL COMMENT '用户等级' DEFAULT 1,
    `student_id` VARCHAR(20) COMMENT '学号',
    `avatar` VARCHAR(200) COMMENT '头像URL',
    `account_status` VARCHAR(20) NOT NULL COMMENT '账号状态' DEFAULT 'active',
    `last_login_at` DATETIME(6) COMMENT ' 最后登录时间',
    `is_system` BOOL NOT NULL COMMENT '是否为系统用户' DEFAULT 0,
    KEY `idx_users_usernam_266d85` (`username`),
    KEY `idx_users_created_43d91f` (`created_at`),
    KEY `idx_users_last_lo_728870` (`last_login_at`)
) CHARACTER SET utf8mb4 COMMENT='用户模型';
CREATE TABLE IF NOT EXISTS `instant_match_wait` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `clicked_at` DATETIME(6) NOT NULL COMMENT '点击时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_matched` BOOL NOT NULL DEFAULT 0,
    `interest_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_instant__interest_8ca1fcc5` FOREIGN KEY (`interest_id`) REFERENCES `interests` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_instant__users_6630c0e4` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_instant_mat_interes_4c03fd` (`interest_id`, `is_matched`, `clicked_at`)
) CHARACTER SET utf8mb4 COMMENT='即时匹配等待模型';
CREATE TABLE IF NOT EXISTS `long_term_match_wait` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `requirements` JSON COMMENT '匹配要求',
    `expire_at` DATETIME(6) NOT NULL COMMENT '过期时间',
    `is_matched` BOOL NOT NULL DEFAULT 0,
    `interest_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_long_ter_interest_79ced710` FOREIGN KEY (`interest_id`) REFERENCES `interests` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_long_ter_users_aac8d1f9` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_long_term_m_interes_0258a9` (`interest_id`, `is_matched`, `expire_at`)
) CHARACTER SET utf8mb4 COMMENT='长期匹配等待模型';
CREATE TABLE IF NOT EXISTS `match_record` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `match_type` VARCHAR(9) NOT NULL COMMENT 'LONG_TERM: long_term\nINSTANT: instant',
    `status` VARCHAR(8) NOT NULL COMMENT 'MATCHING: matching\nMATCHED: matched\nEXPIRED: expired' DEFAULT 'matching',
    `expire_at` DATETIME(6) COMMENT '过期时间',
    `interest_id` INT NOT NULL,
    `user1_id` INT NOT NULL,
    `user2_id` INT COMMENT '被匹配用户，可为空表示匹配失败',
    CONSTRAINT `fk_match_re_interest_e7f0ff0f` FOREIGN KEY (`interest_id`) REFERENCES `interests` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_match_re_users_46ae8faa` FOREIGN KEY (`user1_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_match_re_users_63e36edb` FOREIGN KEY (`user2_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_match_recor_interes_a4856e` (`interest_id`, `match_type`, `status`),
    KEY `idx_match_recor_user1_i_d6a67e` (`user1_id`),
    KEY `idx_match_recor_user2_i_f1b7ff` (`user2_id`),
    KEY `idx_match_recor_expire__69b499` (`expire_at`)
) CHARACTER SET utf8mb4 COMMENT='匹配记录模型';
CREATE TABLE IF NOT EXISTS `posts` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `title` VARCHAR(200) NOT NULL COMMENT '帖子标题',
    `content` LONGTEXT NOT NULL COMMENT '帖子内容',
    `category` VARCHAR(20) NOT NULL COMMENT '帖子分类',
    `is_sticky` BOOL NOT NULL COMMENT '是否置顶' DEFAULT 0,
    `like_count` INT NOT NULL COMMENT '点赞数' DEFAULT 0,
    `comment_count` INT NOT NULL COMMENT '评论数' DEFAULT 0,
    `collect_count` INT NOT NULL COMMENT '收藏数' DEFAULT 0,
    `user_id` INT NOT NULL COMMENT '发帖用户',
    CONSTRAINT `fk_posts_users_10758681` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_posts_created_a1aafc` (`created_at`),
    KEY `idx_posts_categor_a355dc` (`category`)
) CHARACTER SET utf8mb4 COMMENT='帖子模型';
CREATE TABLE IF NOT EXISTS `collect` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `post_id` INT,
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_collect_user_id_9ebf8c` (`user_id`, `post_id`),
    CONSTRAINT `fk_collect_posts_dae8faea` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_collect_users_2a8b3302` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `comments` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `content` LONGTEXT NOT NULL COMMENT '评论内容',
    `parent_id` INT COMMENT '父评论',
    `post_id` INT NOT NULL COMMENT '评论帖子',
    `user_id` INT NOT NULL COMMENT '评论用户',
    CONSTRAINT `fk_comments_comments_ab2e55ce` FOREIGN KEY (`parent_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_comments_posts_06d733fd` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_comments_users_24d9ac18` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_comments_created_34e3bf` (`created_at`)
) CHARACTER SET utf8mb4 COMMENT='评论模型（为null表示顶级评论）';
CREATE TABLE IF NOT EXISTS `like` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `like_type` VARCHAR(20) NOT NULL COMMENT '点赞类型：post=帖子, comment=评论' DEFAULT 'post',
    `comment_id` INT,
    `post_id` INT,
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_like_user_id_ba3b87` (`user_id`, `post_id`),
    UNIQUE KEY `uid_like_user_id_82295a` (`user_id`, `comment_id`),
    CONSTRAINT `fk_like_comments_f5a31179` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_like_posts_d517d438` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_like_users_2224695a` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='点赞模型';
CREATE TABLE IF NOT EXISTS `notification` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `type` VARCHAR(13) NOT NULL COMMENT '通知类型: 帖子评论/点赞/收藏、评论回复/点赞',
    `content` VARCHAR(200) NOT NULL COMMENT '通知展示内容（如：XX评论了你的帖子）',
    `is_read` BOOL NOT NULL COMMENT '是否已读' DEFAULT 0,
    `comment_id` INT COMMENT '关联的评论',
    `post_id` INT COMMENT '关联的帖子',
    `sender_id` INT NOT NULL COMMENT '通知发送者',
    `user_id` INT NOT NULL COMMENT '通知接收者',
    CONSTRAINT `fk_notifica_comments_11951cb2` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_notifica_posts_a6d58366` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_notifica_users_19f3e4ca` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_notifica_users_c30cb5cd` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_notificatio_user_id_772eee` (`user_id`, `is_read`)
) CHARACTER SET utf8mb4 COMMENT='帖子消息模型';
CREATE TABLE IF NOT EXISTS `messages` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `content` LONGTEXT NOT NULL COMMENT '消息内容',
    `is_read` BOOL NOT NULL COMMENT '是否已读' DEFAULT 0,
    `message_type` VARCHAR(20) NOT NULL COMMENT '消息类型' DEFAULT 'text',
    `read_at` DATETIME(6) COMMENT '阅读时间',
    `receiver_id` INT NOT NULL COMMENT '接收者',
    `sender_id` INT NOT NULL COMMENT '发送者',
    CONSTRAINT `fk_messages_users_a2d90c12` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_messages_users_60805009` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_messages_created_c3e88b` (`created_at`)
) CHARACTER SET utf8mb4 COMMENT='消息模型';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `users_interests` (
    `users_id` INT NOT NULL,
    `interest_id` INT NOT NULL,
    FOREIGN KEY (`users_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`interest_id`) REFERENCES `interests` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_users_inter_users_i_2759ae` (`users_id`, `interest_id`)
) CHARACTER SET utf8mb4 COMMENT='用户兴趣';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `long_term_match_wait` DROP COLUMN `requirements`;
        ALTER TABLE `long_term_match_wait` MODIFY COLUMN `is_matched` BOOL COMMENT '是否已匹配' DEFAULT 0;
        ALTER TABLE `long_term_match_wait` MODIFY COLUMN `is_matched` BOOL COMMENT '是否已匹配' DEFAULT 0;
        ALTER TABLE `long_term_match_wait` MODIFY COLUMN `expire_at` DATETIME(6) COMMENT '过期时间';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `long_term_match_wait` ADD `requirements` JSON COMMENT '匹配要求';
        ALTER TABLE `long_term_match_wait` MODIFY COLUMN `is_matched` BOOL NOT NULL DEFAULT 0;
        ALTER TABLE `long_term_match_wait` MODIFY COLUMN `is_matched` BOOL NOT NULL DEFAULT 0;
        ALTER TABLE `long_term_match_wait` MODIFY COLUMN `expire_at` DATETIME(6) NOT NULL COMMENT '过期时间';"""

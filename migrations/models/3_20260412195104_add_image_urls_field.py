from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `posts` ADD `image_urls` JSON NOT NULL COMMENT '图片URL列表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `posts` DROP COLUMN `image_urls`;"""

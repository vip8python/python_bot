"""lenteles

Revision ID: b257cdca44d2
Revises: 
Create Date: 2024-06-11 19:41:01.162115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b257cdca44d2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('participants')
    op.drop_table('tasks')
    op.add_column('users', sa.Column('contacts', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('registered', sa.Date(), nullable=True))
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=100),
               nullable=False)
    op.alter_column('users', 'telegram_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=100),
               nullable=True)
    op.drop_constraint('users_telegram_id_key', 'users', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('users_telegram_id_key', 'users', ['telegram_id'])
    op.alter_column('users', 'telegram_id',
               existing_type=sa.String(length=100),
               type_=sa.INTEGER(),
               nullable=False)
    op.alter_column('users', 'username',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=255),
               nullable=True)
    op.drop_column('users', 'registered')
    op.drop_column('users', 'description')
    op.drop_column('users', 'contacts')
    op.create_table('tasks',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('tasks_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('framework', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('participants', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('github_link', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='tasks_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='tasks_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('participants',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('task_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name='participants_task_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='participants_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='participants_pkey')
    )
    # ### end Alembic commands ###
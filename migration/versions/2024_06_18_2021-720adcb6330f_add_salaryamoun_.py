"""add salaryamount, projectqualificationemployee

Revision ID: 720adcb6330f
Revises: 0a5da0ee96c3
Create Date: 2024-06-18 20:21:44.357215

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '720adcb6330f'
down_revision = '0a5da0ee96c3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'salary_amounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'project_qualification_employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('qualification_id', sa.Integer(), sa.ForeignKey('qualifications.id'), nullable=False),
        sa.Column('employees_count', sa.Integer(), nullable=False),
        sa.Column('salary_amount_id', sa.Integer(), sa.ForeignKey('salary_amounts.id'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_foreign_key(
        'fk_project_qualification_employees_salary_amounts',
        'project_qualification_employees', 'salary_amounts',
        ['salary_amount_id'], ['id']
    )


def downgrade():
    op.drop_table('project_qualification_employees')
    op.drop_table('salary_amounts')

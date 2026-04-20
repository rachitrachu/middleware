"""Rename the truenas_connect table to xnas_connect.

Part of the TrueNAS -> X-NAS rebrand. The feature is now branded as
X-NAS Connect end-to-end (plugin dir middlewared/plugins/xnas_connect,
logger channel 'xnas_connect', /var/log/xnas_connect.log, cert prefix
'xnas_connect_', cache keys 'xnas_connect_*'). The database table is
the last piece still named truenas_connect and this migration closes
the gap so fresh installs + upgrades both land on 'xnas_connect'.

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-04-20 00:00:00.000000+00:00

"""
from alembic import op


revision = 'c2d3e4f5a6b7'
down_revision = 'b1c2d3e4f5a6'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('truenas_connect', 'xnas_connect')


def downgrade():
    op.rename_table('xnas_connect', 'truenas_connect')

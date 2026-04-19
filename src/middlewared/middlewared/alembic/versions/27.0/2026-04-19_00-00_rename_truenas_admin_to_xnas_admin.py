"""Rename the default local administrator from truenas_admin to xnas_admin.

Fresh X-NAS installs create xnas_admin directly, but any system upgraded
from a X-NAS SCALE image has a local user and group literally named
truenas_admin at UID/GID 950. Rename them in place so the product-name
rebrand is consistent end-to-end (home directory, config paths, PAM
tokens, WebUI display). The UID/GID 950 mapping is preserved so file
ownership on mounted pools / /home does not need to be rewritten.

Revision ID: b1c2d3e4f5a6
Revises: a3b4c5d6e7f8
Create Date: 2026-04-19 00:00:00.000000+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = 'a3b4c5d6e7f8'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Rename the built-in administrator user + group at UID/GID 950. Only
    # rename the literal truenas_admin row -- if an operator has already
    # created xnas_admin manually (or the migration re-runs) this is a
    # no-op.
    conn.execute(sa.text(
        "UPDATE account_bsdusers "
        "SET bsdusr_username = 'xnas_admin', "
        "    bsdusr_home = '/home/xnas_admin' "
        "WHERE bsdusr_username = 'truenas_admin' AND bsdusr_uid = 950"
    ))
    conn.execute(sa.text(
        "UPDATE account_bsdgroups "
        "SET bsdgrp_group = 'xnas_admin' "
        "WHERE bsdgrp_group = 'truenas_admin' AND bsdgrp_gid = 950"
    ))


def downgrade():
    conn = op.get_bind()
    conn.execute(sa.text(
        "UPDATE account_bsdusers "
        "SET bsdusr_username = 'truenas_admin', "
        "    bsdusr_home = '/home/truenas_admin' "
        "WHERE bsdusr_username = 'xnas_admin' AND bsdusr_uid = 950"
    ))
    conn.execute(sa.text(
        "UPDATE account_bsdgroups "
        "SET bsdgrp_group = 'truenas_admin' "
        "WHERE bsdgrp_group = 'xnas_admin' AND bsdgrp_gid = 950"
    ))

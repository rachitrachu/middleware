import enum
import errno
import os
from types import MappingProxyType

import xnas_os

from typing import Any

ACL_UNDEFINED_ID = -1


class ACLXattr(enum.StrEnum):
    POSIX_ACCESS = "system.posix_acl_access"
    POSIX_DEFAULT = "system.posix_acl_default"
    ZFS_NATIVE = "system.nfs4_acl_xdr"


ACL_XATTRS = frozenset([xat.value for xat in ACLXattr])

# ACCESS_ACL_XATTRS is set of ACLs that control access to the file itself.
ACCESS_ACL_XATTRS = frozenset([ACLXattr.POSIX_ACCESS.value, ACLXattr.ZFS_NATIVE.value])


def acl_is_present(xat_list: list[str]) -> bool:
    """
    This method returns boolean value if ACL is present in a list of extended
    attribute names. Both POSIX1E and our NFSv4 ACL implementations omit the
    xattr name from the list if it has no impact on permisssions (mode is
    authoritative.
    """
    return bool(set(xat_list) & ACL_XATTRS)


class FS_ACL_Type(enum.StrEnum):
    NFS4 = 'NFS4'
    POSIX1E = 'POSIX1E'
    DISABLED = 'DISABLED'


class NFS4ACE_Tag(enum.StrEnum):
    # See RFC-5661 Section 6.2.1.5
    # https://datatracker.ietf.org/doc/html/rfc5661#section-6.2.1.5
    #
    # Combination of NFS4ACE_Tag and id create the ACE Who field

    # Special identifiers
    SPECIAL_OWNER = 'owner@'  # file owner
    SPECIAL_GROUP = 'group@'  # file group
    SPECIAL_EVERYONE = 'everyone@'  # world (including owner and group)

    # Identifiers for regular user / group entries
    USER = 'USER'
    GROUP = 'GROUP'


class NFS4ACE_Type(enum.StrEnum):
    # See RFC-5661 Section 6.2.1.1
    # https://datatracker.ietf.org/doc/html/rfc5661#section-6.2.1.1
    ALLOW = 'ALLOW'
    DENY = 'DENY'


class NFS4ACE_Mask(enum.StrEnum):
    # See RFC-5661 Section 6.2.1.3.1
    # https://datatracker.ietf.org/doc/html/rfc5661#section-6.2.1.3.1
    READ_DATA = 'READ_DATA'
    WRITE_DATA = 'WRITE_DATA'
    APPEND_DATA = 'APPEND_DATA'
    READ_NAMED_ATTRS = 'READ_NAMED_ATTRS'
    WRITE_NAMED_ATTRS = 'WRITE_NAMED_ATTRS'
    EXECUTE = 'EXECUTE'
    DELETE = 'DELETE'
    DELETE_CHILD = 'DELETE_CHILD'
    READ_ATTRIBUTES = 'READ_ATTRIBUTES'
    WRITE_ATTRIBUTES = 'WRITE_ATTRIBUTES'
    READ_ACL = 'READ_ACL'
    WRITE_ACL = 'WRITE_ACL'
    WRITE_OWNER = 'WRITE_OWNER'
    SYNCHRONIZE = 'SYNCHRONIZE'


class NFS4ACE_MaskSimple(enum.StrEnum):
    # These are convenience access masks that are a combination of multiple
    # permissions defined in NFS4ACE_Mask above
    FULL_CONTROL = 'FULL_CONTROL'  # all perms above
    MODIFY = 'MODIFY'  # all perms except WRITE_ACL and WRITE_OWNER
    READ = 'READ'  # READ | READ_NAMED_ATTRS | READ_ATTRIBUTES | EXECUTE
    TRAVERSE = 'TRAVERSE'  # READ_NAMED_ATTRS | READ_ATTRIBUTES | EXECUTE


class NFS4ACE_Flag(enum.StrEnum):
    # See RFC-5661 Section 6.2.1.4.1
    # https://datatracker.ietf.org/doc/html/rfc5661#section-6.2.1.4.1
    FILE_INHERIT = 'FILE_INHERIT'
    DIRECTORY_INHERIT = 'DIRECTORY_INHERIT'
    NO_PROPAGATE_INHERIT = 'NO_PROPAGATE_INHERIT'
    INHERIT_ONLY = 'INHERIT_ONLY'
    INHERITED = 'INHERITED'


class NFS4ACE_FlagSimple(enum.StrEnum):
    # These are convenience access masks that are a combination of multiple
    # permissions defined in NFS4ACE_Mask above
    INHERIT = 'INHERIT'  # FILE_INHERIT | DIRECTORY_INHERIT
    NOINHERIT = 'NOINHERIT'  # ace flags = 0


class NFS4ACL_Flag(enum.StrEnum):
    # See RFC-5661 Section 6.4.3.2
    # https://datatracker.ietf.org/doc/html/rfc5661#section-6.4.3.2
    AUTOINHERIT = 'autoinherit'
    PROTECTED = 'protected'
    DEFAULTED = 'defaulted'


class POSIXACE_Tag(enum.StrEnum):
    # UGO entries
    USER_OBJ = 'USER_OBJ'  # file owner
    GROUP_OBJ = 'GROUP_OBJ'  # file group
    OTHER = 'OTHER'  # other

    MASK = 'MASK'  # defines maximum permissions granted to extended entries

    # Identifiers for regular user / group entries
    USER = 'USER'
    GROUP = 'GROUP'


class POSIXACE_Mask(enum.StrEnum):
    READ = 'READ'
    WRITE = 'WRITE'
    EXECUTE = 'EXECUTE'


NFS4_SPECIAL_ENTRIES = frozenset([
    NFS4ACE_Tag.SPECIAL_OWNER,
    NFS4ACE_Tag.SPECIAL_GROUP,
    NFS4ACE_Tag.SPECIAL_EVERYONE,
])

POSIX_SPECIAL_ENTRIES = frozenset([
    POSIXACE_Tag.USER_OBJ,
    POSIXACE_Tag.GROUP_OBJ,
    POSIXACE_Tag.OTHER,
    POSIXACE_Tag.MASK,
])


def path_get_acltype(path: str) -> FS_ACL_Type:
    try:
        # ACCESS ACL is sufficient to determine POSIX ACL support
        os.getxattr(path, ACLXattr.POSIX_ACCESS)
        return FS_ACL_Type.POSIX1E

    except OSError as e:
        if e.errno == errno.ENODATA:
            # No ACL set, but zfs acltype is set to POSIX
            return FS_ACL_Type.POSIX1E

        # EOPNOTSUPP means that ZFS acltype is not set to POSIX
        if e.errno != errno.EOPNOTSUPP:
            raise

    try:
        os.getxattr(path, ACLXattr.ZFS_NATIVE)
        return FS_ACL_Type.NFS4
    except OSError as e:
        # ZFS acltype is not set to NFS4 which means it's disabled
        if e.errno == errno.EOPNOTSUPP:
            return FS_ACL_Type.DISABLED

        raise


def normalize_acl_ids(setacl_data: dict[str, Any]) -> None:
    for key in ('uid', 'gid'):
        if setacl_data[key] is None:
            setacl_data[key] = ACL_UNDEFINED_ID

    for ace in setacl_data['dacl']:
        if ace['id'] is None:
            ace['id'] = ACL_UNDEFINED_ID


# ---------------------------------------------------------------------------
# xnas_os integration
# ---------------------------------------------------------------------------

# NFS4 "BASIC" permission shortcuts (all 14 permission bits)
_NFS4_BASIC_FULL = (
    xnas_os.NFS4Perm.READ_DATA |
    xnas_os.NFS4Perm.WRITE_DATA |
    xnas_os.NFS4Perm.APPEND_DATA |
    xnas_os.NFS4Perm.READ_NAMED_ATTRS |
    xnas_os.NFS4Perm.WRITE_NAMED_ATTRS |
    xnas_os.NFS4Perm.EXECUTE |
    xnas_os.NFS4Perm.DELETE_CHILD |
    xnas_os.NFS4Perm.READ_ATTRIBUTES |
    xnas_os.NFS4Perm.WRITE_ATTRIBUTES |
    xnas_os.NFS4Perm.DELETE |
    xnas_os.NFS4Perm.READ_ACL |
    xnas_os.NFS4Perm.WRITE_ACL |
    xnas_os.NFS4Perm.WRITE_OWNER |
    xnas_os.NFS4Perm.SYNCHRONIZE
)
_NFS4_BASIC_MODIFY = _NFS4_BASIC_FULL & ~(
    xnas_os.NFS4Perm.WRITE_ACL | xnas_os.NFS4Perm.WRITE_OWNER
)
_NFS4_BASIC_READ = (
    xnas_os.NFS4Perm.READ_DATA |
    xnas_os.NFS4Perm.READ_NAMED_ATTRS |
    xnas_os.NFS4Perm.READ_ATTRIBUTES |
    xnas_os.NFS4Perm.READ_ACL |
    xnas_os.NFS4Perm.EXECUTE |
    xnas_os.NFS4Perm.SYNCHRONIZE
)
_NFS4_BASIC_TRAVERSE = (
    xnas_os.NFS4Perm.READ_NAMED_ATTRS |
    xnas_os.NFS4Perm.READ_ATTRIBUTES |
    xnas_os.NFS4Perm.EXECUTE |
    xnas_os.NFS4Perm.SYNCHRONIZE
)

# Lookup tables used by the conversion helpers below
_NFS4_PERM_NAMES = tuple(NFS4ACE_Mask)
# Input flag names: our enum members plus audit flags that live only in xnas_os
_NFS4_FLAG_NAMES = (
    NFS4ACE_Flag.FILE_INHERIT, NFS4ACE_Flag.DIRECTORY_INHERIT,
    NFS4ACE_Flag.NO_PROPAGATE_INHERIT, NFS4ACE_Flag.INHERIT_ONLY,
    'SUCCESSFUL_ACCESS', 'FAILED_ACCESS',
    NFS4ACE_Flag.INHERITED,
)
# Output flag names (audit flags omitted)
_NFS4_OUTPUT_FLAG_NAMES = tuple(NFS4ACE_Flag)
_NFS4_BASIC_PERMS = MappingProxyType({
    NFS4ACE_MaskSimple.FULL_CONTROL: _NFS4_BASIC_FULL,
    NFS4ACE_MaskSimple.MODIFY: _NFS4_BASIC_MODIFY,
    NFS4ACE_MaskSimple.READ: _NFS4_BASIC_READ,
    NFS4ACE_MaskSimple.TRAVERSE: _NFS4_BASIC_TRAVERSE,
})
_NFS4_BASIC_PERMS_REV = MappingProxyType({v: k for k, v in _NFS4_BASIC_PERMS.items()})
_NFS4_BASIC_FLAGS = MappingProxyType({
    NFS4ACE_FlagSimple.INHERIT: xnas_os.NFS4Flag.FILE_INHERIT | xnas_os.NFS4Flag.DIRECTORY_INHERIT,
    NFS4ACE_FlagSimple.NOINHERIT: xnas_os.NFS4Flag(0),
})
_NFS4_BASIC_FLAGS_REV = MappingProxyType({v: k for k, v in _NFS4_BASIC_FLAGS.items()})
_NFS4_ACL_FLAGS = MappingProxyType({
    NFS4ACL_Flag.AUTOINHERIT: xnas_os.NFS4ACLFlag.AUTO_INHERIT,
    NFS4ACL_Flag.PROTECTED: xnas_os.NFS4ACLFlag.PROTECTED,
    NFS4ACL_Flag.DEFAULTED: xnas_os.NFS4ACLFlag.DEFAULTED,
})
_NFS4_TAG_TO_WHO = MappingProxyType({
    NFS4ACE_Tag.SPECIAL_OWNER: xnas_os.NFS4Who.OWNER,
    NFS4ACE_Tag.SPECIAL_GROUP: xnas_os.NFS4Who.GROUP,
    NFS4ACE_Tag.SPECIAL_EVERYONE: xnas_os.NFS4Who.EVERYONE,
})
_NFS4_WHO_TO_TAG = MappingProxyType({v: k for k, v in _NFS4_TAG_TO_WHO.items()})
_POSIX_PERM_NAMES = tuple(POSIXACE_Mask)


# ---------------------------------------------------------------------------
# Internal helpers (only valid when xnas_os is available)
# ---------------------------------------------------------------------------

def _perm_obj_to_full_dict(perm: 'xnas_os.NFS4Perm') -> dict:
    return {n: bool(perm & getattr(xnas_os.NFS4Perm, n)) for n in _NFS4_PERM_NAMES}


def _flags_obj_to_dict(flags: 'xnas_os.NFS4Flag') -> dict:
    # SUCCESSFUL_ACCESS and FAILED_ACCESS are intentionally omitted from output
    return {n: bool(flags & getattr(xnas_os.NFS4Flag, n)) for n in _NFS4_OUTPUT_FLAG_NAMES}


def _perm_dict_to_obj(perms_dict: dict) -> 'xnas_os.NFS4Perm':
    perm = xnas_os.NFS4Perm(0)
    for n in _NFS4_PERM_NAMES:
        if perms_dict.get(n):
            perm |= getattr(xnas_os.NFS4Perm, n)
    return perm


def _flags_dict_to_obj(flags_dict: dict) -> 'xnas_os.NFS4Flag':
    flags = xnas_os.NFS4Flag(0)
    for n in _NFS4_FLAG_NAMES:
        if flags_dict.get(n):
            flags |= getattr(xnas_os.NFS4Flag, n)
    return flags


# ---------------------------------------------------------------------------
# Public conversion helpers
# ---------------------------------------------------------------------------

def nfs4ace_dict_to_obj(ace: dict) -> 'xnas_os.NFS4Ace':
    """Convert a middleware NFS4 ACE dict to a xnas_os.NFS4Ace object."""
    tag = ace['tag']
    extra_flags = xnas_os.NFS4Flag(0)
    if who_type := _NFS4_TAG_TO_WHO.get(tag):
        who_id = -1
    elif tag == 'USER':
        who_type, who_id = xnas_os.NFS4Who.NAMED, ace['id']
    elif tag == 'GROUP':
        who_type, who_id = xnas_os.NFS4Who.NAMED, ace['id']
        extra_flags = xnas_os.NFS4Flag.IDENTIFIER_GROUP
    else:
        raise ValueError(f'{tag!r}: unknown NFS4 ACE tag')

    ace_type = xnas_os.NFS4AceType.ALLOW if ace['type'] == 'ALLOW' else xnas_os.NFS4AceType.DENY

    perms = ace['perms']
    if 'BASIC' in perms:
        if (access_mask := _NFS4_BASIC_PERMS.get(perms['BASIC'])) is None:
            raise ValueError(f'{perms["BASIC"]!r}: unknown BASIC permission')
    else:
        access_mask = _perm_dict_to_obj(perms)

    flags_in = ace.get('flags', {})
    if 'BASIC' in flags_in:
        if (ace_flags := _NFS4_BASIC_FLAGS.get(flags_in['BASIC'])) is None:
            raise ValueError(f'{flags_in["BASIC"]!r}: unknown BASIC flag')
    else:
        ace_flags = _flags_dict_to_obj(flags_in)

    return xnas_os.NFS4Ace(ace_type, ace_flags | extra_flags, access_mask, who_type, who_id)


def nfs4acl_dict_to_obj(acl_list: list, aclflags: dict | None) -> 'xnas_os.NFS4ACL':
    """Convert a list of middleware NFS4 ACE dicts to a xnas_os.NFS4ACL."""
    acl_flag_obj = xnas_os.NFS4ACLFlag(0)
    if aclflags:
        for key, flag in _NFS4_ACL_FLAGS.items():
            if aclflags.get(key):
                acl_flag_obj |= flag
    return xnas_os.NFS4ACL.from_aces([nfs4ace_dict_to_obj(ace) for ace in acl_list], acl_flag_obj)


def nfs4acl_obj_to_dict(acl: 'xnas_os.NFS4ACL', uid: int, gid: int, simplified: bool) -> dict:
    """Convert a xnas_os.NFS4ACL to the middleware API dict format."""
    ace_list = []
    for ace in acl.aces:
        ace_flags = ace.ace_flags
        if tag := _NFS4_WHO_TO_TAG.get(ace.who_type):
            out_id = -1
        elif ace_flags & xnas_os.NFS4Flag.IDENTIFIER_GROUP:
            tag, out_id = 'GROUP', ace.who_id
        else:
            tag, out_id = 'USER', ace.who_id

        perm = ace.access_mask
        if simplified and (basic := _NFS4_BASIC_PERMS_REV.get(perm)):
            perms_dict = {'BASIC': basic}
        else:
            perms_dict = _perm_obj_to_full_dict(perm)

        clean_flags = ace_flags & ~xnas_os.NFS4Flag.IDENTIFIER_GROUP
        if simplified and (basic_flag := _NFS4_BASIC_FLAGS_REV.get(clean_flags)):
            flags_dict = {'BASIC': basic_flag}
        else:
            flags_dict = _flags_obj_to_dict(clean_flags)

        ace_list.append({
            'tag': tag, 'id': out_id, 'type': ace.ace_type.name,
            'perms': perms_dict,
            'flags': flags_dict,
        })

    return {
        'uid': uid, 'gid': gid,
        'aclflags': {k: bool(acl.acl_flags & v) for k, v in _NFS4_ACL_FLAGS.items()},
        'trivial': acl.trivial,
        'acl': ace_list,
    }


def posixace_dict_to_obj(ace: dict) -> 'xnas_os.POSIXAce':
    """Convert a middleware POSIX ACE dict to a xnas_os.POSIXAce object."""
    perm_obj = xnas_os.POSIXPerm(0)
    for n in _POSIX_PERM_NAMES:
        if ace['perms'].get(n):
            perm_obj |= getattr(xnas_os.POSIXPerm, n)
    ace_id = -1 if (v := ace.get('id')) is None else v
    return xnas_os.POSIXAce(xnas_os.POSIXTag[ace['tag']], perm_obj, ace_id, bool(ace.get('default', False)))


def posixacl_dict_to_obj(acl_list: list) -> 'xnas_os.POSIXACL':
    """Convert a list of middleware POSIX ACE dicts to a xnas_os.POSIXACL."""
    return xnas_os.POSIXACL.from_aces([posixace_dict_to_obj(ace) for ace in acl_list])


def posixacl_obj_to_dict(acl: 'xnas_os.POSIXACL', uid: int, gid: int) -> dict:
    """Convert a xnas_os.POSIXACL to the middleware API dict format."""
    def _ace_to_dict(ace):
        return {
            'default': ace.default, 'tag': ace.tag.name, 'id': ace.id,
            'perms': {n: bool(ace.perms & getattr(xnas_os.POSIXPerm, n)) for n in _POSIX_PERM_NAMES},
        }
    return {
        'uid': uid, 'gid': gid, 'trivial': acl.trivial,
        'acl': [_ace_to_dict(ace) for ace in (*acl.aces, *acl.default_aces)],
    }


def strip_acl_path(path: str) -> None:
    fd = xnas_os.openat2(path, flags=os.O_RDONLY, resolve=xnas_os.RESOLVE_NO_SYMLINKS)
    try:
        xnas_os.fsetacl(fd, None)
    finally:
        os.close(fd)

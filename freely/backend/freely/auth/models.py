"""Authentication models."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from freely.models import Organization, User, UserSession


# Subject types
class SubjectType(str, Enum):
    """Types of authenticated subjects."""

    USER = "user"
    ORGANIZATION = "organization"
    ANONYMOUS = "anonymous"


# Generic subject type variable
S = TypeVar("S", "User", "Organization", "Anonymous")


class Anonymous:
    """Anonymous (unauthenticated) subject."""

    def __repr__(self) -> str:
        return "<Anonymous>"


@dataclass
class AuthSubject(Generic[S]):
    """
    Authentication subject.

    Represents an authenticated entity (User, Organization, or Anonymous)
    with associated session information.
    """

    subject: S
    session: "UserSession | None" = None

    @property
    def is_user(self) -> bool:
        """Check if subject is a User."""
        from freely.models import User

        return isinstance(self.subject, User)

    @property
    def is_organization(self) -> bool:
        """Check if subject is an Organization."""
        from freely.models import Organization

        return isinstance(self.subject, Organization)

    @property
    def is_anonymous(self) -> bool:
        """Check if subject is Anonymous."""
        return isinstance(self.subject, Anonymous)

    def __repr__(self) -> str:
        return f"<AuthSubject subject={self.subject}>"


# Type guards for better type narrowing
def is_user(auth_subject: AuthSubject) -> bool:
    """Type guard for User subject."""
    from freely.models import User

    return isinstance(auth_subject.subject, User)


def is_organization(auth_subject: AuthSubject) -> bool:
    """Type guard for Organization subject."""
    from freely.models import Organization

    return isinstance(auth_subject.subject, Organization)


def is_anonymous(auth_subject: AuthSubject) -> bool:
    """Type guard for Anonymous subject."""
    return isinstance(auth_subject.subject, Anonymous)

from django.contrib.auth.models import User
from django.db import models


class Team(models.Model):
    """A user-created team that controls access to data files."""

    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(User, related_name="teams")


class AccessLevel(models.IntegerChoices):
    PUBLIC = 1, "Public"
    AUTHENTICATED = 2, "Authenticated"
    PRIVATE = 3, "Private"
    TEAM = 4, "Team"


class DataFile(models.Model):
    """Represents a file with controlled access levels."""

    name = models.CharField(max_length=255)
    access_level = models.PositiveSmallIntegerField(
        choices=AccessLevel.choices, default=AccessLevel.PRIVATE, db_index=True
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="data_files")
    teams = models.ManyToManyField(Team, blank=True, related_name="data_files")

    class Meta:
        indexes = [
            models.Index(fields=["access_level"]),
        ]

    def is_accessible_by(self, user: User) -> bool:
        """Check if the user has access to this file."""
        if self.access_level == AccessLevel.PUBLIC:
            return True
        if self.access_level == AccessLevel.AUTHENTICATED and user.is_authenticated:
            return True
        if self.access_level == AccessLevel.PRIVATE and self.owner == user:
            return True
        if (
            self.access_level == AccessLevel.TEAM
            and self.teams.filter(members=user).exists()
        ):
            return True
        return False

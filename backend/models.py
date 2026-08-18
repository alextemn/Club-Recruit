import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from backend.managers import UserManager


class UserType(models.TextChoices):
    STUDENT = "STUDENT", "Student"
    CLUB_ADMIN = "CLUB_ADMIN", "Club admin"


class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    NONBINARY = "NONBINARY", "Nonbinary"
    UNDISCLOSED = "UNDISCLOSED", "Undisclosed"


class ApplicationStatus(models.TextChoices):
    NOT_STARTED = "NOT_STARTED", "Not started"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    SUBMITTED = "SUBMITTED", "Submitted"
    IN_REVIEW = "IN_REVIEW", "In review"
    INTERVIEW = "INTERVIEW", "Interview"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"


class Club(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=UserType.choices)
    grad_year = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.UNDISCLOSED,
    )
    club = models.ForeignKey(
        Club,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="admins",
    )
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["firstname", "lastname", "type"]

    class Meta:
        indexes = [
            models.Index(fields=["grad_year", "gender"]),
        ]

    def __str__(self):
        return self.email


class Application(models.Model):
    club = models.OneToOneField(
        Club,
        on_delete=models.CASCADE,
        related_name="application",
    )
    year = models.PositiveSmallIntegerField()
    questions = models.JSONField(default=list)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.club} ({self.year})"


class StudentApplication(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="student_applications",
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    answers = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.NOT_STARTED,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "club"],
                name="one_app_per_student_per_club",
            ),
        ]
        indexes = [
            models.Index(fields=["club", "status"]),
            models.Index(fields=["club", "submitted_at"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.club}"

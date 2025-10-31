from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files import File


# ==============================
# User Profile
# ==============================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Basic Info
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    courtesy = models.CharField(max_length=10, blank=True)  # Mr, Mrs, Dr
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    password = models.CharField(max_length=128, blank=True)
    user_type = models.CharField(
        max_length=20,
        choices=[("Admin", "Admin"), ("User", "User")],
        default="User"
    )

    # Additional Details
    blood_group = models.CharField(max_length=5, blank=True)
    rotary_club = models.CharField(max_length=100, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    wedding_date = models.DateField(null=True, blank=True)

    # Business & Education
    business_name = models.CharField(max_length=150, blank=True)
    business_category = models.CharField(max_length=100, blank=True)
    educational_qualification = models.CharField(max_length=150, blank=True)

    # Addresses
    office_address = models.TextField(blank=True)
    resident_address = models.TextField(blank=True)

    # RMB & Social Media
    is_rmb_member = models.BooleanField(default=False)
    joined_rmb_date = models.DateField(null=True, blank=True)
    facebook_link = models.URLField(blank=True)
    linkedin_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"


# ==============================
# Editable Pages (like About, Contact, Leadership)
# ==============================
class EditablePage(models.Model):
    slug = models.SlugField(unique=True)  # e.g., 'about', 'contact', 'leadership'
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


# ==============================
# Contact Form Messages
# ==============================
class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ==============================
# Sponsorship
# ==============================
class Sponsorship(models.Model):
    company = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    sponsorship = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.sponsorship}"


# ==============================
# Leadership & Committees
# ==============================
class LeadershipTeam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.designation}"


class LeadershipCommittee(models.Model):
    title = models.CharField(max_length=150)
    members = models.ManyToManyField(User, related_name="committees")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ==============================
# Directory PDF Upload
# ==============================
class DirectoryPDF(models.Model):
    title = models.CharField(max_length=255, default="RMB Directory PDF")
    pdf_file = models.FileField(upload_to="directory_pdfs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ==============================
# About Page & Team Members
# ==============================
class AboutPage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to="team_pictures/")

    def __str__(self):
        return self.name

from django.db import models
from django.contrib.auth.models import User


class Designation(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title


class AboutPageEditor(models.Model):
    title = models.CharField(max_length=200, default="About RMB Numero Uno")
    description = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "About Page Editor"


class TeamMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="team_pictures/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.designation.title if self.designation else 'N/A'}"


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    
import qrcode
from io import BytesIO
from django.core.files import File
class Attendance(models.Model):
    STATUS_CHOICES = (
        ("absent", "Absent"),
        ("present", "Present"),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendances")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    # Keep old boolean if you want; maintain compatibility with serializers using `status`
    is_present = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="absent")
    marked_at = models.DateTimeField(null=True, blank=True)
    qr_code = models.ImageField(upload_to="qrcodes/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user")

    def generate_qr_code(self):
        """Generate a QR code that contains the mark-attendance endpoint URL for this event.
           We don't embed user id or token in the QR for security; the app will send auth header."""
        # URL points to endpoint that accepts POST to mark attendance for event id.
        # It does not include user info or token.
        qr_data = f"http://127.0.0.1:8000/api/attendance/{self.event.id}/mark/"
        qr_img = qrcode.make(qr_data)
        qr_io = BytesIO()
        qr_img.save(qr_io, "PNG")
        qr_io.seek(0)
        file_name = f"event_{self.event.id}_user_{self.user.id}.png"
        self.qr_code.save(file_name, File(qr_io), save=False)

    def mark_present(self):
        self.is_present = True
        self.status = "present"
        self.marked_at = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        # Generate QR on create if not present
        if not self.qr_code:
            try:
                self.generate_qr_code()
            except Exception:
                # don't break save if QR generation fails for any reason
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"








# models.py
from django.db import models
from django.contrib.auth.models import User

class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=255)
    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



# ==============================
# Knowledge Centre
# ==============================
class KnowledgeItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ("folder", "Folder"),
        ("file", "File"),
    ]

    name = models.CharField(max_length=255)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, default="folder")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )
    file = models.FileField(upload_to="knowledge_centre/", null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


from django.db import models

class GalleryImage(models.Model):
    CATEGORY_CHOICES = [
        ('members', 'Members'),
        ('events', 'Events'),
        ('one_to_ones', '1:1s'),
        ('guests', 'Guests'),
    ]
    image = models.ImageField(upload_to='gallery/')
    title = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.title or self.image.name}"


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class D2DConnect(models.Model):
    from_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="d2d_from_member")
    to_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="d2d_to_member")
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"D2D: {self.from_member.username} -> {self.to_member.username}"

class BusinessGiven(models.Model):
    from_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_given_from")
    to_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_given_to")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Given: {self.from_member.username} -> {self.to_member.username} ({self.amount})"

class BusinessReceived(models.Model):
    from_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_received_from")
    to_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_received_to")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Received: {self.from_member.username} <- {self.to_member.username} ({self.amount})"

class ReferralGiven(models.Model):
    from_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referral_from_member")
    to_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referral_to_member")
    contact_name = models.CharField(max_length=255)
    contact_no = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Referral: {self.from_member.username} -> {self.to_member.username} ({self.contact_name})"


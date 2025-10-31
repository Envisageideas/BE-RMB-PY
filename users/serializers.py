from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, EditablePage


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = [
            "courtesy", "blood_group", "rotary_club", "business_name",
            "business_category", "educational_qualification",
            "office_address", "resident_address", "birthdate",
            "wedding_date", "joined_rmb_date", "facebook_link", "linkedin_link",
            "instagram_link", "mobile", "is_rmb_member", "profile_picture"
        ]



class EditablePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditablePage
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    mobile = serializers.CharField(source="profile.mobile", read_only=False,required=False)
    user_type = serializers.CharField(source="profile.user_type", read_only=True)
    profile_picture = serializers.ImageField(source="profile.profile_picture", required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile",
            "mobile",
            "user_type",
            "profile_picture",
            "is_active",
        )
        extra_kwargs = {
            "username": {"read_only": True},
            "email": {"required": True},
        }

    
    def create(self, validated_data):
        profile_data = validated_data.pop("profile", {})
        password = self.context["request"].data.get("password")
        email = validated_data.get("email")
        username = email

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        user = User(username=username, **validated_data)
        if password:
            user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update UserProfile
        profile = getattr(instance, "profile", None)
        if profile_data:
            if profile:
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()
            else:
                UserProfile.objects.create(user=instance, **profile_data)
        return instance


from rest_framework import serializers
from .models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "message", "created_at"]



from .models import Sponsorship

class SponsorshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsorship
        fields = '__all__'


# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import LeadershipTeam, LeadershipCommittee

class UserMiniSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source="profile.profile_picture", read_only=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "profile_picture"]


class LeadershipTeamSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = LeadershipTeam
        fields = ["id", "user", "user_id", "designation", "created_at"]


class LeadershipCommitteeSerializer(serializers.ModelSerializer):
    members = UserMiniSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), source="members", write_only=True
    )

    class Meta:
        model = LeadershipCommittee
        fields = ["id", "title", "members", "member_ids", "created_at"]


from rest_framework import serializers
from .models import DirectoryPDF

class DirectoryPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirectoryPDF
        fields = '__all__'


from rest_framework import serializers
from .models import AboutPage, TeamMember


class AboutPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutPage
        fields = '__all__'


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'

from rest_framework import serializers
from .models import AboutPage

class AboutPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutPage
        fields = '__all__'

from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"












from rest_framework import serializers
from .models import Event, Attendance
from django.contrib.auth import get_user_model
class AttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'user', 'event', 'status', 'marked_at', 'qr_code']


class EventWithAttendanceSerializer(serializers.ModelSerializer):
    attendance_records = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'attendance_records']

    def get_attendance_records(self, obj):
        attendance = Attendance.objects.filter(event=obj)
        return AttendanceSerializer(attendance, many=True).data




















# serializers.py
from rest_framework import serializers
from .models import Testimonial
from django.contrib.auth.models import User

class TestimonialSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Testimonial
        fields = ['id', 'user', 'name', 'profile_picture', 'company', 'text']

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_profile_picture(self, obj):
        return obj.user.profile.profile_picture.url if obj.user.profile.profile_picture else None


from .models import KnowledgeItem

class KnowledgeItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = KnowledgeItem
        fields = ['id', 'name', 'item_type', 'parent', 'file', 'children', 'created_at']

    def get_children(self, obj):
        if obj.item_type == "folder":
            return KnowledgeItemSerializer(obj.children.all(), many=True).data
        return []


from rest_framework import serializers
from .models import GalleryImage

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = '__all__'


from rest_framework import serializers
from .models import D2DConnect, BusinessGiven, BusinessReceived, ReferralGiven

class D2DSerializer(serializers.ModelSerializer):
    class Meta:
        model = D2DConnect
        fields = '__all__'

class BusinessGivenSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessGiven
        fields = '__all__'

class BusinessReceivedSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessReceived
        fields = '__all__'

class ReferralGivenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralGiven
        fields = '__all__'



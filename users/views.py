from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets, permissions, status, generics
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import EditablePage, LeadershipTeam, LeadershipCommittee, DirectoryPDF, ContactMessage, Sponsorship
from .serializers import EditablePageSerializer, LeadershipTeamSerializer, LeadershipCommitteeSerializer, DirectoryPDFSerializer, ContactMessageSerializer, SponsorshipSerializer
# Import all models & serializers
from .models import (
    UserProfile,
    EditablePage,
    ContactMessage,
    Sponsorship,
    LeadershipTeam,
    LeadershipCommittee,
    DirectoryPDF,
)
from .serializers import (
    UserSerializer,
    EditablePageSerializer,
    ContactMessageSerializer,
    SponsorshipSerializer,
    LeadershipTeamSerializer,
    LeadershipCommitteeSerializer,
    DirectoryPDFSerializer,
)

# =====================================================
# 🧍 USER & AUTH
# =====================================================

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth.models import User
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.db import transaction

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Open registration

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        files = request.FILES

        profile_fields = [
            "courtesy", "mobile", "user_type", "blood_group", "rotary_club",
            "birthdate", "wedding_date", "business_name", "business_category",
            "educational_qualification", "office_address", "resident_address",
            "is_rmb_member", "facebook_link", "linkedin_link", "instagram_link",
            "joined_rmb_date", "profile_picture"
        ]

        profile_data = {k: data.get(k) for k in profile_fields if k in data}

        if "profile_picture" in files:
            profile_data["profile_picture"] = files["profile_picture"]

        # Convert boolean fields
        if "is_rmb_member" in profile_data:
            profile_data["is_rmb_member"] = str(profile_data["is_rmb_member"]).lower() in ("1", "true", "yes", "on")

        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        user_type = profile_data.get("user_type", "User")

        try:
            with transaction.atomic():
                # Create Django User
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )

                # Set staff/admin status
                if user_type == "Admin":
                    user.is_staff = True      # Admin dashboard access
                    user.is_superuser = False  # Optional: set True if full superuser
                user.save()

                # Create Profile
                UserProfile.objects.create(
                    user=user,
                    **profile_data
                )

            # Serialize response
            serializer = self.get_serializer(user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        return Response({"token": token.key, "user": user_data}, status=status.HTTP_200_OK)

# =====================================================
# 🧾 EDITABLE PAGES
# =====================================================

class EditablePageViewSet(viewsets.ModelViewSet):
    queryset = EditablePage.objects.all()
    serializer_class = EditablePageSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


# =====================================================
# ✉️ CONTACT MESSAGE
# =====================================================

class ContactMessageView(generics.ListCreateAPIView):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
            if self.request.method == "POST":
                return [AllowAny()]  # Allow users to submit contact form
            elif self.request.method == "GET":
                return [AllowAny()]  # Allow viewing messages without auth
            return super().get_permissions()
# =====================================================
# 💰 SPONSORSHIP
# =====================================================

class SponsorshipView(generics.ListCreateAPIView):
    queryset = Sponsorship.objects.all().order_by('-created_at')
    serializer_class = SponsorshipSerializer
    permission_classes = [permissions.AllowAny]
    def get_permissions(self):
            if self.request.method == "POST":
                return [AllowAny()]  # Allow users to submit contact form
            elif self.request.method == "GET":
                return [AllowAny()]  # Allow viewing messages without auth
            return super().get_permissions()

# =====================================================
# 👥 LEADERSHIP TEAM & COMMITTEE
# =====================================================

class LeadershipTeamView(generics.ListCreateAPIView):
    queryset = LeadershipTeam.objects.all().select_related("user")
    serializer_class = LeadershipTeamSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class LeadershipCommitteeView(generics.ListCreateAPIView):
    queryset = LeadershipCommittee.objects.all().prefetch_related("members")
    serializer_class = LeadershipCommitteeSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class LeadershipTeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeadershipTeam.objects.all().select_related("user")
    serializer_class = LeadershipTeamSerializer
    permission_classes = [permissions.IsAuthenticated]

class LeadershipCommitteeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeadershipCommittee.objects.all().prefetch_related("members")
    serializer_class = LeadershipCommitteeSerializer
    permission_classes = [permissions.IsAuthenticated]
# =====================================================
# 📂 DIRECTORY PDF MANAGEMENT
# =====================================================

# =====================================================
# 📂 DIRECTORY PDF MANAGEMENT
# =====================================================

from rest_framework.parsers import MultiPartParser, FormParser

class DirectoryPDFViewSet(viewsets.ModelViewSet):
    """
    Handles listing, uploading, and deleting directory PDFs.
    - Public can GET
    - Authenticated users (admin) can POST/DELETE
    """
    queryset = DirectoryPDF.objects.all().order_by('-uploaded_at')
    serializer_class = DirectoryPDFSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import AboutPage, TeamMember
from .serializers import AboutPageSerializer, TeamMemberSerializer


class AboutPageViewSet(viewsets.ModelViewSet):
    queryset = AboutPage.objects.all()
    serializer_class = AboutPageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.perform_update(serializer)
        return Response(serializer.data)


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticatedOrReadOnly]






from rest_framework import viewsets
from .models import AboutPage
from .serializers import AboutPageSerializer

class AboutPageViewSet(viewsets.ModelViewSet):
    queryset = AboutPage.objects.all()
    serializer_class = AboutPageSerializer



from rest_framework import viewsets, permissions
from .models import Event
from .serializers import EventSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Attendance, Event
from .serializers import AttendanceSerializer
from datetime import date

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().select_related('user', 'event')
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically assign the current user
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark(self, request, pk=None):
        """
        ✅ Mark attendance for the logged-in user for the event (pk=event id)
        ✅ Only allowed if the event date is today
        """
        user = request.user
        event = get_object_or_404(Event, id=pk)

        # ✅ Check event date
        today_str = date.today().isoformat()
        if str(event.date) != today_str:
            return Response(
                {"error": "Attendance can only be marked for today's event."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Check if already marked
        attendance, created = Attendance.objects.get_or_create(
            user=user,
            event=event,
            defaults={"status": "present"}
        )

        if not created:
            return Response(
                {"message": "Attendance already marked for this event."},
                status=status.HTTP_200_OK,
            )

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# views.py
from rest_framework import viewsets
from .models import Testimonial
from .serializers import TestimonialSerializer

class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all().order_by('-id')
    serializer_class = TestimonialSerializer


from rest_framework import viewsets
from .models import KnowledgeItem
from .serializers import KnowledgeItemSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class KnowledgeItemViewSet(viewsets.ModelViewSet):
    queryset = KnowledgeItem.objects.all()
    serializer_class = KnowledgeItemSerializer
    permission_classes = [permissions.AllowAny]


from rest_framework import viewsets
from .models import GalleryImage
from .serializers import GalleryImageSerializer

class GalleryImageViewSet(viewsets.ModelViewSet):
    queryset = GalleryImage.objects.all().order_by('-uploaded_at')
    serializer_class = GalleryImageSerializer





from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import D2DConnect, BusinessGiven, BusinessReceived, ReferralGiven
from .serializers import D2DSerializer, BusinessGivenSerializer, BusinessReceivedSerializer, ReferralGivenSerializer
from django.http import JsonResponse
from django.utils import timezone
# Common helper
def handle_crud(request, model, serializer_class):
    if request.method == 'GET':
        objs = model.objects.all()
        serializer = serializer_class(objs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def d2d_list_create(request):
    return handle_crud(request, D2DConnect, D2DSerializer)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def business_given_list_create(request):
    return handle_crud(request, BusinessGiven, BusinessGivenSerializer)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def business_received_list_create(request):
    return handle_crud(request, BusinessReceived, BusinessReceivedSerializer)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def referral_given_list_create(request):
    return handle_crud(request, ReferralGiven, ReferralGivenSerializer)

# 🆕 New detail views (update/delete)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def referral_detail(request, category, pk):
    model_map = {
        "d2d": (D2DConnect, D2DSerializer),
        "given": (BusinessGiven, BusinessGivenSerializer),
        "received": (BusinessReceived, BusinessReceivedSerializer),
        "referral": (ReferralGiven, ReferralGivenSerializer),
    }

    model_class, serializer_class = model_map.get(category, (None, None))
    if not model_class:
        return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        obj = model_class.objects.get(pk=pk)
    except model_class.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = serializer_class(obj)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = serializer_class(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)













# users/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Event, Attendance
from .serializers import AttendanceSerializer, EventSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


# EventWithAttendance view as before, using IsAuthenticated
class EventWithAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .serializers import EventWithAttendanceSerializer
        events = Event.objects.all()
        serializer = EventWithAttendanceSerializer(events, many=True)
        return Response(serializer.data)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from .models import Attendance, Event
from .serializers import AttendanceSerializer
from .serializers import AttendanceSerializer, EventSerializer, EventWithAttendanceSerializer
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_with_attendance(request):
    events = Event.objects.all()
    serializer = EventWithAttendanceSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def mark_attendance(request, pk):
    """
    POST → Mark attendance for logged-in user for a specific event.
    GET → Check if attendance already marked.
    """
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    attendance, created = Attendance.objects.get_or_create(event=event, user=user)

    if request.method == 'POST':
        # Mark as present with timestamp
        attendance.status = 'present'
        attendance.is_present = True
        attendance.marked_at = timezone.now()
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)




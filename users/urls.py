from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from .views import AboutPageViewSet
from .views import TestimonialViewSet
from .views import EventViewSet
from .views import mark_attendance
from .views import GalleryImageViewSet
from .views import EventWithAttendanceView
from .views import EventViewSet, AttendanceViewSet
from .views import KnowledgeItemViewSet
from .views import AboutPageViewSet, TeamMemberViewSet
from .views import EditablePageViewSet, LeadershipTeamView, LeadershipCommitteeView, DirectoryPDFViewSet, ContactMessageView, SponsorshipView
from .views import (
    UserViewSet,
    MeAPIView,
    EditablePageViewSet,
    LoginView,
    ContactMessageView,
    SponsorshipView,
    LeadershipTeamView,
    LeadershipTeamDetailView,
    LeadershipCommitteeView,
    DirectoryPDFViewSet,
    AboutPageViewSet, TestimonialViewSet, EventViewSet, GalleryImageViewSet,
    EventWithAttendanceView, AttendanceViewSet, mark_attendance, ContactMessageView,
    SponsorshipView, LeadershipTeamView, LeadershipTeamDetailView, LeadershipCommitteeView,
    DirectoryPDFViewSet, UserViewSet, MeAPIView, LoginView
)
from .views import LeadershipCommitteeDetailView
# =====================================================
# Routers
# =====================================================
from . import views
router = DefaultRouter()
router.register(r'attendance', AttendanceViewSet, basename='attendance')

router.register(r"users", UserViewSet, basename="user")
router.register(r"pages", EditablePageViewSet, basename="editablepage")
router.register(r"directory", DirectoryPDFViewSet, basename="directory")
router.register(r'about', AboutPageViewSet, basename='about')
router.register(r'events', EventViewSet, basename='event')
router.register(r'testimonials', TestimonialViewSet, basename='testimonial')
router.register(r'knowledge-centre', KnowledgeItemViewSet, basename='knowledge-centre')
router.register('gallery', GalleryImageViewSet, basename='gallery')



# =====================================================
# URL Patterns
# =====================================================

urlpatterns = [
    # 🔐 Auth & Users
    path('attendance/<int:pk>/mark/', mark_attendance, name='mark-attendance'),
    path('api/', include(router.urls)),
    path("login/", LoginView.as_view(), name="login"),
    path("users/me/", MeAPIView.as_view(), name="user-me"),
    path("api/users/me/", MeAPIView.as_view(), name="user-me"),
    # 🔄 Include router endpoints (users, pages, directory)
    path("", include(router.urls)),
    path('referrals/d2d/', views.d2d_list_create),
    path('referrals/given/', views.business_given_list_create),
    path('referrals/received/', views.business_received_list_create),
    path('referrals/referral/', views.referral_given_list_create),
    path('referrals/<str:category>/<int:pk>/', views.referral_detail),
    #path("attendance/<int:pk>/mark/", mark_attendance, name="attendance-mark-attendance"),
    #path('api/attendance/<int:pk>/mark/', views.mark_attendance, name='mark-attendance'),
    #path("api/attendance/", views.attendance_list, name="attendance-list"),
    # ✉️ Contact and Sponsorship
    path("contact/", ContactMessageView.as_view(), name="contact"),
    path("api/contact/", ContactMessageView.as_view(), name="contact-alt"),
    path("sponsorship/", SponsorshipView.as_view(), name="sponsorship"),
    path('api/', include(router.urls)),
    # 👥 Leadership
    path("leadership/team/", LeadershipTeamView.as_view(), name="leadership-team"),
    path("leadership/team/<int:pk>/", LeadershipTeamDetailView.as_view(), name="leadership-team-detail"),
    path("leadership/committee/", LeadershipCommitteeView.as_view(), name="leadership-committee"),
    path("leadership/committee/<int:pk>/",LeadershipCommitteeDetailView.as_view(),name="leadership-committee-detail"),

    path('events-with-attendance/', EventWithAttendanceView.as_view(), name='events-with-attendance'),
]

# =====================================================
# 🖼️ MEDIA FILE SERVING (For PDFs)
# =====================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



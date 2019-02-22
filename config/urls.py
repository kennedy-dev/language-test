from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.views import defaults as default_views
from testapp.views import RecordPage, RecordSuccessPage, AnalystPage, StatisticsPage
from language.users.views import user_create_view, password_change_view

from django.conf.urls import url


urlpatterns = [
    path("", RedirectView.as_view(url="/accounts/login/"), name="home"),
    path("record/", RecordPage.as_view(), name="record"),
    path("analyst/", AnalystPage.as_view(), name="analyst"),
    path("statistics/", StatisticsPage.as_view(), name="stats"),
    path("success/", RecordSuccessPage.as_view(), name="success"),
    path(
        "about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    url(r'^admin/', admin.site.urls),
    # User management
    path(
        "users/",
        include("language.users.urls", namespace="users"),
    ),
    path("accounts/signup/", view=user_create_view, name="signup"),
    path("accounts/password/reset/key/2-set-password/", view=password_change_view, name="change_password"),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

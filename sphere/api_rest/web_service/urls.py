"""api_sphere URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
try:
    from sphere.settings import START_ANNOTATION, START_DICOMWEB
except ImportError:
    START_DICOMWEB = START_ANNOTATION = True

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

if START_ANNOTATION:
    from api_annotation.views import SaveAnnotationView
if START_DICOMWEB:
    from api_sphere_dicomweb.views import AllInstancesView, AllSeriesView, \
        AllInstancesOfStudyView, AllInstancesOfSeriesOfStudyView , \
        AllStudiesView, AllSeriesOfStudyView, DCMInstancesOfSeriesView, \
        MetadataSeriesView, MetadataInstanceView, DCMInstanceView, \
        MetadataStudyView, DCMInstancesOfSeriesOfStudyView, InstanceFrameView

swagger_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="""**SphereDicomWeb**
      SphereDicomWeb is an DICOMweb server that implements RESTful services in DICOM.
      Below is the API documentation of the DICOM Web Services implemented by the SphereDicomWeb server.
      """,
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="ossama.achouri-ext@aphp.fr"),
      license=openapi.License(name="Test License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # =============================== Swagger =========================== #
    url(r'^swagger(?P<format>\.json|\.yaml)$', swagger_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', swagger_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', swagger_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if START_DICOMWEB:
    urlpatterns.extend([
        # ============================== Admin ============================== #
        path('admin/', admin.site.urls),

        # ========================= SphereDicomWeb ========================== #
        # === QIDO_RS === #
        # Link: /qidors/series
        path('qidors/series', AllSeriesView.as_view()),
        # Link: /qidors/studies
        path('qidors/studies', AllStudiesView.as_view()),
        # Link: /qidors/instances
        path('qidors/instances', AllInstancesView.as_view()),
        # Link: /qidors/studies/{StudyInstanceUID}/instances
        path('qidors/studies/<study_uid>/instances', AllInstancesOfStudyView.as_view()),
        # Link: /qidors/studies/{StudyInstanceUID}/series
        path('qidors/studies/<study_uid>/series', AllSeriesOfStudyView.as_view()),
        # Link: /qidors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances
        path('qidors/studies/<study_uid>/series/<series_uid>/instances', AllInstancesOfSeriesOfStudyView.as_view()),

        # === WADO_RS === #
        # Link: /wadors/studies/{StudyInstanceUID}/metadata
        path('wadors/studies/<study_uid>/metadata', MetadataStudyView.as_view()),
        # Link: /wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/metadata
        path('wadors/studies/<study_uid>/series/<series_uid>/metadata', MetadataSeriesView.as_view()),
        # Link: /wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances/{SOPInstanceUID}/metadata
        path('wadors/studies/<study_uid>/series/<series_uid>/instances/<instance_uid>/metadata', MetadataInstanceView.as_view()),
        # Link: /wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances/{SOPInstanceUID}
        path('wadors/studies/<study_uid>/series/<series_uid>/instances/<instance_uid>', DCMInstanceView.as_view()),
        # Link: /wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}
        path('wadors/studies/<study_uid>/series/<series_uid>', DCMInstancesOfSeriesView.as_view()),
        # Link: /wadors/studies/{StudyInstanceUID}
        path('wadors/studies/<study_uid>', DCMInstancesOfSeriesOfStudyView.as_view()),
        # Link: /wadors/studies/{StudyInstanceUID}/series/{SeriesInstanceUID}/instances/{SOPInstanceUID}/frames/{frame}
        path(
            'wadors/studies/<study_uid>/series/<series_uid>/instances/<instance_uid>/frames/<frame>',
            InstanceFrameView.as_view()),
    ])

if START_ANNOTATION:
    # ============================ Annotation ============================== #
    urlpatterns.append(path('save_annotation/', SaveAnnotationView.as_view()))

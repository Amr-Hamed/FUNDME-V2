from django.contrib import admin
# Register your models here.

from userProfile.models import Categories, ProjectPics, ProjectTags, ProjectReports, ProjectRatings, \
    ProjectComments, ProjectDonations, Project, UserProfile, User

admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(Categories)
admin.site.register(ProjectPics)
admin.site.register(ProjectTags)
admin.site.register(ProjectReports)
admin.site.register(ProjectRatings)
admin.site.register(ProjectComments)
admin.site.register(ProjectDonations)
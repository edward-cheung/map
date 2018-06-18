from django.contrib import admin
from topic.models import User, Tag, Topic, Comment, Good, Image

# Register your models here.
admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Topic)
admin.site.register(Comment)
admin.site.register(Good)
admin.site.register(Image)

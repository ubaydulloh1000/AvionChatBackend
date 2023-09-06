from apps.base.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from ckeditor_uploader.fields import RichTextUploadingField


class PostCategory(TimeStampedModel, MPTTModel):
    class Meta:
        db_table = "post_categories"
        verbose_name = _("Post Category")
        verbose_name_plural = _("Post Categories")

    name = models.CharField(verbose_name=_("Name"), max_length=255)
    parent = TreeForeignKey(
        verbose_name=_("Parent"),
        to="self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Post(TimeStampedModel):
    class Meta:
        db_table = "posts"
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    title = models.CharField(verbose_name=_("Title"), max_length=511)
    author = models.ForeignKey(
        verbose_name=_("Author"),
        to="accounts.User",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    channel = models.ForeignKey(
        verbose_name=_("Channel"),
        to="chat.Chat",
        on_delete=models.CASCADE,
        related_name="posts",
        null=True,
    )
    category = models.ForeignKey(
        verbose_name=_("Category"),
        to="posts.PostCategory",
        on_delete=models.CASCADE,
        related_name="posts",
        null=True,
    )
    content = RichTextUploadingField(verbose_name=_("Content"))

    is_edited = models.BooleanField(verbose_name=_("Is Edited"), default=False)
    edited_at = models.DateTimeField(verbose_name=_("Edited At"), null=True, blank=True)

    def __str__(self):
        return self.title


class Tag(TimeStampedModel):
    class Meta:
        db_table = "tags"
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    name = models.CharField(verbose_name=_("Name"), max_length=255)

    def __str__(self):
        return self.name


class PostTag(TimeStampedModel):
    class Meta:
        db_table = "post_tags"
        verbose_name = _("Post Tag")
        verbose_name_plural = _("Post Tags")

    post = models.ForeignKey(
        verbose_name=_("Post"),
        to="posts.Post",
        on_delete=models.CASCADE,
        related_name="tags",
    )
    tag = models.ForeignKey(
        verbose_name=_("Tag"),
        to="posts.Tag",
        on_delete=models.CASCADE,
        related_name="posts",
    )

    def __str__(self):
        return f"{self.post} - {self.tag}"


class PostComment(TimeStampedModel):
    class Meta:
        db_table = "post_comments"
        verbose_name = _("Post Comment")
        verbose_name_plural = _("Post Comments")

    post = models.ForeignKey(
        verbose_name=_("Post"),
        to="posts.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        verbose_name=_("Author"),
        to="accounts.User",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField(verbose_name=_("Content"))
    is_edited = models.BooleanField(verbose_name=_("Is Edited"), default=False)
    edited_at = models.DateTimeField(verbose_name=_("Edited At"), null=True, blank=True)

    def __str__(self):
        return f"{self.post} - {self.author}"

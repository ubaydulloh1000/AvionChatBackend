# Generated by Django 4.2.4 on 2023-11-26 07:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0013_channelsubscription_deleted_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan sana')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Yangilangan sana')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Is deleted?')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='deleted at')),
                ('is_archived', models.BooleanField(default=False, verbose_name='Is Archived')),
                ('is_muted', models.BooleanField(default=False, verbose_name='Is Muted')),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_memberships', to='chat.chat', verbose_name='Chat')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_memberships', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Chat Membership',
                'verbose_name_plural': 'Chat Memberships',
                'db_table': 'chat_membership',
                'unique_together': {('chat', 'user')},
            },
        ),
    ]

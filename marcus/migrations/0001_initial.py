# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('marcus_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, blank=True)),
            ('title_ru', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description_ru', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title_en', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marcus.Category'], null=True, blank=True)),
            ('essential', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('marcus', ['Category'])

        # Adding model 'Tag'
        db.create_table('marcus_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, blank=True)),
            ('title_ru', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description_ru', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title_en', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('marcus', ['Tag'])

        # Adding model 'Article'
        db.create_table('marcus_article', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=200, blank=True)),
            ('title_ru', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('text_ru', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('title_en', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('text_en', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('published', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('comments_hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('marcus', ['Article'])

        # Adding M2M table for field categories on 'Article'
        db.create_table('marcus_article_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['marcus.article'], null=False)),
            ('category', models.ForeignKey(orm['marcus.category'], null=False))
        ))
        db.create_unique('marcus_article_categories', ['article_id', 'category_id'])

        # Adding M2M table for field tags on 'Article'
        db.create_table('marcus_article_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm['marcus.article'], null=False)),
            ('tag', models.ForeignKey(orm['marcus.tag'], null=False))
        ))
        db.create_unique('marcus_article_tags', ['article_id', 'tag_id'])

        # Adding model 'ArticleUpload'
        db.create_table('marcus_articleupload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(related_name='uploads', to=orm['marcus.Article'])),
            ('upload', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('marcus', ['ArticleUpload'])

        # Adding model 'Comment'
        db.create_table('marcus_comment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('article', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marcus.Article'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('guest_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('guest_email', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('guest_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(default='127.0.0.1', max_length=15)),
            ('spam_status', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True)),
            ('approved', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('noteworthy', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('marcus', ['Comment'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('marcus_category')

        # Deleting model 'Tag'
        db.delete_table('marcus_tag')

        # Deleting model 'Article'
        db.delete_table('marcus_article')

        # Removing M2M table for field categories on 'Article'
        db.delete_table('marcus_article_categories')

        # Removing M2M table for field tags on 'Article'
        db.delete_table('marcus_article_tags')

        # Deleting model 'ArticleUpload'
        db.delete_table('marcus_articleupload')

        # Deleting model 'Comment'
        db.delete_table('marcus_comment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'marcus.article': {
            'Meta': {'object_name': 'Article'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['marcus.Category']", 'symmetrical': 'False'}),
            'comments_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['marcus.Tag']", 'symmetrical': 'False'}),
            'text_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text_ru': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'marcus.articleupload': {
            'Meta': {'object_name': 'ArticleUpload'},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'uploads'", 'to': "orm['marcus.Article']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'upload': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'marcus.category': {
            'Meta': {'object_name': 'Category'},
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_ru': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'essential': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['marcus.Category']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'marcus.comment': {
            'Meta': {'object_name': 'Comment'},
            'approved': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['marcus.Article']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'guest_email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'guest_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'guest_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '15'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'noteworthy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'spam_status': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'marcus.tag': {
            'Meta': {'object_name': 'Tag'},
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_ru': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['marcus']
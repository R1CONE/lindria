from __future__ import annotations
from datetime import datetime as dt, date, timedelta
from app import db
from .dicts import Language
from .tools import DescriptionManager, Dictionary, MediafileManager, PosterManager, TitleManager


class ContentType(Dictionary): plural_title = True
class Genre(Dictionary): pass


class Mediafile(db.EmbeddedDocument):
  # size: int = db.IntField(required=True)
  language: Language = db.ReferenceField(Language, required=True)
  genres: list[Genre] = db.ListField(db.ReferenceField(Genre), default=[])
  # duration: int = db.IntField()
  # resolution: str = db.StringField(max_length=255)


class Content(db.Document, TitleManager, PosterManager, DescriptionManager):
  meta = {'allow_inheritance': True, 'ordering': ['-added_date'],
  'indexes': ['code', 'type', 'release_date', 'added_date'], }
  code: str = db.StringField(max_length=255, primary_key=True, required=True)
  type: ContentType = db.ReferenceField(ContentType, required=True)
  release_date: date = db.DateField()
  added_date: dt = db.DateTimeField(default=dt.utcnow, required=True)
  original_language: Language = db.ReferenceField(Language, required=True)
  _code_pattern: str = r'^[a-z-0-9]+$'
  
  @classmethod
  @property
  def code_pattern(cls):
    codes = [f'^{o.code}$' for o in Content.objects]
    codes = f'(?!{"|".join(codes)})' if codes else ''
    return f'{codes}{cls._code_pattern}'
  
  @property
  def self_code_pattern(self):
    codes = [f'^{o.code}$' for o in Content.objects if o.code != self.code]
    codes = f'(?!{"|".join(codes)})' if codes else ''
    return f'{codes}{self._code_pattern}'
  
  def __unicode__(self) -> str: return self.title()


class Weight(db.EmbeddedDocument):
  unit: Content = db.ReferenceField(Content, primary_key=True)
  weight: int = db.IntField(required=True)
  _view_time: float = db.FloatField(default=0)

  @property
  def view_time(self) -> timedelta:
    return timedelta(seconds=self._view_time)
  
  @view_time.setter
  def view_time(self, value: timedelta):
    self._view_time = value.total_seconds()


class Movie(Content, MediafileManager): pass


class Episode(db.EmbeddedDocument, MediafileManager, DescriptionManager, TitleManager):
  number: int = db.IntField(primary_key=True)
  release_date: dt = db.DateTimeField(required=True)
  original_language: Language = db.ReferenceField(Language, required=True)


class Season(db.EmbeddedDocument, DescriptionManager, TitleManager):
  number: int = db.IntField(primary_key=True)
  episodes: list[Episode] = db.ListField(db.EmbeddedDocumentField(Episode, unique=True), default=[])


class Series(Content):
  seasons: list[Season] = db.ListField(db.EmbeddedDocumentField(Season, unique=True), default=[])


class File(db.Document):
  name: str = db.StringField(max_length=255, required=True)
  
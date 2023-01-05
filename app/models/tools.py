from __future__ import annotations
from typing import Self
from . import _types
from app import db, DLC


class TitleManager:
  _title: str = db.StringField(max_length=255, required=True)
  _titles: list[_types.Title] = db.ListField(db.EmbeddedDocumentField(_types.Title, unique=True), default=[])
  
  def title(self, language: Language | None = None, default: bool = True) -> str:
    if language is None or language.code == DLC: return self._title
    for l in self._titles:
      if l.language == language:
        return l.title
    return self._title if default else ''
  
  def set_title(self, language: Language | None, title: str, save: bool = True) -> Self:
    if title == '': return self.remove_title(language, save) if language else self
    if language.code == DLC or language is None:
      self._title = title
      return self.save() if save else self
    for l in self._titles:
      if l.language == language:
        l.title = title
        return self.save() if save else self
    self._titles.append(_types.Title(language=language, title=title))
    return self.save() if save else self
  
  def remove_title(self, language: Language, save: bool = True):
    if language.code == DLC:
      raise ValueError(f'Cannot remove default title({language.title(language)}) from {self.__class__.__name__} object')
    for l in self._titles:
      if l.language == language:
        self._titles.remove(l)
        if save: self.save()
    return self


class PosterManager:
  _posters: list[_types.Poster] = db.ListField(db.EmbeddedDocumentField(_types.Poster), default=[])
  
  def poster(self, language: Language | None = None) -> str:
    ln_code = language.code if language else DLC
    for p in self._posters:
      if p.language.code == ln_code:
        return p.paths[0]
    return ''
  
  def posters(self, language: Language | None = None) -> list[str]:
    ln_code = language.code if language else DLC
    for p in self._posters:
      if p.language.code == ln_code:
        return p.paths
    return []
  
  def add_poster(self, language: Language, path: str, save: bool = True):
    for p in self._posters:
      if p.language == language:
        if path not in p.paths:
          p.paths.append(path)
        if save: self.save()
        return self
    self._posters.append(_types.Poster(language=language, paths=[path]))
    if save: self.save()
    return self
  
  def remove_poster(self, language: Language, path: str, save: bool = True):
    for p in self._posters:
      if p.language == language:
        if path in p.paths:
          p.paths.remove(path)
          if not p.paths:
            self._posters.remove(p)
          if save: self.save()
    return self


class DescriptionManager:
  _descriptions: list[_types.Description] = db.ListField(db.EmbeddedDocumentField(_types.Description), default=[])
  
  def description(self, language: Language | None = None) -> str:
    ln_code = language.code if language else DLC
    for d in self._descriptions:
      if d.language.code == ln_code:
        return d.description
    return ''
  
  def set_description(self, language: Language, description: str, save: bool = True):
    if description == '': return self.remove_description(language, save)
    for d in self._descriptions:
      if d.language == language:
        d.description = description
        if save: self.save()
        return self
    self._descriptions.append(_types.Description(language=language, description=description))
    if save: self.save()
    return self
  
  def remove_description(self, language: Language, save: bool = True):
    for d in self._descriptions:
      if d.language == language:
        self._descriptions.remove(d)
        if save: self.save()
    return self


class MediafileManager: pass


class Dictionary(db.Document, TitleManager, DescriptionManager):
  meta = {'abstract': True, 'allow_inheritance': True, 'ordering': ['code'], 'indexes': ['code']}
  active: bool = db.BooleanField(default=True, required=True)
  code: str = db.StringField(max_length=80, primary_key=True, required=True)
  _code_pattern: str = '^[a-z0-9_]{1,255}$'
  
  @property
  def self_code_pattern(self):
    codes = [o.code for o in self.__class__.objects if o != self]
    return self._code_pattern if not codes else f'(?!{"|".join(codes)}){self._code_pattern}'
  
  @classmethod
  @property
  def code_pattern(cls):
    codes = [o.code for o in cls.objects]
    return cls._code_pattern if not codes else f'(?!{"|".join(codes)}){cls._code_pattern}'
  
  def __unicode__(self) -> str: return self.title()
  def __str__(self) -> str: return self.title()
  def __repr__(self) -> str: return f'<{self.__class__.__name__} {self.code}>'
  def __eq__(self, other: Self) -> bool: return self.__class__ == other.__class__ and self.code == other.code
  def __ne__(self, other: Self) -> bool: return not self == other


class Language(Dictionary):
  code: str = db.StringField(max_length=5, primary_key=True)
  _code_pattern: str = '^[a-z]{2}_[A-Z]{2}$' # ISO 639-1 + ISO 3166-1 alpha-2
  self_title: str = db.StringField(max_length=255, required=True)
  
  @classmethod
  @property
  def default(cls) -> Self: return cls.objects(code=DLC).first()
  
  @classmethod
  @property
  def other(cls) -> list[Self]: return cls.objects(code__ne=DLC)
  
  def title(self, language: Language | None = None, default: bool = True) -> str:
    if language == self: return self.self_title
    return super().title(language, default)
  
  def set_title(self, language: Language | None, title: str, save: bool = True) -> Self:
    if language == self:
      self.self_title = title
      if self.code != DLC: return self.save() if save else self
    return super().set_title(language, title, save)
  
  def remove_title(self, language: Language, save: bool = True):
    if language == self: raise ValueError('Cannot remove title for language itself')
    return super().remove_title(language, save)
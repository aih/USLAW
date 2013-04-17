import datetime
from haystack.indexes import *
from haystack import site
#from laws.models import Law

#class LawIndex(SearchIndex):
#    text = CharField(document=True, model_attr="index_text")
#    title = CharField(model_attr='title')
#    lawname = CharField(model_attr='name')
 
 #   def get_queryset(self):
 #       """Used when the entire index for model is updated."""
 #       return Law.objects.all()

#site.register(Law, LawIndex)


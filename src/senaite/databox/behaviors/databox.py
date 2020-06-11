# -*- coding: utf-8 -*-

from bika.lims import api
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from senaite.databox import _
from senaite.databox import logger
from senaite.databox.config import TMP_FOLDER_KEY
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IDataBoxBehavior(model.Schema):

    # N.B. do not name this field `portal_type`
    query_type = schema.Choice(
        title=_(u"Query Type"),
        description=_(u"The type to query"),
        source="senaite.databox.vocabularies.addable_types",
        required=False,
    )

    display_columns = schema.List(
        title=_(u"Display Columns"),
        description=_(u"Choose display columns"),
        default=["Title", "Description"],
        value_type=schema.Choice(
            vocabulary="senaite.databox.vocabularies.display_columns"),
        required=False,
    )

    limit = schema.Int(
        title=_(u"Limit"),
        description=_(u"Limit Search Results"),
        required=False,
        default=5,
        min=1,
    )

    sort_on = schema.TextLine(
        title=_(u"label_sort_on", default=u"Sort on"),
        description=_(u"Sort the databox on this index"),
        required=False,
    )


@implementer(IDataBoxBehavior)
@adapter(IDexterityContent)
class DataBox(object):

    def __init__(self, context):
        self.context = context
        logger.info("IDataBoxBehavior::__init__:context={}"
                    .format(repr(context)))

    def get_fields(self):
        """Returns all schema fields of the selected query type

        IMPORTANT: Do not call from within `__init__` due to permissions
        """
        obj = self._create_temporary_object()
        if obj is None:
            return []
        fields = api.get_fields(obj).keys()
        return fields

    def _create_temporary_object(self):
        """Create a temporary object to fetch the fields from

        This is needed to get schema extended fields as well.
        """
        portal_type = self.query_type
        if portal_type is None:
            return None
        portal_factory = api.get_tool("portal_factory")
        temp_folder = portal_factory._getTempFolder(TMP_FOLDER_KEY)
        if portal_type in temp_folder:
            return temp_folder[portal_type]
        temp_folder.invokeFactory(portal_type, id=portal_type)
        return temp_folder[portal_type]

    def get_query_catalog(self, default="portal_catalog"):
        """Returns the primary catalog for the selected query type
        """
        archetype_tool = api.get_tool("archetype_tool")
        portal_type = self.query_type
        catalogs = archetype_tool.getCatalogsByType(portal_type)
        if len(catalogs) == 0:
            return default
        primary_catalog = catalogs[0]
        return primary_catalog.getId()

    # Getters and setters for our fields.

    def _set_query_type(self, value):
        self.context.query_type = value

    def _get_query_type(self):
        return getattr(self.context, "query_type", None)

    query_type = property(_get_query_type, _set_query_type)

    def _set_display_columns(self, value):
        self.context.display_columns = value

    def _get_display_columns(self):
        return getattr(self.context, "display_columns", None)

    display_columns = property(_get_display_columns, _set_display_columns)

    def _set_limit(self, value):
        self.context.limit = value

    def _get_limit(self):
        return getattr(self.context, "limit", 1000)

    limit = property(_get_limit, _set_limit)

    def _set_sort_on(self, value):
        self.context.sort_on = value

    def _get_sort_on(self, default="created"):
        return getattr(self.context, "sort_on", default)

    sort_on = property(_get_sort_on, _set_sort_on)

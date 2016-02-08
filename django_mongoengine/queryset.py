from mongoengine import queryset as qs

class QueryWrapper(object):
    # XXX: copy funcs from django; now it's just wrapper
    select_related = False
    order_by = []

    def __init__(self, q):
        self.q = q

class QuerySet(qs.QuerySet):
    """
    A base queryset with django-required attributes
    """

    @property
    def model(self):
        return self._document

    @property
    def query(self):
        return QueryWrapper(self._query)

    def get_queryset(self):
        return self

    def latest(self, field_name):
        return self.order_by("-" + field_name).first()

    def earliest(self, field_name):
        return self.order_by(field_name).first()

    def exists(self):
        return bool(self)


    def _clone(self):
        return self.clone()

    @property
    def ordered(self):
        """
        Returns True if the QuerySet is ordered -- i.e. has an order_by()
        clause or a default ordering on the model.
        """
        if self._ordering:
            return True
        elif self._document._meta.ordering:
            return True
        else:
            return False


class QuerySetManager(qs.QuerySetManager):
    default = QuerySet

    def all(self):
        return self.get_queryset()

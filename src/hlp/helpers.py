# from sqlalchemy.ext.declarative import declared_attr
#
#
# class BaseMixin():
#
#     @declared_attr
#     def __tablename__(cls):
#         return cls.__name__.lower()
#
#     def clean(self, session):
#         """
#         clean table
#
#         Returns:
#
#         TODO: cleanup
#         """
#         session.execute('''TRUNCATE TABLE {}'''.format(self.__tablename__))
#     @classmethod
#     def populate(cls, data_list, session):
#         for entry in data_list:
#             session.add(cls(**entry))
#         session.commit()
#
#     def __repr__(self):
#         values = ', '.join("%s=%r" % (n, getattr(self, n)) for n in self.__table__.c.keys())
#         return "%s(%s)" % (self.__class__.__name__, values)
#
# class AssocBaseMixin():
#
#     @declared_attr
#     def __tablename__(cls):
#         return cls.__name__.lower()

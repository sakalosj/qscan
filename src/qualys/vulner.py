import logging
from sqlalchemy import Integer, Column, ForeignKey, String

from qualys.db import Base, BaseMixin

logger = logging.getLogger('qualys.vulner')


class Vulner(BaseMixin, Base):
    qid = Column(Integer, primary_key=True)
    patch_qid_fk = Column(Integer, ForeignKey('patch.qid'))
    severity = Column(Integer)
    title = Column(String(30))

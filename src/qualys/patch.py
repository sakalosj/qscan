import logging

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from qualys.db import Base, BaseMixin

logger = logging.getLogger('qualys.vulner')


class Patch(BaseMixin, Base):
    """
    Class is processing vulnerabilities and managing table qualys_vulner
    """
    qid = Column(Integer, primary_key=True)
    vulners = relationship('Vulner', backref='patch')
    severity = Column(Integer)
    title = Column(String(30))



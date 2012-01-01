"""Element of operating system. (Base class for all 'System' subelements)."""

from base import Base

class Element(Base):

    sys = None

    def __init__(self, system):
        super(Element, self).__init__(system.app)
        self.sys = system


# vim: set sts=4 sw=4 et :

import unittest
from bandwidth.catapult.bxml import BXMLResponse
from lxml.builder import E

class BXMLResponseTests(unittest.TestCase):
    def test_to_xml(self):
        """
        to_xml() should build XML
        """
        estimated_xml = b'<xml><Response><Hangup/></Response></xml>'
        xml = BXMLResponse(E.Hangup())
        self.assertEqual(estimated_xml, xml.to_xml())

    def test_to_xml_with_several_verbs(self):
        """
        to_xml() should build XML (some verbs)
        """
        estimated_xml = b'<xml><Response><Pause duration="10"/><Hangup/></Response></xml>'
        xml = BXMLResponse(E.Pause({'duration': '10'}), E.Hangup())
        self.assertEqual(estimated_xml, xml.to_xml())

    def test__str__(self):
        """
        __str__() should return XML as string
        """
        estimated_xml = '<xml><Response><Hangup/></Response></xml>'
        xml = BXMLResponse(E.Hangup())
        self.assertEqual(estimated_xml, str(xml))

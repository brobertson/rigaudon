import lxml
from lxml import etree
import StringIO
xhtml = etree.Element("{http://www.w3.org/1999/xhtml}html")
body = etree.SubElement(xhtml, "{http://www.w3.org/1999/xhtml}body")
root = etree.Element("root")
para = etree.SubElement(body, "{http://www.w3.org/1999/xhtml}p")
para2 = etree.SubElement(body, "{http://www.w3.org/1999/xhtml}p")
para2.text="two"
para2.set("class","foo")
para2.set("title","a b c d e")
print(etree.tostring(xhtml, pretty_print=True))
tree = etree.parse(StringIO.StringIO('''\
<?xml version="1.0"?>
<!DOCTYPE html
PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
 <html xmlns="http://www.w3.org/1999/xhtml">
 <head>
 <meta content="riguadon 0.3" name="ocr-system"/>
<meta name="ocr-nmber-of-pages" content="???"/>
<meta name="ocr-langs" content="grc lat"/>
  <meta content="ocr_line ocr_page" name="ocr-capabilities"/>
 <title>OCR Output</title>
 </head>
<body/>
 </html>
 '''))
root = tree.getroot()
body = root.find("{http://www.w3.org/1999/xhtml}body")
para = etree.SubElement(body, "{http://www.w3.org/1999/xhtml}p")
para2 = etree.SubElement(body, "{http://www.w3.org/1999/xhtml}p")
para2.text="two"
para2.set("class","foo")
para2.set("title","a b c d e")
print(etree.tostring(tree))

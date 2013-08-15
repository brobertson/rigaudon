<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:abbyy="http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml">
<xsl:output method="text" encoding="UTF-8"/>
<xsl:template match="html">
  <xsl:apply-templates select="//span[@class='ocr_line']"/>
</xsl:template>
<xsl:template match="span[@class='ocr_line']"><xsl:text disable-output-escaping="yes">
</xsl:text>
<xsl:apply-templates/>
</xsl:template>
<xsl:template match="span[@class='ocr_word']">
<xsl:value-of select="."/><xsl:text disable-output-escaping="yes"> </xsl:text>
</xsl:template>
</xsl:stylesheet>


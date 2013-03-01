<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text" omit-xml-declaration="yes" indent="no"/>
<xsl:template match="/">
  <xsl:apply-templates select="TEI.2/text/body"/>
</xsl:template>
<xsl:template match="body">
<xsl:apply-templates match="*[@lang != 'eng']"/>
</xsl:template>
<xsl:template match="*[@lang != 'eng']">
  <xsl:value-of select="text()"/>
  <xsl:apply-templates match="*[@lang != 'eng']"/>
</xsl:template>
</xsl:stylesheet>

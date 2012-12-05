<xsl:stylesheet  xmlns:abbyy="http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml" version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>
  <xsl:template match="abbyy:formatting">
     <xsl:apply-templates select="node()"/>
  </xsl:template>
</xsl:stylesheet>


<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!-- Makes a tab separated list table of metadata information for this archive.org meta.xml file -->
<xsl:output method="text"/>
<xsl:template match="/">
<xsl:apply-templates select="metadata/identifier"/><xsl:text>&#x9;</xsl:text><xsl:apply-templates select="metadata/creator"/><xsl:text>&#x9;</xsl:text><xsl:apply-templates select="metadata/title"/><xsl:text>&#x9;</xsl:text><xsl:apply-templates select="metadata/publisher"/><xsl:text>&#x9;</xsl:text><xsl:apply-templates select="metadata/date"/><xsl:text>&#x9;</xsl:text><xsl:apply-templates select="metadata/ppi"/><xsl:text>&#x9;</xsl:text><xsl:apply-templates select="metadata/publisher" mode="fontInspection"/><xsl:text>
</xsl:text>
</xsl:template>
<xsl:template match="metadata/creator">
 <xsl:apply-templates/>
 <xsl:if test="not(position() = last())"><xsl:text>; </xsl:text></xsl:if>
</xsl:template>

<xsl:template match="metadata/publisher" mode="fontInspection">
  <xsl:choose>
   <xsl:when test="contains(.,'Teubner')">
      <xsl:text>Teubner_serif</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Tevbner')">
      <xsl:text>Teubner_serif</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Tuebner')">
      <xsl:text>Teubner_serif</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Taubner')">
      <xsl:text>Teubner_serif</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Didot')">
      <xsl:text>Didot</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Oxon')">
      <xsl:text>Oxford</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Oxford')">
      <xsl:text>Oxford</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Weidm')">
      <xsl:text>Weidmann</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Reimer')">
      <xsl:text>Reimer</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Bipont')">
      <xsl:text>Biponti</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Cambridge')">
      <xsl:text>CUP</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Heinem')">
      <xsl:text>Heinemann</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Harv')">
      <xsl:text>HUP</xsl:text>
   </xsl:when>
   <xsl:when test="contains(.,'Macm')">
      <xsl:text>Macmillan</xsl:text>
   </xsl:when>
   <xsl:otherwise>
      <xsl:text>UNKNOWN</xsl:text>
   </xsl:otherwise>
  </xsl:choose>
  </xsl:template>
</xsl:stylesheet>

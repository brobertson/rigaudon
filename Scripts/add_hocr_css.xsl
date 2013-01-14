<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>
    <xsl:output method="xml" indent="yes"/>

    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="head">
       <xsl:copy>
                       <xsl:apply-templates select="@* | node()"/>
          <link rel="stylesheet" type="text/css" href="http://heml.mta.ca/Rigaudon/hocr.css"/>
          <meta http-equiv="content-type" content="application/xhtml+xml; charset=UTF-8" />
      </xsl:copy>
    </xsl:template>
</xsl:stylesheet>
